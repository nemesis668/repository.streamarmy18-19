from __future__ import absolute_import

import os

import pyxbmct
import xbmc
import xbmcgui

from resources.lib.core import paths
from resources.lib.core import player
from resources.lib.gui.details import ColossusFullWindow
from resources.lib.gui.sports import busy_fetch, notify
from resources.lib.sources.anime import api as anime_api
from resources.lib.sources.anime.api import AnimeError


def anime_art(focused=False):
    selected = paths.ANIME_FOCUS_PATH
    normal = paths.ANIME_PATH
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


class AnimeHubWindow(ColossusFullWindow):
    def __init__(self):
        super(AnimeHubWindow, self).__init__('')
        self.setup_canvas()
        self.set_controls()
        self.set_navigation()
        self.focus_anime()

    def onInit(self):
        self.focus_anime()

    def focus_anime(self):
        try:
            self.setFocus(self.anime_button)
        except Exception:
            pass
        self._paint('anime')

    def set_controls(self):
        self.add_fanart(paths.BACKDROP_PATH or paths.FANART_PATH)

        self.back_button = pyxbmct.Button('Back')
        self.placeControl(self.back_button, 2, 2, 6, 10)
        self.connect(self.back_button, self.close)

        self.header_label = pyxbmct.Label(
            '[B]CARTOONS & ANIME[/B]',
            font='font13',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.header_label, 2, 14, 6, 40)

        self.status_label = pyxbmct.Label(
            'Choose Anime or Cartoons.',
            font='font12',
            textColor='0xFFD0D6DE',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.status_label, 2, 56, 6, 40)

        self.poster = pyxbmct.Image(anime_art(focused=True), aspectRatio=0)
        self.placeControl(self.poster, 12, 3, 16, 16)

        self.title_label = pyxbmct.Label(
            '[B]Anime[/B]',
            font='font30',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.title_label, 12, 22, 8, 74)

        self.meta_label = pyxbmct.Label(
            'Latest  |  Top  |  Viewed  |  A-Z  |  Search  |  Random',
            font='font13',
            textColor='0xFFD0D6DE',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.meta_label, 20, 22, 5, 74)

        self.overview_box = pyxbmct.TextBox(font='font13', textColor='0xFFE8EEF4')
        self.placeControl(self.overview_box, 26, 22, 10, 74)
        self.overview_box.setText(
            'Anime has latest, top lists, most viewed, A-Z, search, and a random episode. '
            'Cartoons has an A-Z list and search. Open a title, pick an episode, then play.'
        )

        self.anime_image = pyxbmct.Image(anime_art(focused=True), aspectRatio=0)
        self.placeControl(self.anime_image, 40, 28, 40, 22, pad_x=0, pad_y=0)

        self.anime_button = pyxbmct.Button('', noFocusTexture='', focusTexture='')
        self.placeControl(self.anime_button, 40, 28, 40, 22, pad_x=0, pad_y=0)
        self.connect(self.anime_button, open_anime_catalog)

        self.anime_caption = pyxbmct.Label(
            '[COLOR aqua][B]ANIME[/B][/COLOR]',
            font='font13',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_CENTER
        )
        self.placeControl(self.anime_caption, 80, 28, 6, 22)

        from resources.lib.gui.cartoons import cartoon_art, open_cartoon_catalog
        self.cartoon_art = cartoon_art
        self.cartoon_image = pyxbmct.Image(cartoon_art(focused=False), aspectRatio=0)
        self.placeControl(self.cartoon_image, 40, 51, 40, 22, pad_x=0, pad_y=0)

        self.cartoon_button = pyxbmct.Button('', noFocusTexture='', focusTexture='')
        self.placeControl(self.cartoon_button, 40, 51, 40, 22, pad_x=0, pad_y=0)
        self.connect(self.cartoon_button, open_cartoon_catalog)

        self.cartoon_caption = pyxbmct.Label(
            '[B]CARTOONS[/B]',
            font='font13',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_CENTER
        )
        self.placeControl(self.cartoon_caption, 80, 51, 6, 22)

    def set_navigation(self):
        self.back_button.controlDown(self.anime_button)
        self.back_button.controlRight(self.anime_button)
        self.anime_button.controlUp(self.back_button)
        self.anime_button.controlRight(self.cartoon_button)
        self.cartoon_button.controlUp(self.back_button)
        self.cartoon_button.controlLeft(self.anime_button)

    def onAction(self, action):
        super(AnimeHubWindow, self).onAction(action)
        try:
            focused = self.getFocus()
        except Exception:
            focused = None
        if focused == self.cartoon_button:
            self._paint('cartoon')
        else:
            self._paint('anime')

    def _paint(self, key):
        anime_focused = key == 'anime'
        cartoon_focused = key == 'cartoon'
        anime_image = anime_art(focused=anime_focused)
        cartoon_image = self.cartoon_art(focused=cartoon_focused)
        preview = cartoon_image if cartoon_focused else anime_image
        try:
            self.anime_image.setImage(anime_image)
            self.cartoon_image.setImage(cartoon_image)
            self.poster.setImage(preview if os.path.exists(preview) else paths.ICON_PATH)
        except Exception:
            pass
        self.anime_caption.setLabel('[COLOR aqua][B]ANIME[/B][/COLOR]' if anime_focused else '[B]ANIME[/B]')
        self.cartoon_caption.setLabel('[COLOR aqua][B]CARTOONS[/B][/COLOR]' if cartoon_focused else '[B]CARTOONS[/B]')
        if cartoon_focused:
            self.title_label.setLabel('[B]Cartoons[/B]')
            self.meta_label.setLabel('A-Z  |  Search  |  Episodes')
            self.overview_box.setText(
                'Browse cartoons A to Z or search for a title. '
                'Open a series, pick an episode, and play.'
            )
        else:
            self.title_label.setLabel('[B]Anime[/B]')
            self.meta_label.setLabel('Latest  |  Top  |  Viewed  |  A-Z  |  Search  |  Random')
            self.overview_box.setText(
                'Browse latest releases, top lists by day, week, or month, most viewed, '
                'or A-Z. Search for a title, or jump to a random episode. '
                'Then pick a source to play.'
            )


class AnimeListWindow(ColossusFullWindow):
    def __init__(self, heading, status_text, items, on_select, empty_title, empty_meta, empty_overview, list_heading, tools=False):
        super(AnimeListWindow, self).__init__('')
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
        self.mode = 'latest'
        self.page = 1
        self.pages = 1
        self.letter = 'All'
        self.current_index = -1
        self.fallback_art = anime_art(focused=True)
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

        poster_height = 30 if self.tools else 48
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
            self.latest_button = pyxbmct.Button('Latest')
            self.top_button = pyxbmct.Button('Top')
            self.viewed_button = pyxbmct.Button('Viewed')
            self.az_button = pyxbmct.Button('A-Z')
            self.search_button = pyxbmct.Button('Search')
            self.random_button = pyxbmct.Button('Random')
            self.prev_button = pyxbmct.Button('Prev')
            self.next_button = pyxbmct.Button('Next')
            mode_buttons = (
                (self.latest_button, self.load_latest),
                (self.top_button, self.load_top),
                (self.viewed_button, self.load_viewed),
                (self.az_button, self.load_az),
                (self.search_button, self.search_titles),
                (self.random_button, self.load_random),
            )
            row = 44
            for button, action in mode_buttons:
                self.placeControl(button, row, 3, 6, 18)
                self.connect(button, action)
                row += 7
            self.placeControl(self.prev_button, 88, 3, 6, 8)
            self.placeControl(self.next_button, 88, 12, 6, 9)
            self.connect(self.prev_button, self.prev_page)
            self.connect(self.next_button, self.next_page)
            self._sync_pager()
        else:
            self.latest_button = None
            self.top_button = None
            self.viewed_button = None
            self.az_button = None
            self.search_button = None
            self.random_button = None
            self.prev_button = None
            self.next_button = None

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
        if self.latest_button is None:
            self.back_button.controlRight(self.results_list)
            self.back_button.controlDown(self.results_list)
            self.results_list.controlLeft(self.back_button)
            self.results_list.controlUp(self.back_button)
            return

        buttons = (
            self.latest_button,
            self.top_button,
            self.viewed_button,
            self.az_button,
            self.search_button,
            self.random_button,
        )
        self.back_button.controlDown(self.latest_button)
        self.back_button.controlRight(self.results_list)
        for index, button in enumerate(buttons):
            button.controlUp(buttons[index - 1] if index else self.back_button)
            if index + 1 < len(buttons):
                button.controlDown(buttons[index + 1])
            else:
                button.controlDown(self.prev_button)
            button.controlRight(self.results_list)
        self.prev_button.controlUp(self.random_button)
        self.prev_button.controlRight(self.next_button)
        self.next_button.controlUp(self.random_button)
        self.next_button.controlLeft(self.prev_button)
        self.results_list.controlLeft(self.latest_button)
        self.results_list.controlUp(self.back_button)

    def onAction(self, action):
        super(AnimeListWindow, self).onAction(action)
        self.update_preview()

    def replace_items(self, items, status_text):
        self.all_items = _rows(items)
        self.status_text = status_text
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
            self.overview_box.setText('Try another search.')
            try:
                self.poster.setImage(self.fallback_art)
            except Exception:
                pass
            return
        for item in self.visible_items:
            self.results_list.addItem(item.get('label') or '')
        self.status_label.setLabel('%s  |  %s' % (len(self.visible_items), self.status_text))
        self.update_preview(force=True)

    def _sync_pager(self):
        if self.prev_button is None:
            return
        visible = self.pages > 1
        for button, enabled in (
            (self.prev_button, visible and self.page > 1),
            (self.next_button, visible and self.page < self.pages),
        ):
            try:
                button.setVisible(visible)
                button.setEnabled(enabled)
            except Exception:
                pass

    def _show_catalog(self, items, heading, status, page=1, pages=1):
        self.page = page
        self.pages = max(int(pages or 1), 1)
        self.list_heading.setLabel('[B]%s[/B]' % heading)
        self._sync_pager()
        self.replace_items(items, status)
        if not items:
            notify('No titles found.')

    def load_latest(self):
        items = busy_fetch(anime_api.latest_titles, 'Loading latest anime...')
        if items is None:
            return
        self.mode = 'latest'
        self._show_catalog(items, 'LATEST', 'Select a title.')

    def load_top(self):
        choice = xbmcgui.Dialog().select('Top Anime', ['Day', 'Week', 'Month'])
        if choice < 0:
            return
        period = ('day', 'week', 'month')[choice]
        label = ('DAY', 'WEEK', 'MONTH')[choice]
        items = busy_fetch(lambda: anime_api.top_titles(period), 'Loading top anime...')
        if items is None:
            return
        self.mode = 'top'
        self._show_catalog(items, 'TOP · %s' % label, 'Select a title.')

    def load_viewed(self, page=1):
        if not isinstance(page, int):
            page = 1
        page = int(page or 1)
        payload = busy_fetch(lambda: anime_api.most_viewed(page), 'Loading most viewed...')
        if not payload:
            return
        self.mode = 'viewed'
        self._show_catalog(
            payload.get('items') or [],
            'MOST VIEWED',
            'Page %s of %s.' % (payload.get('page') or page, payload.get('pages') or 1),
            payload.get('page') or page,
            payload.get('pages') or 1
        )

    def load_az(self):
        letters = ['All', '#', '0-9'] + [chr(code) for code in range(ord('A'), ord('Z') + 1)]
        choice = xbmcgui.Dialog().select('A-Z', letters)
        if choice < 0:
            return
        self.letter = letters[choice]
        self.load_az_page(1)

    def load_az_page(self, page):
        letter = self.letter or 'All'
        payload = busy_fetch(
            lambda: anime_api.az_titles(letter, page),
            'Loading A-Z...'
        )
        if not payload:
            return
        self.mode = 'az'
        self.letter = payload.get('letter') or letter
        self._show_catalog(
            payload.get('items') or [],
            'A-Z · %s' % self.letter,
            'Page %s of %s.' % (payload.get('page') or page, payload.get('pages') or 1),
            payload.get('page') or page,
            payload.get('pages') or 1
        )

    def prev_page(self):
        if self.page <= 1:
            return
        self._turn_page(self.page - 1)

    def next_page(self):
        if self.page >= self.pages:
            return
        self._turn_page(self.page + 1)

    def _turn_page(self, page):
        if self.mode == 'viewed':
            self.load_viewed(page)
        elif self.mode == 'az':
            self.load_az_page(page)

    def search_titles(self):
        keyboard = xbmc.Keyboard('', 'Search anime')
        keyboard.doModal()
        if not keyboard.isConfirmed():
            return
        phrase = (keyboard.getText() or '').strip()
        if not phrase:
            return
        items = busy_fetch(lambda: anime_api.search_titles(phrase), 'Searching...')
        if items is None:
            return
        self.mode = 'search'
        self._show_catalog(items, 'SEARCH', 'Results for %s.' % phrase)

    def load_random(self):
        episode = busy_fetch(anime_api.random_episode, 'Picking a random episode...')
        if not episode:
            return
        _open_servers(episode)

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
    window = AnimeListWindow(
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


def _play_server(item):
    try:
        resolved = busy_fetch(lambda: anime_api.resolve_server(item), 'Starting source...')
    except AnimeError as exc:
        notify(str(exc))
        return
    if not resolved or not resolved.get('url'):
        return
    title = item.get('show_title') or 'Anime'
    episode = item.get('episode_title') or item.get('title') or ''
    if episode:
        title = '%s - %s' % (title, episode)
    subtitle = resolved.get('subtitle') or ''
    player.play_stream(
        title,
        resolved.get('url'),
        resolved.get('headers') or {},
        subtitles=[subtitle] if subtitle else None
    )


def _open_servers(item):
    try:
        servers = busy_fetch(lambda: anime_api.servers_for(item), 'Loading sources...')
    except AnimeError as exc:
        notify(str(exc))
        return
    if servers is None:
        return
    if not servers:
        notify('That episode has no sources.')
        return
    heading = item.get('show_title') or 'Anime'
    _open_list(
        heading,
        'Choose a source.',
        servers,
        _play_server,
        item.get('title') or 'Episode',
        'Choose a source',
        item.get('overview') or 'Select a source to play.',
        'SOURCES'
    )


def _open_episodes(item):
    try:
        episodes = busy_fetch(lambda: anime_api.episodes_for(item), 'Loading episodes...')
    except AnimeError as exc:
        notify(str(exc))
        return
    if episodes is None:
        return
    if not episodes:
        notify('That title has no episodes.')
        return
    for episode in episodes:
        audio = episode.get('meta') or ''
        episode['label'] = episode.get('title') or 'Episode'
        if audio and audio != 'Episode':
            episode['label'] = '%s  |  %s' % (episode['label'], audio)
    _open_list(
        item.get('title') or 'Anime',
        'Select an episode.',
        episodes,
        _open_servers,
        item.get('title') or 'Anime',
        item.get('meta') or '',
        episodes[0].get('overview') or 'Select an episode.',
        'EPISODES'
    )


def open_anime_catalog():
    try:
        items = busy_fetch(anime_api.latest_titles, 'Loading latest anime...')
    except AnimeError as exc:
        notify(str(exc))
        return
    if items is None:
        return
    if not items:
        notify('No titles found.')
        return
    _open_list(
        'ANIME',
        'Select a title.',
        items,
        _open_episodes,
        'Anime',
        'Latest, top, viewed, A-Z, search, or random.',
        'Highlight a title to see the poster, then select it to open episodes.',
        'LATEST',
        tools=True
    )


def open_anime():
    window = AnimeHubWindow()
    window.show()
    xbmc.sleep(50)
    window.focus_anime()
    window.doModal()
    del window
