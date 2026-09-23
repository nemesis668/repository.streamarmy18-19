from __future__ import absolute_import

import json
import threading
import time

import requests


FLARE_URL = 'http://217.154.17.37:8191/v1'
_LOCK = threading.Lock()
_SESSION = {'id': None}

_MARKERS = (
    'just a moment',
    'cf-browser-verification',
    'attention required',
    'cf-challenge',
    'challenge-platform',
    'enable javascript and cookies',
    'checking your browser',
    'cf-mitigated',
)


class FlareError(Exception):
    pass


class Page(object):
    def __init__(self, text, url, status_code=200):
        self.text = text or ''
        self.url = url
        self.status_code = int(status_code or 200)
        self.headers = {}
        self.encoding = 'utf-8'
        self.content = self.text.encode('utf-8', 'replace')

    def json(self):
        return json.loads(self.text)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError('HTTP %s' % self.status_code)


def _log(message):
    try:
        import xbmc
        xbmc.log('[Colossus] %s' % message, xbmc.LOGINFO)
    except Exception:
        pass


def _sample(body):
    if body is None:
        return ''
    if isinstance(body, bytes):
        body = body[:5000].decode('utf-8', 'ignore')
    else:
        body = str(body)[:5000]
    return body.lower()


def body_is_challenge(status, body, headers=None):
    headers = headers or {}
    mitigated = ''
    server = ''
    for key, value in headers.items():
        name = str(key).lower()
        if name == 'cf-mitigated':
            mitigated = str(value).lower()
        elif name == 'server':
            server = str(value).lower()
    if mitigated:
        return True
    sample = _sample(body)
    if any(marker in sample for marker in _MARKERS):
        return True
    if int(status or 0) in (403, 503) and 'cloudflare' in server:
        return True
    if int(status or 0) in (403, 503) and 'cloudflare' in sample and 'ray id' in sample:
        return True
    return False


def is_challenge(response):
    if response is None:
        return False
    try:
        headers = response.headers or {}
    except Exception:
        headers = {}
    content_type = ''
    try:
        content_type = str(headers.get('Content-Type') or headers.get('content-type') or '').lower()
    except Exception:
        content_type = ''
    if content_type.startswith('image/') or content_type.startswith('video/') or 'mpegurl' in content_type:
        return False
    try:
        body = response.text
    except Exception:
        body = ''
    try:
        status = response.status_code
    except Exception:
        status = 0
    return body_is_challenge(status, body, headers)


def _post(payload, timeout):
    response = requests.post(
        FLARE_URL,
        data=json.dumps(payload),
        headers={'Content-Type': 'application/json'},
        timeout=timeout + 15,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise FlareError('FlareSolverr returned an unexpected response.')
    return data


def _drop_session():
    _SESSION['id'] = None


def _ensure_session(timeout):
    if _SESSION['id']:
        return _SESSION['id']
    try:
        data = _post({'cmd': 'sessions.create'}, timeout)
    except requests.ConnectionError as exc:
        _log('FlareSolverr session was not created: %s' % exc)
        raise
    except Exception as exc:
        _log('FlareSolverr session was not created: %s' % exc)
        return None
    if data.get('status') != 'ok':
        return None
    session_id = data.get('session')
    if session_id:
        _SESSION['id'] = session_id
    return session_id


def _notify_wait():
    now = time.time()
    if now - _SESSION.get('notified', 0) < 8:
        return
    _SESSION['notified'] = now
    try:
        import xbmcgui
        from resources.lib.core import paths
        xbmcgui.Dialog().notification(
            paths.ADDON_NAME,
            'Detected Cloudflare. Bypassing with FlareSolverr, please wait.',
            paths.ICON_PATH,
            8000
        )
    except Exception:
        pass


def solve(url, timeout=60):
    _notify_wait()
    with _LOCK:
        session_id = _ensure_session(timeout)
        payload = {
            'cmd': 'request.get',
            'url': url,
            'maxTimeout': int(timeout * 1000),
        }
        if session_id:
            payload['session'] = session_id
        try:
            data = _post(payload, timeout)
        except Exception:
            if not session_id:
                raise
            _drop_session()
            payload.pop('session', None)
            data = _post(payload, timeout)
        if data.get('status') != 'ok':
            if session_id:
                _drop_session()
            message = data.get('message') or 'FlareSolverr could not open that page.'
            raise FlareError(message)
        solution = data.get('solution') or {}
        text = solution.get('response') or ''
        final_url = solution.get('url') or url
        status = solution.get('status') or 200
        if not str(text).strip() or body_is_challenge(status, text):
            raise FlareError('Cloudflare challenge was not solved.')
        _log('FlareSolverr opened %s' % url.split('?')[0])
        return Page(text, final_url, status)
