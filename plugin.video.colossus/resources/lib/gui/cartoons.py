from __future__ import absolute_import

import os

import pyxbmct
import xbmc
import xbmcgui

from resources.lib.core import paths
from resources.lib.core import player
from resources.lib.gui.details import ColossusFullWindow
from resources.lib.gui.sports import busy_fetch, notify
from resources.lib.sources.cartoon import api as cartoon_api


def cartoon_art(focused=False):
    selected = paths.CARTOON_FOCUS_PATH
    normal = paths.CARTOON_PATH
    if focused and os.path.exists(selected):
        return selected
    if os.path.exists(normal):
        return normal
    return paths.ICON_PATH


def _rows(items):
    rows = []
    for item in items or []:
        row = dict(item)
        row['label'] = item.get('label') or item.get('title') or ''
        rows.append(row)
    return rows


class CartoonListWindow(ColossusFullWindow):
    def __init__(self, heading, status_text, items, on_select, empty_title, empty_meta, empty_overview, list_heading, tools=False):
        super(CartoonListWindow, self).__init__('')
        self.heading = heading
        self.status_text = status_text
        self.all_items = _rows(items)
        self.visible_items = list(self.all_items)
        self.on_select = on_select
        self.empty_title = empty_title
        self.empty_meta = empty_meta
        self.empty_overview = empty_overview
        self.list_heading_text = list_heading
        self.tools = tools
        self.letter = 'A'
        self.current_index = -1
        self.fallback_art = cartoon_art(focused=True)
        self.setup_canvas()
        self.set_controls()
        self.set_navigation()
        self.populate_list()
        self.setFocus(self.results_list)

    def set_controls(self):
        self.add_fanart(paths.BACKDROP_PATH or paths.FANART_PATH)

        self.back_button = pyxbmct.Button('Back')
        self.placeControl(self.back_button, 2, 2, 6, 10)
        self.connect(self.back_button, self.close)

        self.header_label = pyxbmct.Label(
            '[B]%s[/B]' % self.heading,
            font='font13',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.header_label, 2, 14, 6, 48)

        self.status_label = pyxbmct.Label(
            self.status_text,
            font='font12',
            textColor='0xFFD0D6DE',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.status_label, 2, 64, 6, 32)

        poster_height = 40 if self.tools else 48
        self.poster = pyxbmct.Image(self.fallback_art, aspectRatio=2)
        self.placeControl(self.poster, 12, 3, poster_height, 20)

        self.title_label = pyxbmct.Label(
            '[B]%s[/B]' % self.empty_title,
            font='font30',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.title_label, 12, 25, 10, 38)

        self.meta_label = pyxbmct.Label(
            self.empty_meta,
            font='font13',
            textColor='0xFFD0D6DE',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.meta_label, 23, 25, 6, 38)

        self.overview_box = pyxbmct.TextBox(font='font13', textColor='0xFFE8EEF4')
        self.placeControl(self.overview_box, 30, 25, 28, 38)
        self.overview_box.setText(self.empty_overview)

        if self.tools:
            self.az_button = pyxbmct.Button('A-Z')
            self.placeControl(self.az_button, 56, 3, 7, 9)
            self.connect(self.az_button, self.choose_letter)
            self.search_button = pyxbmct.Button('Search')
            self.placeControl(self.search_button, 56, 13, 7, 9)
            self.connect(self.search_button, self.search_titles)
        else:
            self.az_button = None
            self.search_button = None

        self.list_heading = pyxbmct.Label(
            '[B]%s[/B]' % self.list_heading_text,
            font='font13',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.list_heading, 8, 68, 6, 28)

        self.results_list = pyxbmct.List()
        self.placeControl(self.results_list, 14, 66, 78, 32)
        self.connect(self.results_list, self.select_current)

    def set_navigation(self):
        if self.az_button is not None:
            self.back_button.controlDown(self.az_button)
            self.back_button.controlRight(self.results_list)
            self.az_button.controlUp(self.back_button)
            self.az_button.controlRight(self.search_button)
            self.az_button.controlDown(self.results_list)
            self.search_button.controlUp(self.back_button)
            self.search_button.controlLeft(self.az_button)
            self.search_button.controlDown(self.results_list)
            self.results_list.controlLeft(self.az_button)
            self.results_list.controlUp(self.az_button)
        else:
            self.back_button.controlRight(self.results_list)
            self.back_button.controlDown(self.results_list)
            self.results_list.controlLeft(self.back_button)
            self.results_list.controlUp(self.back_button)

    def onAction(self, action):
        super(CartoonListWindow, self).onAction(action)
        self.update_preview()

    def replace_items(self, items, status_text, heading=None):
        self.all_items = _rows(items)
        self.status_text = status_text
        if heading:
            self.list_heading.setLabel('[B]%s[/B]' % heading)
        self.populate_list()
        self.setFocus(self.results_list)

    def populate_list(self):
        self.results_list.reset()
        self.current_index = -1
        self.visible_items = list(self.all_items)
        if not self.visible_items:
            self.results_list.addItem('Nothing found')
            self.status_label.setLabel(self.status_text or 'Nothing found.')
            self.title_label.setLabel('[B]Nothing found[/B]')
            self.meta_label.setLabel('')
            self.overview_box.setText('Try another letter or search.')
            try:
                self.poster.setImage(self.fallback_art)
            except Exception:
                pass
            return
        for item in self.visible_items:
            self.results_list.addItem(item.get('label') or '')
        self.status_label.setLabel('%s  |  %s' % (len(self.visible_items), self.status_text))
        self.update_preview(force=True)

    def choose_letter(self):
        letters = ['#'] + [chr(code) for code in range(ord('A'), ord('Z') + 1)]
        choice = xbmcgui.Dialog().select('A-Z', letters)
        if choice < 0:
            return
        self.letter = letters[choice]
        items = busy_fetch(lambda: cartoon_api.shows_for_letter(self.letter), 'Loading cartoons...')
        if items is None:
            return
        self.replace_items(items, 'Letter %s.' % self.letter, self.letter)

    def search_titles(self):
        keyboard = xbmc.Keyboard('', 'Search cartoons')
        keyboard.doModal()
        if not keyboard.isConfirmed():
            return
        phrase = (keyboard.getText() or '').strip()
        if not phrase:
            return
        items = busy_fetch(lambda: cartoon_api.search_shows(phrase), 'Searching...')
        if items is None:
            return
        self.replace_items(items, 'Results for %s.' % phrase, 'SEARCH')

    def select_current(self):
        position = self.results_list.getSelectedPosition()
        if position < 0 or position >= len(self.visible_items):
            return
        self.on_select(self.visible_items[position])

    def update_preview(self, force=False):
        if not self.visible_items:
            return
        try:
            index = self.results_list.getSelectedPosition()
        except Exception:
            return
        if index < 0 or index >= len(self.visible_items):
            return
        if not force and index == self.current_index:
            return
        self.current_index = index
        item = self.visible_items[index]
        self.title_label.setLabel('[B]%s[/B]' % (item.get('title') or self.empty_title))
        self.meta_label.setLabel(item.get('meta') or '')
        self.overview_box.setText(item.get('overview') or self.empty_overview)
        poster = item.get('poster') or self.fallback_art
        try:
            self.poster.setImage(poster)
        except Exception:
            pass


def _open_list(heading, status_text, items, on_select, empty_title, empty_meta, empty_overview, list_heading, tools=False):
    window = CartoonListWindow(
        heading,
        status_text,
        items,
        on_select,
        empty_title,
        empty_meta,
        empty_overview,
        list_heading,
        tools=tools
    )
    window.doModal()
    del window


def _play_episode(item):
    resolved = busy_fetch(lambda: cartoon_api.resolve_episode(item.get('href')), 'Starting episode...')
    if not resolved or not resolved.get('url'):
        return
    title = item.get('show_title') or 'Cartoon'
    episode = item.get('title') or ''
    if episode:
        title = '%s - %s' % (title, episode)
    player.play_stream(title, resolved.get('url'), resolved.get('headers') or {})


def _open_episodes(item):
    episodes = busy_fetch(lambda: cartoon_api.episodes_for(item), 'Loading episodes...')
    if not episodes:
        return
    _open_list(
        item.get('title') or 'Cartoon',
        'Select an episode.',
        episodes,
        _play_episode,
        item.get('title') or 'Cartoon',
        item.get('meta') or '',
        'Select an episode to play.',
        'EPISODES'
    )


def open_cartoon_catalog():
    items = busy_fetch(lambda: cartoon_api.shows_for_letter('A'), 'Loading cartoons...')
    if items is None:
        return
    if not items:
        notify('No titles found.')
        return
    _open_list(
        'CARTOONS',
        'Letter A.',
        items,
        _open_episodes,
        'Cartoons',
        'A-Z  |  Search',
        'Pick a letter or search, then open a series and choose an episode.',
        'A',
        tools=True
    )
