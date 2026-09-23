from __future__ import absolute_import

import threading
import time

import pyxbmct
import xbmc
import xbmcgui

from resources.lib.core import access
from resources.lib.core import paths
from resources.lib.gui.details import ColossusFullWindow


def _pin_text(value):
    return str(value or '').strip().upper()


class AccessWindow(ColossusFullWindow):
    def __init__(self, code_url, notice=''):
        super(AccessWindow, self).__init__('')
        self.allowed = False
        self.code_url = code_url or 'https://pinsystem.co.uk/'
        self.notice = notice or ''
        self.setup_canvas()
        self.set_controls()
        self.set_navigation()
        self.setFocus(self.pin_edit)

    def _centered_label(self, text, row, height=5, font='font13', text_color='0xFFE8EEF4'):
        label = pyxbmct.Label(
            text,
            font=font,
            textColor=text_color,
            alignment=pyxbmct.ALIGN_CENTER
        )
        self.placeControl(label, row, 10, height, 80, pad_x=0, pad_y=0)
        return label

    def set_controls(self):
        self.add_fanart(paths.BACKDROP_PATH or paths.FANART_PATH)

        self.icon = pyxbmct.Image(paths.ICON_PATH, aspectRatio=2)
        self.placeControl(self.icon, 12, 45, 16, 10, pad_x=0, pad_y=0)

        self.title_label = self._centered_label(
            '[B]ACCESS CODE[/B]',
            29,
            height=7,
            font='font30',
            text_color='0xFFFFFFFF'
        )
        self._centered_label(
            '[B]Colossus stays locked until this PIN is accepted.[/B]',
            37,
            text_color='0xFF7EE0FF'
        )
        self._centered_label(
            'Head to [COLOR gold][B]%s[/B][/COLOR]' % self.code_url,
            43
        )
        self._centered_label(
            'Choose [COLOR aqua][B]Kodi Addons[/B][/COLOR] and generate a PIN.',
            48
        )
        self._centered_label(
            'A demo video on the site shows you how.',
            53,
            text_color='0xFFB7C3CE'
        )
        self._centered_label(
            '[COLOR aqua][B]Enter Pin[/B][/COLOR]',
            59
        )

        self.pin_edit = pyxbmct.Edit('', font='font13', textColor='0xFFFFFFFF')
        self.placeControl(self.pin_edit, 65, 30, 8, 40, pad_x=0, pad_y=0)

        self.status_label = self._centered_label(
            self.notice,
            74,
            height=6,
            text_color='0xFFF2C14E'
        )

        self.continue_button = pyxbmct.Button('Check PIN')
        self.placeControl(self.continue_button, 82, 32, 8, 16, pad_x=0, pad_y=0)
        self.connect(self.continue_button, self.submit)

        self.quit_button = pyxbmct.Button('Quit')
        self.placeControl(self.quit_button, 82, 52, 8, 16, pad_x=0, pad_y=0)
        self.connect(self.quit_button, self.quit_addon)

    def set_navigation(self):
        self.pin_edit.controlDown(self.continue_button)
        self.continue_button.controlUp(self.pin_edit)
        self.continue_button.controlRight(self.quit_button)
        self.quit_button.controlUp(self.pin_edit)
        self.quit_button.controlLeft(self.continue_button)

    def quit_addon(self):
        self.allowed = False
        self.close()

    def submit(self):
        if getattr(self, '_checking', False):
            return
        pin = _pin_text(self.pin_edit.getText())
        if not pin:
            self.status_label.setLabel('Enter the PIN from Pinsystem.')
            return
        self._checking = True
        self.status_label.setLabel('Checking PIN...')
        xbmc.sleep(50)
        status, expires = _wait(lambda: access.obtain_pass(pin)) or ('unreachable', 0)
        self._checking = False
        if status == 'valid':
            access.save_pin(pin, expires)
            self.allowed = True
            self.close()
            return
        if status == 'expired':
            self.status_label.setLabel('That PIN has expired. Generate a new one at Pinsystem and try again.')
        elif status == 'unreachable':
            self.status_label.setLabel('Could not reach Pinsystem. Try again, or quit.')
        else:
            self.status_label.setLabel('That PIN is not valid. Try again, or quit.')


def _wait(work):
    holder = {'result': None, 'done': False}

    def worker():
        try:
            holder['result'] = work()
        finally:
            holder['done'] = True

    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    while not holder['done']:
        xbmc.sleep(100)
    return holder['result']


def _dismiss_busy():
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    xbmc.executebuiltin('Dialog.Close(busydialognocancel)')


class StartupCover(ColossusFullWindow):
    def __init__(self):
        super(StartupCover, self).__init__('')
        self.setup_canvas()
        self.add_fanart(paths.BACKDROP_PATH or paths.FANART_PATH)
        self.icon = pyxbmct.Image(paths.ICON_PATH, aspectRatio=2)
        self.placeControl(self.icon, 42, 45, 16, 10, pad_x=0, pad_y=0)

    def present(self):
        xbmcgui.Window.show(self)
        xbmc.sleep(50)
        _dismiss_busy()


def allow_entry():
    code_url = 'https://pinsystem.co.uk/'
    notice = ''
    while True:
        policy = _wait(access.fetch_policy)
        if policy is None:
            if access.pass_still_valid():
                return True
            retry = xbmcgui.Dialog().yesno(
                paths.ADDON_NAME,
                'Could not reach the access check.',
                nolabel='Quit',
                yeslabel='Retry'
            )
            if not retry:
                return False
            continue
        code_url = policy.get('code_url') or code_url
        saved, expires = access.load_pin()
        if not policy.get('required'):
            status, _new_expires = _wait(lambda: access.obtain_pass('')) or ('unreachable', 0)
            if status == 'valid' or access.pass_still_valid():
                return True
            retry = xbmcgui.Dialog().yesno(
                paths.ADDON_NAME,
                'Could not reach the access check.',
                nolabel='Quit',
                yeslabel='Retry'
            )
            if not retry:
                return False
            continue
        if saved:
            status, new_expires = _wait(lambda: access.obtain_pass(saved)) or ('unreachable', 0)
            if status == 'valid':
                access.save_pin(saved, new_expires or expires)
                return True
            if status == 'unreachable' and access.pass_still_valid():
                return True
            access.clear_pin()
            if status == 'expired':
                notice = 'Your saved PIN has expired. Generate a new one at Pinsystem.'
            elif status == 'unreachable':
                notice = 'Could not reach Pinsystem. Enter the PIN again, or quit.'
            else:
                notice = 'The saved PIN is no longer valid. Enter a new one.'
        else:
            notice = ''
        break

    window = AccessWindow(code_url, notice)
    xbmcgui.Window.show(window)
    xbmc.sleep(50)
    window.doModal()
    allowed = window.allowed
    del window
    return allowed
