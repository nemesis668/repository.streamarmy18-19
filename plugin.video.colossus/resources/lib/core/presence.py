from __future__ import absolute_import

import json
import os
import threading
import uuid

import xbmc
import xbmcgui
import xbmcvfs

from resources.lib.core import paths


API_BASE = 'https://nemzzy.info'
PING_URL = API_BASE + '/colossus/ping'
INSTALL_URL = API_BASE + '/colossus/install'
INTERVAL_SECONDS = 120

_stop = threading.Event()
_thread = None
_generation = 0
_seen_generation = -1


def device_type():
    checks = (
        ('system.platform.android', 'Android'),
        ('system.platform.uwp', 'Windows'),
        ('system.platform.windows', 'Windows'),
        ('system.platform.tvos', 'tvOS'),
        ('system.platform.ios', 'iOS'),
        ('system.platform.osx', 'macOS'),
        ('system.platform.darwin', 'macOS'),
        ('system.platform.webos', 'webOS'),
        ('system.platform.linux.raspberrypi', 'Raspberry Pi'),
        ('system.platform.linux', 'Linux'),
    )
    for condition, name in checks:
        try:
            if xbmc.getCondVisibility(condition):
                return name
        except Exception:
            continue
    return 'Kodi'


def _id_path():
    folder = paths.PROFILE_PATH
    try:
        if not xbmcvfs.exists(folder):
            xbmcvfs.mkdirs(folder)
    except Exception:
        try:
            os.makedirs(folder)
        except Exception:
            pass
    return os.path.join(folder, 'presence_id')


def user_id():
    path = _id_path()
    try:
        with open(path, 'r') as handle:
            stored = handle.read().strip()
        if stored:
            return stored
    except Exception:
        pass
    stored = uuid.uuid4().hex
    try:
        with open(path, 'w') as handle:
            handle.write(stored)
    except Exception:
        pass
    return stored


def _on_kodi_screen(generation):
                                                                                          
    global _seen_generation
    if generation != _generation:
        return True
    try:
        current = xbmcgui.getCurrentWindowId()
    except Exception:
        return False
    if current >= 13000:
        _seen_generation = generation
        return False
    return _seen_generation == generation


def _install_flag_path():
    return os.path.join(paths.PROFILE_PATH, 'install_registered')


def _register_install():
    flag = _install_flag_path()
    try:
        if os.path.exists(flag):
            return
    except Exception:
        pass
    import requests
    response = requests.post(
        INSTALL_URL,
        data=json.dumps({
            'user_id': user_id(),
            'device_type': device_type(),
        }),
        headers={'Content-Type': 'application/json'},
        timeout=8,
    )
    if response.status_code != 200:
        xbmc.log(
            '[Colossus] Install registration HTTP %s' % response.status_code,
            xbmc.LOGINFO
        )
        return
    try:
        folder = os.path.dirname(flag)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
        with open(flag, 'w') as handle:
            handle.write('1')
    except Exception:
        pass


def _send():
    if _stop.is_set():
        return
    import requests
    response = requests.post(
        PING_URL,
        data=json.dumps({
            'user_id': user_id(),
            'device_type': device_type(),
        }),
        headers={'Content-Type': 'application/json'},
        timeout=8,
    )
    if response.status_code != 200:
        xbmc.log(
            '[Colossus] Presence heartbeat HTTP %s' % response.status_code,
            xbmc.LOGINFO
        )


def _loop(generation):
    if generation == _generation and not _stop.is_set():
        try:
            _register_install()
        except Exception as exc:
            xbmc.log('[Colossus] Install registration failed: %s' % exc, xbmc.LOGINFO)
    while generation == _generation and not _stop.is_set():
        if _on_kodi_screen(generation):
            return
        try:
            _send()
        except Exception as exc:
            xbmc.log('[Colossus] Presence heartbeat failed: %s' % exc, xbmc.LOGINFO)
        waited = 0
        while waited < INTERVAL_SECONDS:
            if generation != _generation or _stop.is_set() or _on_kodi_screen(generation):
                return
            step = min(5, INTERVAL_SECONDS - waited)
            if _stop.wait(step):
                return
            waited += step


def start():
    global _thread, _generation
    previous = _thread
    _generation += 1
    generation = _generation
    _stop.set()
    if previous is not None and previous.is_alive() and previous is not threading.current_thread():
        previous.join(timeout=2)
    _stop.clear()
    thread = threading.Thread(target=_loop, args=(generation,), name='colossus-presence')
    thread.daemon = True
    _thread = thread
    thread.start()


def stop():
    global _generation, _thread
    _generation += 1
    _stop.set()
    thread = _thread
    _thread = None
    if thread is not None and thread.is_alive() and thread is not threading.current_thread():
        thread.join(timeout=2)
