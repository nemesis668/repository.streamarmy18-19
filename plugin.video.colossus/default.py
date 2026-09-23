from __future__ import absolute_import

import sys
from urllib.parse import parse_qs

import xbmcplugin


def _action():
    raw = sys.argv[2] if len(sys.argv) > 2 else ''
    if raw.startswith('?'):
        raw = raw[1:]
    return (parse_qs(raw).get('action') or [''])[0]


def _finish_plugin():
    try:
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False, cacheToDisc=False)
    except Exception:
        pass


if __name__ == '__main__':
    action = _action()
    if action in ('set_adult_password', 'reset_adult_password'):
        from resources.lib.core import adult_lock
        try:
            if action == 'set_adult_password':
                adult_lock.set_password()
            else:
                adult_lock.reset_password()
        finally:
            _finish_plugin()
    else:
        from resources.lib.gui.home import run
        run()
