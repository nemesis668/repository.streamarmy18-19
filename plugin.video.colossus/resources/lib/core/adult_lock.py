from __future__ import absolute_import

import hashlib
import os
import time

import xbmc
import xbmcgui

from resources.lib.core import paths


HASH_SETTING = 'adult_password_hash'
RESET_AT_SETTING = 'adult_password_reset_at'
RESET_LABEL_SETTING = 'adult_password_reset'
ARMED_SETTING = 'adult_lock_armed'
MIN_LENGTH = 4

_settings_from_addon = False
_guard = None


def protection_enabled():
    return paths.ADDON.getSetting('protect_adult') == 'true'


def has_password():
    return bool((paths.ADDON.getSetting(HASH_SETTING) or '').strip())


def sync_reset_label():
    stored = (paths.ADDON.getSetting(RESET_AT_SETTING) or '').strip() or 'Never'
    if paths.ADDON.getSetting(RESET_LABEL_SETTING) != stored:
        paths.ADDON.setSetting(RESET_LABEL_SETTING, stored)


def arm():
    paths.ADDON.setSetting(ARMED_SETTING, 'true')


def start_guard():
    global _guard
    restore_if_bypassed()
    if _guard is None:
        _guard = _SettingsGuard()


def mark_settings_session(active):
    global _settings_from_addon
    _settings_from_addon = bool(active)


def confirm_disable(was_on):
    if not was_on or protection_enabled() or not has_password():
        return
    if paths.ADDON.getSetting(ARMED_SETTING) == 'false':
        return
    if not _claim_off():
        return
    try:
        if protection_enabled() or paths.ADDON.getSetting(ARMED_SETTING) == 'false':
            return
        entered = _ask('Adult password to turn protection off')
        if entered and _hash(entered) == paths.ADDON.getSetting(HASH_SETTING):
            paths.ADDON.setSetting(HASH_SETTING, '')
            paths.ADDON.setSetting(ARMED_SETTING, 'false')
            paths.ADDON.setSetting('protect_adult', 'false')
            return
        paths.ADDON.setSetting('protect_adult', 'true')
        if entered:
            xbmcgui.Dialog().ok(
                paths.ADDON_NAME,
                'Wrong password. Password protection stays on.'
            )
        else:
            xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Password protection stays on.')
    finally:
        _release_off()


def restore_if_bypassed():
    if not has_password() or paths.ADDON.getSetting(ARMED_SETTING) == 'false':
        return
    if paths.ADDON.getSetting(ARMED_SETTING) != 'true':
        paths.ADDON.setSetting(ARMED_SETTING, 'true')
    if protection_enabled():
        return
    paths.ADDON.setSetting('protect_adult', 'true')
    xbmcgui.Dialog().ok(
        paths.ADDON_NAME,
        'Password protection was turned off without the password, so it has been turned back on.'
    )


class _SettingsGuard(xbmc.Monitor):
    def onSettingsChanged(self):
        if _settings_from_addon:
            return
        confirm_disable(True)


def prompt_in_progress():
    try:
        return os.path.exists(_prompt_flag())
    except Exception:
        return False


def unlock():
    if not protection_enabled():
        return True
    if not has_password():
        xbmcgui.Dialog().ok(
            paths.ADDON_NAME,
            'Password protect adult is on, but no password is set.\n'
            'Set one in Settings.'
        )
        return False
    entered = _ask('Adult password')
    if not entered:
        return False
    if _hash(entered) != paths.ADDON.getSetting(HASH_SETTING):
        xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Wrong password.')
        return False
    return True


def create_password():
    return _run_exclusive(lambda: _choose_new_password(require_current=False))


def set_password():
    return _run_exclusive(lambda: _choose_new_password(require_current=has_password()))


def reset_password():
    if not has_password():
        xbmcgui.Dialog().ok(
            paths.ADDON_NAME,
            'No adult password is set yet.\n'
            'Use Set adult password.'
        )
        return False
    return _run_exclusive(_reset_password)


def _reset_password():
    confirmed = xbmcgui.Dialog().yesno(
        paths.ADDON_NAME,
        'Reset the adult password without the current one?\n'
        'The time of this reset is shown in Settings.',
        nolabel='Cancel',
        yeslabel='Reset'
    )
    if not confirmed:
        return False
    if not _choose_new_password(require_current=False, announce=False):
        return False
    stamp = time.strftime('%d %b %Y, %H:%M')
    paths.ADDON.setSetting(RESET_AT_SETTING, stamp)
    paths.ADDON.setSetting(RESET_LABEL_SETTING, stamp)
    xbmcgui.Dialog().ok(
        paths.ADDON_NAME,
        'Adult password reset.\n'
        'Settings will show: %s' % stamp
    )
    return True


def _choose_new_password(require_current, announce=True):
    if require_current:
        current = _ask('Current adult password')
        if not current:
            return False
        if _hash(current) != paths.ADDON.getSetting(HASH_SETTING):
            xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Wrong password.')
            return False
    first = _ask('New adult password')
    if not first:
        return False
    if len(first) < MIN_LENGTH:
        xbmcgui.Dialog().ok(
            paths.ADDON_NAME,
            'Use at least %s characters.' % MIN_LENGTH
        )
        return False
    second = _ask('Repeat the new adult password')
    if first != second:
        xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Those passwords did not match.')
        return False
    paths.ADDON.setSetting(HASH_SETTING, _hash(first))
    paths.ADDON.setSetting('protect_adult', 'true')
    paths.ADDON.setSetting(ARMED_SETTING, 'true')
    if announce:
        xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Adult password saved.')
    return True


def _prompt_flag():
    return os.path.join(paths.PROFILE_PATH, 'adult_password_prompt')


def _run_exclusive(func):
    if not _claim_prompt():
        _wait_for_prompt()
        return has_password()
    try:
        return bool(func())
    finally:
        _release_prompt()


def _claim_prompt():
    folder = os.path.dirname(_prompt_flag())
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    try:
        handle = os.open(_prompt_flag(), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except OSError:
        return False
    os.close(handle)
    return True


def _wait_for_prompt():
    for _ in range(150):
        if not prompt_in_progress():
            return
        xbmc.sleep(200)


def _release_prompt():
    try:
        os.remove(_prompt_flag())
    except Exception:
        pass


def _off_flag():
    return os.path.join(paths.PROFILE_PATH, 'adult_off_check')


def _claim_off():
    folder = os.path.dirname(_off_flag())
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    try:
        handle = os.open(_off_flag(), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except OSError:
        return False
    os.close(handle)
    return True


def _release_off():
    try:
        os.remove(_off_flag())
    except Exception:
        pass


def _ask(heading):
    kind = getattr(xbmcgui, 'INPUT_PASSWORD', 5)
    option = getattr(xbmcgui, 'PASSWORD_VERIFY', 1)
    entered = xbmcgui.Dialog().input(heading, '', type=kind, option=option)
    return (entered or '').strip()


def _hash(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
