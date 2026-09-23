from __future__ import absolute_import

import pyxbmct
import xbmcgui

from resources.lib.core import paths


SECTION_DESCRIPTIONS = {
    'Sports': 'Live sports, replays, and event links will be migrated here.',
    'Movies & Shows': 'Movie and TV browsing will be migrated here.',
    'XXX': 'Adult provider menus and scraper-backed browsing will be migrated here.',
    'Music': 'Music content and streams will be migrated here.',
    'Cartoons & Anime': 'Cartoon and anime content will be migrated here.',
    'Community Lists': 'Community curated lists and shared collections will be migrated here.',
}


class SectionWindow(pyxbmct.BlankDialogWindow):
    def __init__(self, section_name):
        super(SectionWindow, self).__init__()
        self.section_name = section_name
        self.setGeometry(900, 560, 100, 100)
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
        self.set_controls()
        self.set_navigation()
        self.setFocus(self.back_button)

    def set_controls(self):
        title = '[B]%s[/B]' % self.section_name
        description = SECTION_DESCRIPTIONS.get(
            self.section_name,
            'This section is ready for content migration.'
        )

        self.title_label = pyxbmct.Label(title, alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.title_label, 8, 10, 10, 80)

        self.description_box = pyxbmct.TextBox()
        self.placeControl(self.description_box, 22, 12, 28, 76)
        self.description_box.setText(
            '[COLOR aqua]%s[/COLOR]\n\n'
            'This is a fresh Colossus section, not a link into any old addon.\n'
            'Provider menus and playback will be added here in the next migration phases.'
            % description
        )

        self.placeholder_list = pyxbmct.List()
        self.placeControl(self.placeholder_list, 54, 18, 24, 64)
        self.placeholder_list.addItem('Ready for migration')
        self.placeholder_list.addItem('No old addon links are used')
        self.placeholder_list.addItem('Press Back or Close to return home')

        self.back_button = pyxbmct.Button('Close')
        self.placeControl(self.back_button, 84, 35, 8, 30)

        self.connect(self.back_button, self.close)
        self.connect(self.placeholder_list, self.show_placeholder_notice)

    def set_navigation(self):
        self.placeholder_list.controlDown(self.back_button)
        self.placeholder_list.controlUp(self.back_button)
        self.back_button.controlUp(self.placeholder_list)
        self.back_button.controlDown(self.placeholder_list)

    def show_placeholder_notice(self):
        xbmcgui.Dialog().notification(
            paths.ADDON_NAME,
            '%s is ready for content migration.' % self.section_name,
            paths.ICON_PATH,
            2500
        )


def open_section(section_name):
    if section_name == 'Sports':
        try:
            from resources.lib.gui.sports import open_sports
            open_sports()
        except Exception as exc:
            xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Sports failed to open.\n%s' % exc)
        return

    if section_name == 'Music':
        try:
            from resources.lib.gui.music import open_music
            open_music()
        except Exception as exc:
            xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Music failed to open.\n%s' % exc)
        return

    if section_name == 'Movies & Shows':
        from resources.lib.gui.movies import open_movies_window
        open_movies_window()
        return

    if section_name == 'XXX':
        try:
            from resources.lib.gui.adult import open_xxx
            open_xxx()
        except Exception as exc:
            xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Adult section failed to open.\n%s' % exc)
        return

    if section_name == 'Cartoons & Anime':
        try:
            from resources.lib.gui.anime import open_anime
            open_anime()
        except Exception as exc:
            xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Anime failed to open.\n%s' % exc)
        return

    if section_name == 'Community Lists':
        try:
            from resources.lib.gui.community import open_community
            open_community()
        except Exception as exc:
            xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Community Lists failed to open.\n%s' % exc)
        return

    window = SectionWindow(section_name)
    window.doModal()
    del window
