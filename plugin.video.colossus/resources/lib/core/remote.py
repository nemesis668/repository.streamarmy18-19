                                                                                        

from __future__ import absolute_import

import base64
import json
import os
import time

from resources.lib.core import paths


ENGINE_FALLBACK = 'http://31.70.139.36:8787'
MAX_BODY = 8 * 1024 * 1024


class RemoteError(Exception):
    def __init__(self, message, exc='RemoteError'):
        super(RemoteError, self).__init__(message)
        self.exc = exc or 'RemoteError'


def _pass_path():
    return os.path.join(paths.PROFILE_PATH, 'engine_pass.json')


def save_pass(token, engine, exp):
    try:
        exp = int(exp or 0)
    except (TypeError, ValueError):
        exp = 0
    payload = {
        'token': token or '',
        'engine': (engine or ENGINE_FALLBACK).rstrip('/'),
        'exp': exp,
    }
    try:
        with open(_pass_path(), 'w') as handle:
            handle.write(json.dumps(payload))
    except Exception:
        pass


def _load():
    try:
        with open(_pass_path(), 'r') as handle:
            payload = json.loads(handle.read() or '{}')
    except Exception:
        payload = {}
    token = str(payload.get('token') or '')
    engine = str(payload.get('engine') or ENGINE_FALLBACK).rstrip('/')
    try:
        exp = int(payload.get('exp') or 0)
    except (TypeError, ValueError):
        exp = 0
    return token, engine, exp


def token_valid():
    token, _engine, exp = _load()
    return bool(token) and exp > int(time.time()) + 30


def _refresh():
    from resources.lib.core import access
    pin, _expires = access.load_pin()
    status, _expires = access.obtain_pass(pin or '')
    return status == 'valid' and token_valid()


def _pairs(response):
    pairs = []
    cookies = []
    raw_headers = getattr(getattr(response, 'raw', None), 'headers', None)
    items = None
    if raw_headers is not None and hasattr(raw_headers, 'items'):
        try:
            items = list(raw_headers.items())
        except Exception:
            items = None
    if items is None:
        try:
            items = list(response.headers.items())
        except Exception:
            items = []
    for key, value in items:
        if str(key).lower() == 'set-cookie':
            cookies.append(str(value))
            continue
        pairs.append([str(key), str(value)])
    return pairs, cookies


def _fetch(spec):
    import requests
    url = spec.get('url') or ''
    if not url:
        return {'error': 'Missing page address.'}
    body = b''
    encoded = spec.get('body_b64') or ''
    if encoded:
        try:
            body = base64.b64decode(encoded)
        except Exception:
            return {'error': 'Bad request body.'}
    timeout = spec.get('timeout') or 25
    try:
        timeout = int(timeout)
    except (TypeError, ValueError):
        timeout = 25
    headers = {}
    for key, value in spec.get('headers') or []:
        headers[str(key)] = str(value)
    try:
        response = requests.request(
            spec.get('method') or 'GET',
            url,
            headers=headers,
            data=body or None,
            timeout=timeout + 5,
            allow_redirects=True,
            verify=False,
        )
    except Exception as exc:
        return {'error': str(exc) or 'Could not download that page.'}
    content = response.content or b''
    if len(content) > MAX_BODY:
        return {
            'status': response.status_code,
            'url': response.url,
            'error': 'Page was too large.',
        }
    pairs, cookies = _pairs(response)
    return {
        'status': response.status_code,
        'url': response.url,
        'reason': response.reason or '',
        'headers': pairs,
        'set_cookies': cookies,
        'body_b64': base64.b64encode(content).decode('ascii'),
        'error': '',
    }


def _resolve_on_device(spec):
    action = spec.get('action') or 'resolve'
    url = spec.get('url') or ''
    text = ''
    try:
        import resolveurl
        hosted = resolveurl.HostedMediaFile(url)
        if action == 'valid_url':
            text = '1' if hosted.valid_url() else '0'
        else:
            try:
                text = hosted.resolve() or ''
            except Exception:
                text = ''
            if not text:
                try:
                    text = resolveurl.resolve(url) or ''
                except Exception:
                    text = ''
    except Exception as exc:
        return {'error': str(exc) or 'Could not resolve that link.'}
    if text is False or text is None:
        text = ''
    return {
        'status': 200,
        'url': url,
        'reason': '',
        'headers': [],
        'set_cookies': [],
        'body_b64': base64.b64encode(str(text).encode('utf-8')).decode('ascii'),
        'error': '',
    }


def _post(engine, path, payload, timeout):
    import requests
    response = requests.post(
        engine.rstrip('/') + path,
        json=payload,
        timeout=timeout,
    )
    try:
        data = response.json()
    except Exception:
        data = {'state': 'error', 'error': 'Bad engine response.', 'exc': 'RemoteError'}
    return response.status_code, data


def call(module, name, args=None, kwargs=None, on_progress=None):
    args = list(args or [])
    kwargs = dict(kwargs or {})
    refreshed = False
    while True:
        token, engine, exp = _load()
        if not token or exp <= int(time.time()) + 30:
            if refreshed or not _refresh():
                raise RemoteError('Could not reach Colossus. Try again in a moment.')
            refreshed = True
            token, engine, exp = _load()
        status, data = _post(engine, '/v1/call', {
            'token': token,
            'module': module,
            'fn': name,
            'args': args,
            'kwargs': kwargs,
        }, 190)
        if status == 401 and not refreshed:
            refreshed = True
            if _refresh():
                continue
            raise RemoteError('Could not reach Colossus. Try again in a moment.')
        while isinstance(data, dict) and data.get('state') == 'fetch':
            spec = data.get('fetch') or {}
            cancelled = False
            if spec.get('kind') == 'progress':
                if on_progress:
                    try:
                        cancelled = bool(on_progress(spec.get('percent') or 0, spec.get('text') or ''))
                    except Exception:
                        cancelled = False
                fetched = {'status': 200, 'error': '', 'cancelled': cancelled}
            elif spec.get('kind') == 'resolve':
                fetched = _resolve_on_device(spec)
            else:
                fetched = _fetch(spec)
            status, data = _post(engine, '/v1/resume', {
                'token': token,
                'job': data.get('job') or '',
                'status': fetched.get('status') or 0,
                'url': fetched.get('url') or '',
                'reason': fetched.get('reason') or '',
                'headers': fetched.get('headers') or [],
                'set_cookies': fetched.get('set_cookies') or [],
                'body_b64': fetched.get('body_b64') or '',
                'error': fetched.get('error') or '',
                'cancelled': bool(fetched.get('cancelled')),
            }, 190)
            if status == 401:
                raise RemoteError('Could not reach Colossus. Try again in a moment.')
        break
    if not isinstance(data, dict):
        raise RemoteError('Bad engine response.')
    if data.get('state') == 'ok':
        return data.get('result')
    raise RemoteError(data.get('error') or 'Request failed.', data.get('exc') or 'RemoteError')
