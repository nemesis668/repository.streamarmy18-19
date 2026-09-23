from __future__ import absolute_import

import json
import os
import time

import xbmcvfs

from resources.lib.core import paths


API_BASE = 'https://nemzzy.info'
ACCESS_URL = API_BASE + '/colossus/access'
PIN_API = 'https://pinsystem.co.uk/service.php'
PIN_PLUGIN = 'RnVja1lvdSE'
CODE_URL = 'https://pinsystem.co.uk/'


def _code_path():
    folder = paths.PROFILE_PATH
    try:
        if not xbmcvfs.exists(folder):
            xbmcvfs.mkdirs(folder)
    except Exception:
        try:
            os.makedirs(folder)
        except Exception:
            pass
    return os.path.join(folder, 'access_code.json')


def load_pin():
    try:
        with open(_code_path(), 'r') as handle:
            payload = json.loads(handle.read() or '{}')
    except Exception:
        return '', 0
    pin = str(payload.get('pin') or '').strip().upper()
    try:
        expires = int(payload.get('expires') or 0)
    except (TypeError, ValueError):
        expires = 0
    if not pin:
        return '', 0
    return pin, expires


def save_pin(pin, expires):
    pin = str(pin or '').strip().upper()
    if not pin:
        return
    try:
        expires = int(expires or 0)
    except (TypeError, ValueError):
        expires = 0
    if expires <= 0:
        expires = int(time.time()) + 4 * 3600
    try:
        with open(_code_path(), 'w') as handle:
            handle.write(json.dumps({'pin': pin, 'expires': expires}))
    except Exception:
        pass


def clear_pin():
    path = _code_path()
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def _get(url):
    import requests
    response = requests.get(url, timeout=12)
    if response.status_code != 200:
        return None
    try:
        return response.json()
    except Exception:
        return None


def fetch_policy():
                                                                                             
    try:
        payload = _get(ACCESS_URL)
    except Exception:
        return None
    if not isinstance(payload, dict) or 'required' not in payload:
        return None
    code_url = str(payload.get('code_url') or CODE_URL).strip() or CODE_URL
    return {
        'required': bool(payload.get('required')),
        'code_url': code_url,
    }


def pass_still_valid():
    from resources.lib.core import remote
    return remote.token_valid()


def obtain_pass(pin=''):
                                                                                  
    from resources.lib.core import presence
    from resources.lib.core import remote
    try:
        import requests
        response = requests.post(
            API_BASE + '/colossus/pass',
            json={
                'device_id': presence.user_id(),
                'pin': str(pin or '').strip().upper(),
            },
            timeout=20,
        )
        payload = response.json()
    except Exception:
        return 'unreachable', 0
    if not isinstance(payload, dict):
        return 'unreachable', 0
    token = payload.get('token') or ''
    if token:
        remote.save_pass(token, payload.get('engine') or '', payload.get('exp') or 0)
        try:
            expires = int(payload.get('expires') or 0)
        except (TypeError, ValueError):
            expires = 0
        return 'valid', expires
    return str(payload.get('status') or 'invalid'), 0


def check_pin(pin):
                                                                                     
    pin = str(pin or '').strip().upper()
    if not pin:
        return 'invalid', 0
    try:
        import requests
        url = '%s?code=%s&plugin=%s&format=json' % (
            PIN_API,
            requests.utils.quote(pin),
            PIN_PLUGIN,
        )
        payload = _get(url)
    except Exception:
        return 'unreachable', 0
    if not isinstance(payload, dict):
        return 'unreachable', 0
    status = str(payload.get('status') or '').strip().lower()
    if status == 'ok':
        try:
            expires = int(payload.get('expires') or 0)
        except (TypeError, ValueError):
            expires = 0
        if expires <= 0:
            expires = int(time.time()) + 4 * 3600
        return 'valid', expires
    message = str(payload.get('message') or '').lower()
    if 'expired' in message:
        return 'expired', 0
    return 'invalid', 0
