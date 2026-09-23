from __future__ import absolute_import

import os
import re

import pyxbmct
import xbmc
import xbmcgui

from resources.lib.core import paths
from resources.lib.gui.details import ColossusFullWindow
from resources.lib.gui.sports import notify


def _listing_art(path, fallback=None):
    fallback = fallback or paths.ICON_PATH
    if path:
        text = str(path).strip()
        if text.startswith('//'):
            text = 'https:' + text
        lowered = text.lower()
        if lowered.startswith('http://') or lowered.startswith('https://'):
            return text
    return fallback


def _confirm_age():
    marker = os.path.join(paths.PROFILE_PATH, 'xxx_age_ok')
    if os.path.exists(marker):
        return True
    accepted = xbmcgui.Dialog().yesno(
        paths.ADDON_NAME,
        'This section is for adults only.\n'
        'If you are not 18 or over, go back.\n'
        'You can hide the Adult tile by turning on Disable adult in Settings.',
        nolabel='Back',
        yeslabel='I am 18+'
    )
    if not accepted:
        return False
    try:
        with open(marker, 'w') as handle:
            handle.write('ok')
    except Exception:
        pass
    return True


def _load_xxx():
    progress = xbmcgui.DialogProgress()
    progress.create(paths.ADDON_NAME, 'Loading adult sources...')
    try:
        import colossusxxx
        colossusxxx.ensure_loaded()
        return colossusxxx
    except Exception as exc:
        xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Adult sources failed to load.\n%s' % exc)
        return None
    finally:
        try:
            progress.close()
        except Exception:
            pass


def _run_listing(xxx, payload, message):
    progress = xbmcgui.DialogProgress()
    progress.create(paths.ADDON_NAME, message)
    try:
        return xxx.browse(payload)
    except SystemExit:
        notify('Nothing found.')
        return []
    except Exception as exc:
        xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Could not load that list.\n%s' % exc)
        return None
    finally:
        try:
            progress.close()
        except Exception:
            pass


def _tile_art(normal, selected, focused=False):
    if focused and os.path.exists(selected):
        return selected
    if os.path.exists(normal):
        return normal
    return paths.ICON_PATH


def sites_art(focused=False):
    return _tile_art(paths.XXX_SITES_PATH, paths.XXX_SITES_FOCUS_PATH, focused)


def cams_art(focused=False):
    return _tile_art(paths.XXX_CAMS_PATH, paths.XXX_CAMS_FOCUS_PATH, focused)


def movies_art(focused=False):
    return _tile_art(paths.XXX_MOVIES_PATH, paths.XXX_MOVIES_FOCUS_PATH, focused)


HUB_OPTIONS = (
    {
        'key': 'sites',
        'caption': 'SITES',
        'title': 'Sites',
        'meta': 'Tubes  |  Categories  |  Videos',
        'overview': 'Browse every tube and site, open a source, then pick a video to play.',
        'section': 'sites',
        'list_heading': 'SITES',
        'empty_overview': 'Highlight a site, then select it to browse.',
        'art': sites_art,
    },
    {
        'key': 'cams',
        'caption': 'LIVE CAMS',
        'title': 'Live Cams',
        'meta': 'Live rooms  |  Tags  |  Play',
        'overview': 'Open a live cam source, browse rooms that are online, then play a stream.',
        'section': 'cams',
        'list_heading': 'CAMS',
        'empty_overview': 'Highlight a cam source, then select it to browse live rooms.',
        'art': cams_art,
    },
    {
        'key': 'movies',
        'caption': 'MOVIES',
        'title': 'Movies',
        'meta': 'Full movies  |  Scenes  |  Play',
        'overview': 'Browse movie sources, pick a title, then resolve and play.',
        'section': 'movies',
        'list_heading': 'MOVIES',
        'empty_overview': 'Highlight a movie source, then select it to browse titles.',
        'art': movies_art,
    },
)


def open_section_list(xxx, option):
    section = option['section']
    sites = xxx.list_sites(section)
    if not sites:
        notify('No sources found in that section.')
        return
    items = [xxx.gui_site_item(site) for site in sites]
    for item in items:
        item['art'] = paths.ICON_PATH
    window = AdultBrowseWindow(
        heading=option['caption'],
        status_text='%s sources  |  Select a source.' % len(items),
        items=items,
        xxx=xxx,
        art_path=paths.ICON_PATH,
        empty_title=option['title'],
        empty_meta='Select a source',
        empty_overview=option['empty_overview'],
        allow_search=True,
        search_heading='Search all sources',
        search_button_text='Search',
        list_heading=option['list_heading'],
        search_section=option['section']
    )
    window.doModal()
    del window


def _prompt_keyword(heading):
    keyboard = xbmc.Keyboard('', heading)
    keyboard.doModal()
    if not keyboard.isConfirmed():
        return ''
    return (keyboard.getText() or '').strip()


def _should_prompt_site_search(payload):
    if payload.get('keyword'):
        return False
    mode = str(payload.get('mode') or '')
    if mode.startswith('utils.'):
        return False
    name = _plain(payload.get('name') or '')
    if not re.search(r'search', name, re.I):
        return False
    if 'search' not in mode.lower():
        return False
    return True


def _open_global_search(xxx, section):
    phrase = _prompt_keyword('Search all sources')
    if not phrase:
        return
    progress = xbmcgui.DialogProgress()
    progress.create(paths.ADDON_NAME, 'Starting search...')
    try:
        results = xxx.search_all(phrase, section, progress)
    except Exception as exc:
        xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Search failed.\n%s' % exc)
        return
    finally:
        try:
            progress.close()
        except Exception:
            pass
    if not results:
        notify('No results found.')
        return
    items = [xxx.gui_list_item(entry, paths.ICON_PATH) for entry in results]
    for item in items:
        item['art'] = _listing_art(item.get('art'), paths.ICON_PATH)
    window = AdultBrowseWindow(
        heading='SEARCH',
        status_text='%s results  |  %s' % (len(items), phrase),
        items=items,
        xxx=xxx,
        art_path=paths.ICON_PATH,
        empty_title=phrase,
        empty_meta='Select a result',
        empty_overview='Highlight a result, then select it to open or play.',
        allow_search=True,
        search_heading='Filter results',
        search_button_text='Filter',
        list_heading='RESULTS',
        split_nav=False
    )
    window.doModal()
    del window


def _open_listing(xxx, payload, heading, art_path):
    if _should_prompt_site_search(payload):
        phrase = _prompt_keyword(_plain(payload.get('name') or 'Search'))
        if not phrase:
            return
        payload = dict(payload)
        payload['keyword'] = phrase
        payload['folder'] = True
    entries = _run_listing(xxx, payload, 'Loading...')
    if entries is None:
        return
    if xxx.is_play_item(payload):
        return
    if not entries:
        if payload.get('folder') is False:
            return
        notify('Nothing found.')
        return
    items = [xxx.gui_list_item(entry, paths.ICON_PATH) for entry in entries]
    for item in items:
        item['art'] = _listing_art(item.get('art'), paths.ICON_PATH)
    name = payload.get('keyword') or payload.get('name') or heading
    window = AdultBrowseWindow(
        heading=_plain(name).upper()[:48],
        status_text='%s items  |  Select an item.' % len(items),
        items=items,
        xxx=xxx,
        art_path=_listing_art(art_path, paths.ICON_PATH),
        empty_title=_plain(name),
        empty_meta='Select an item',
        empty_overview='Highlight an item, then select it to open or play.',
        allow_search=True,
        search_heading='Search this list',
        search_button_text='Search',
        list_heading='RESULTS',
        split_nav=True
    )
    window.doModal()
    del window


def _plain(text):
    text = text or ''
    text = re.sub(r'\[/?COLOR[^\]]*\]', '', text)
    text = re.sub(r'\[/?B\]', '', text)
    return text.replace('[CR]', ' ').strip() or 'Adult'


_NEXT_RE = re.compile(
    r'next page|previous page|currently in page|load more|^next\b|^prev(ious)?\b',
    re.I
)
_MENU_RE = re.compile(
    r'^(search|categor(y|ies)|actors?|studios?|tags?|models?|pornstars?|'
    r'channels?|photos?|movies?|films?|scenes?|networks?|performers?|'
    r'newest|popular|trending|featured|recommended|top rated|most recent|'
    r'being watched|login|logout|favorites?|a-z|live|webcams?|sort|'
    r'collections?|playlists?|sponsors?)\b',
    re.I
)
_COLOR_MENU_RE = re.compile(r'\[color (hotpink|deeppink|pink)\]', re.I)


def _is_nav_item(item, mixed_with_videos):
    data = item.get('data') or {}
    kind = (data.get('kind') or '').lower()
    if kind == 'video':
        return False
    try:
        import colossusxxx
        if colossusxxx.is_play_item(data):
            return False
    except Exception:
        pass
    raw = '%s %s' % (item.get('label') or '', data.get('name') or '')
    plain = _plain(raw)
    if _NEXT_RE.search(plain):
        return True
    if _COLOR_MENU_RE.search(raw):
        return True
    if mixed_with_videos and kind == 'dir':
        return True
    if data.get('folder') is False and _MENU_RE.match(plain.strip()):
        return True
    if _MENU_RE.match(plain.strip()):
        return True
    return False


def _split_nav_items(items, split_nav):
    items = list(items or [])
    if not split_nav:
        return [], items
    mixed = False
    for item in items:
        data = item.get('data') or {}
        if (data.get('kind') or '').lower() == 'video':
            mixed = True
            break
    nav = []
    content = []
    for item in items:
        if _is_nav_item(item, mixed):
            nav.append(item)
        else:
            content.append(item)
    return nav, content


def _nav_label(item):
    text = _plain(item.get('title') or item.get('label') or 'Open')
    lowered = text.lower()
    if 'next page' in lowered or lowered.startswith('next'):
        return 'Next'
    if 'prev' in lowered and 'page' in lowered:
        return 'Previous'
    if len(text) > 18:
        return text[:16] + '...'
    return text


def _play_adult(result, title):
    from urllib.parse import unquote

    url = ''
    if isinstance(result, dict):
        url = result.get('url') or ''
    elif isinstance(result, str):
        url = result
    if not url:
        xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Could not get a playable link.')
        return
    headers = {}
    if '|' in url:
        url, blob = url.split('|', 1)
        for part in blob.split('&'):
            if '=' not in part:
                continue
            key, value = part.split('=', 1)
            headers[unquote(key)] = unquote(value)
    from resources.lib.core import player
    player.play_stream(title or 'Adult', url, headers)


def _on_item(xxx, item, fallback_art):
    payload = item.get('data') or {}
    art = _listing_art(item.get('art'), fallback_art or paths.ICON_PATH)
    if xxx.is_play_item(payload):
        try:
            result = xxx.play(payload)
            _play_adult(result, item.get('title') or 'Adult')
        except Exception as exc:
            xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Playback failed.\n%s' % exc)
        return
    _open_listing(xxx, payload, payload.get('name') or item.get('title') or 'Adult', art)


class AdultHubWindow(ColossusFullWindow):
    def __init__(self, xxx):
        super(AdultHubWindow, self).__init__('')
        self.xxx = xxx
        self.option_images = {}
        self.option_buttons = {}
        self.option_captions = {}
        self.setup_canvas()
        self.set_controls()
        self.set_navigation()
        self.focus_sites()

    def onInit(self):
        self.focus_sites()

    def focus_sites(self):
        sites = self.option_buttons.get('sites')
        if sites is None:
            return
        try:
            self.setFocus(sites)
        except Exception:
            pass
        self.update_hub_preview()

    def set_controls(self):
        self.add_fanart(paths.BACKDROP_PATH or paths.FANART_PATH)

        self.back_button = pyxbmct.Button('Back')
        self.placeControl(self.back_button, 2, 2, 6, 10)
        self.connect(self.back_button, self.close)

        self.header_label = pyxbmct.Label(
            '[B]XXX[/B]',
            font='font13',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.header_label, 2, 14, 6, 30)

        self.status_label = pyxbmct.Label(
            'Choose Sites, Live Cams, or Movies.',
            font='font12',
            textColor='0xFFD0D6DE',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.status_label, 2, 46, 6, 50)

        self.poster = pyxbmct.Image(sites_art(focused=True), aspectRatio=0)
        self.placeControl(self.poster, 12, 3, 16, 16)

        self.title_label = pyxbmct.Label(
            '[B]Sites[/B]',
            font='font30',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.title_label, 12, 22, 8, 74)

        self.meta_label = pyxbmct.Label(
            HUB_OPTIONS[0]['meta'],
            font='font13',
            textColor='0xFFD0D6DE',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.meta_label, 20, 22, 5, 74)

        self.overview_box = pyxbmct.TextBox(font='font13', textColor='0xFFE8EEF4')
        self.placeControl(self.overview_box, 26, 22, 10, 74)
        self.overview_box.setText(HUB_OPTIONS[0]['overview'])

        layouts = ((40, 8), (40, 37), (40, 66))
        for option, (row, column) in zip(HUB_OPTIONS, layouts):
            art = option['art'](focused=(option['key'] == 'sites'))
            image = pyxbmct.Image(art if os.path.exists(art) else paths.ICON_PATH, aspectRatio=0)
            self.option_images[option['key']] = image
            self.placeControl(image, row, column, 40, 26, pad_x=0, pad_y=0)

            button = pyxbmct.Button('', noFocusTexture='', focusTexture='')
            self.option_buttons[option['key']] = button
            self.placeControl(button, row, column, 40, 26, pad_x=0, pad_y=0)
            self.connect(button, (lambda current=option: open_section_list(self.xxx, current)))

            caption = pyxbmct.Label(
                '[COLOR aqua][B]%s[/B][/COLOR]' % option['caption'] if option['key'] == 'sites' else '[B]%s[/B]' % option['caption'],
                font='font13',
                textColor='0xFFFFFFFF',
                alignment=pyxbmct.ALIGN_CENTER
            )
            self.option_captions[option['key']] = caption
            self.placeControl(caption, 80, column, 6, 26)

    def set_navigation(self):
        sites = self.option_buttons['sites']
        cams = self.option_buttons['cams']
        movies = self.option_buttons['movies']

        self.back_button.controlDown(sites)
        self.back_button.controlRight(sites)

        sites.controlUp(self.back_button)
        sites.controlRight(cams)

        cams.controlUp(self.back_button)
        cams.controlLeft(sites)
        cams.controlRight(movies)

        movies.controlUp(self.back_button)
        movies.controlLeft(cams)

    def onAction(self, action):
        super(AdultHubWindow, self).onAction(action)
        self.update_hub_preview()

    def update_hub_preview(self):
        try:
            focused = self.getFocus()
        except Exception:
            return

        current = HUB_OPTIONS[0]
        for option in HUB_OPTIONS:
            caption = self.option_captions[option['key']]
            is_focused = focused == self.option_buttons[option['key']]
            if is_focused:
                current = option
                caption.setLabel('[COLOR aqua][B]%s[/B][/COLOR]' % option['caption'])
            else:
                caption.setLabel('[B]%s[/B]' % option['caption'])
            art = option['art'](focused=is_focused)
            try:
                self.option_images[option['key']].setImage(art)
            except Exception:
                pass

        art = current['art'](focused=True)
        try:
            self.poster.setImage(art if os.path.exists(art) else paths.ICON_PATH)
        except Exception:
            pass
        self.title_label.setLabel('[B]%s[/B]' % current['title'])
        self.meta_label.setLabel(current['meta'])
        self.overview_box.setText(current['overview'])


class AdultBrowseWindow(ColossusFullWindow):
    def __init__(
        self,
        heading,
        status_text,
        items,
        xxx,
        art_path,
        empty_title,
        empty_meta,
        empty_overview,
        allow_search=False,
        search_heading='Search',
        search_button_text='Search',
        list_heading='RESULTS',
        split_nav=False,
        search_section=None
    ):
        super(AdultBrowseWindow, self).__init__('')
        self.heading = heading
        self.status_text = status_text
        self.nav_items, content_items = _split_nav_items(items, split_nav)
        self.all_items = list(content_items)
        self.visible_items = list(self.all_items)
        self.xxx = xxx
        self.art_path = art_path
        self.empty_title = empty_title
        self.empty_meta = empty_meta
        self.empty_overview = empty_overview
        self.allow_search = allow_search
        self.search_heading = search_heading
        self.search_button_text = search_button_text or 'Search'
        self.search_section = search_section
        if self.nav_items and self.search_button_text == 'Search' and not self.search_section:
            self.search_button_text = 'Filter'
        self.list_heading_text = list_heading
        self.current_index = -1
        self.nav_buttons = []
        self.setup_canvas()
        self.set_controls()
        self.set_navigation()
        self.populate_list()
        try:
            self.setFocus(self.results_list)
        except Exception:
            if self.search_button is not None:
                self.setFocus(self.search_button)

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

        button_slots = len(self.nav_items) + (1 if self.allow_search else 0)
        if button_slots:
            poster_h = max(16, min(40, 78 - 2 - (5 * button_slots)))
        else:
            poster_h = 48
        self.poster = pyxbmct.Image(_listing_art(self.art_path, paths.ICON_PATH), aspectRatio=0)
        self.placeControl(self.poster, 12, 3, poster_h, 20)

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

        row = 12 + poster_h + 2
        if self.allow_search:
            self.search_button = pyxbmct.Button(self.search_button_text)
            self.placeControl(self.search_button, row, 3, 5, 18)
            self.connect(self.search_button, self.search_items)
            row += 5
        else:
            self.search_button = None

        max_nav = max(0, (96 - row) // 5)
        extra_nav = self.nav_items[max_nav:]
        if extra_nav:
            self.all_items = extra_nav + self.all_items
            self.visible_items = list(self.all_items)
        for item in self.nav_items[:max_nav]:
            button = pyxbmct.Button(_nav_label(item))
            self.placeControl(button, row, 3, 5, 18)
            self.connect(button, (lambda current=item: _on_item(self.xxx, current, self.art_path)))
            self.nav_buttons.append(button)
            row += 5

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
        left_controls = []
        if self.search_button is not None:
            left_controls.append(self.search_button)
        left_controls.extend(self.nav_buttons)

        if not left_controls:
            self.back_button.controlRight(self.results_list)
            self.back_button.controlDown(self.results_list)
            self.results_list.controlLeft(self.back_button)
            self.results_list.controlUp(self.back_button)
            return

        first = left_controls[0]
        last = left_controls[-1]
        self.back_button.controlRight(first)
        self.back_button.controlDown(first)
        first.controlUp(self.back_button)
        first.controlLeft(self.back_button)

        for index, control in enumerate(left_controls):
            control.controlRight(self.results_list)
            if index > 0:
                control.controlUp(left_controls[index - 1])
            if index < len(left_controls) - 1:
                control.controlDown(left_controls[index + 1])
            else:
                control.controlDown(self.results_list)
            control.controlLeft(self.back_button)

        self.results_list.controlLeft(last)
        self.results_list.controlUp(last)

    def onAction(self, action):
        super(AdultBrowseWindow, self).onAction(action)
        self.update_preview()

    def populate_list(self, query=''):
        query = (query or '').strip().lower()
        self.results_list.reset()
        self.current_index = -1
        if query:
            self.visible_items = []
            for item in self.all_items:
                haystack = ' '.join([
                    item.get('label') or '',
                    item.get('title') or '',
                    item.get('meta') or '',
                    item.get('overview') or '',
                    item.get('search') or '',
                ]).lower()
                if query in haystack:
                    self.visible_items.append(item)
        else:
            self.visible_items = list(self.all_items)

        if not self.visible_items:
            if self.nav_items and not query:
                self.results_list.addItem('Choose a section')
                self.status_label.setLabel('Use the buttons on the left.')
                self.title_label.setLabel('[B]%s[/B]' % self.empty_title)
                self.meta_label.setLabel('')
                self.overview_box.setText('Open a section on the left to load results.')
            else:
                self.results_list.addItem('No matches')
                self.status_label.setLabel('0 matches  |  Try another search.')
                self.title_label.setLabel('[B]No matches[/B]')
                self.meta_label.setLabel('')
                self.overview_box.setText('No items matched that search.')
            return

        for item in self.visible_items:
            self.results_list.addItem(_plain(item.get('title') or item.get('label') or ''))
        count_label = 'matches' if query else self.list_heading_text.lower()
        self.status_label.setLabel('%s %s  |  Select an item.' % (
            len(self.visible_items),
            count_label
        ))
        self.update_preview(force=True)

    def search_items(self):
        if self.search_section:
            _open_global_search(self.xxx, self.search_section)
            return
        keyboard = xbmc.Keyboard('', self.search_heading)
        keyboard.doModal()
        if not keyboard.isConfirmed():
            return
        self.populate_list(keyboard.getText())
        self.setFocus(self.results_list)

    def select_current(self):
        position = self.results_list.getSelectedPosition()
        if position < 0 or position >= len(self.visible_items):
            return
        _on_item(self.xxx, self.visible_items[position], self.art_path)

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
        try:
            self.poster.setImage(_listing_art(item.get('art'), self.art_path or paths.ICON_PATH))
        except Exception:
            pass


def open_xxx():
    if paths.ADDON.getSetting('disable_adult') == 'true':
        return
    from resources.lib.core import adult_lock
    if not adult_lock.unlock():
        return
    if not _confirm_age():
        return
    xxx = _load_xxx()
    if xxx is None:
        return
    window = AdultHubWindow(xxx)
    window.show()
    xbmc.sleep(50)
    window.focus_sites()
    window.doModal()
    del window
