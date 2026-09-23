from __future__ import absolute_import

import json
import os
import re
import time

import pyxbmct
import xbmc
import xbmcgui

from resources.lib.core import paths
from resources.lib.core import player
from resources.lib.gui.details import ColossusFullWindow
from resources.lib.gui.sports import SportsBrowseWindow, busy_fetch, notify
from resources.lib.gui.podcasts import open_podcasts, podcast_art
from resources.lib.gui.mp3s import open_mp3, mp3_art
from resources.lib.sources.fmstream import api as fmstream
from resources.lib.sources.fmstream.api import FmstreamBlocked, PAGE_SIZE


CACHE_TTL = 8 * 3600
CACHE_FOLDER = 'fmstream'


def _cache_dir():
    folder = os.path.join(paths.PROFILE_PATH, CACHE_FOLDER)
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


def _cache_get(name):
    path = os.path.join(_cache_dir(), name)
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            payload = json.load(handle)
        if time.time() - float(payload.get('fetched') or 0) > CACHE_TTL:
            return None
        return payload.get('data')
    except Exception:
        return None


def _cache_set(name, data):
    path = os.path.join(_cache_dir(), name)
    try:
        with open(path, 'w', encoding='utf-8') as handle:
            json.dump({'fetched': time.time(), 'data': data}, handle)
    except Exception:
        pass


def world_radio_art(focused=False):
    selected = paths.WORLD_RADIO_FOCUS_PATH
    normal = paths.WORLD_RADIO_PATH
    if focused and os.path.exists(selected):
        return selected
    if os.path.exists(normal):
        return normal
    return paths.ICON_PATH


def load_countries():
    cached = _cache_get('countries.json')
    if cached:
        return cached
    countries = fmstream.get_countries()
    if countries:
        _cache_set('countries.json', countries)
    return countries


def _safe_search(text):
    return re.sub(r'[^a-zA-Z0-9 ]+', '', text or '').strip()


def load_station_page(country, offset=0, search=''):
    code = (country or {}).get('code') or ''
    search = _safe_search(search)
    cache_name = 'page_%s_%s_%s.json' % (
        code.replace('/', '_'),
        int(offset or 0),
        search.replace(' ', '_')[:40]
    )
    cached = _cache_get(cache_name)
    if cached:
        return cached
    try:
        page = fmstream.get_station_page(code, offset, search)
    except FmstreamBlocked:
        raise RuntimeError(
            'Could not load that list. Try again in a moment.'
        )
    if page and page.get('stations'):
        _cache_set(cache_name, page)
    return page


def page_status(country, page):
    stations = (page or {}).get('stations') or []
    offset = int((page or {}).get('offset') or 0)
    total = int((country or {}).get('count') or 0)
    start = offset + 1 if stations else 0
    end = offset + len(stations)
    query = (page or {}).get('query') or ''
    if query:
        return 'Results %s-%s  |  Select a station.' % (start, end)
    if total:
        return '%s-%s of %s  |  Select a station.' % (start, end, total)
    return '%s stations  |  Select a station.' % len(stations)


def pager_item(kind, offset, country):
    total = int((country or {}).get('count') or 0)
    if kind == 'prev':
        start = max(1, offset - PAGE_SIZE + 1)
        end = offset
        return {
            'label': '[B]<< Previous 50[/B]',
            'title': 'Previous 50',
            'meta': 'Stations %s-%s' % (start, end) if end else 'Previous page',
            'overview': 'Load the previous 50 stations.',
            'data': {'page': 'prev', 'offset': max(0, offset - PAGE_SIZE)},
        }
    next_start = offset + 1
    next_end = offset + PAGE_SIZE
    if total:
        next_end = min(total, next_end)
    return {
        'label': '[B]Next 50 >>[/B]',
        'title': 'Next 50',
        'meta': 'Stations %s-%s' % (next_start, next_end),
        'overview': 'Load the next 50 stations.',
        'data': {'page': 'next', 'offset': offset},
    }


def station_page_items(country, page):
    name = (country or {}).get('name') or ''
    offset = int((page or {}).get('offset') or 0)
    stations = (page or {}).get('stations') or []
    items = []
    if offset > 0:
        items.append(pager_item('prev', offset, country))
    for station in stations:
        items.append(station_item(station, name))
    if page.get('has_more'):
        items.append(pager_item('next', offset + PAGE_SIZE, country))
    return items


def country_item(country):
    name = country.get('name') or 'Country'
    count = int(country.get('count') or 0)
    return {
        'label': '%s    (%s)' % (name, count),
        'title': name,
        'meta': '%s stations' % count,
        'overview': 'Open %s to browse %s live radio stations, then choose a stream to play.' % (
            name,
            count
        ),
        'search': '%s %s' % (name, country.get('code') or ''),
        'data': country,
    }


def station_item(station, country_name=''):
    name = station.get('name') or 'Station'
    streams = fmstream.playable_streams(station)
    location = ', '.join([part for part in (station.get('city'), station.get('region'), country_name) if part])
    style = station.get('style') or ''
    meta_parts = [part for part in (location, style, '%s streams' % len(streams)) if part]
    overview_parts = [
        station.get('slogan') or '',
        station.get('description') or '',
        station.get('frequencies') or '',
        station.get('homepage') or '',
    ]
    overview = '\n'.join([part for part in overview_parts if part]) or (
        'Select this station to choose a stream.'
    )
    return {
        'label': name,
        'title': name,
        'meta': '   |   '.join(meta_parts),
        'overview': overview,
        'search': ' '.join([
            name,
            location,
            style,
            station.get('branding') or '',
            station.get('slogan') or '',
            station.get('description') or '',
        ]),
        'data': station,
    }


def stream_item(stream, station, index, total):
    label = fmstream.format_stream_label(stream)
    codec = (stream.get('codec') or '').upper()
    region = stream.get('region') or ''
    meta_parts = [
        'Source %s of %s' % (index, total),
        codec,
        fmstream.format_kbps(stream.get('bitrate')),
        region,
    ]
    return {
        'label': label,
        'title': label,
        'meta': '  |  '.join([part for part in meta_parts if part]),
        'overview': 'Play this stream for %s.' % (station.get('name') or 'this station'),
        'data': {
            'title': station.get('name') or 'World Radio',
            'url': stream.get('url') or '',
            'codec': stream.get('codec') or '',
        },
    }


def open_world_radio():
    countries = busy_fetch(load_countries, 'Loading countries...')
    if countries is None:
        return
    if not countries:
        notify('No countries found.')
        return

    items = [country_item(country) for country in countries]
    window = SportsBrowseWindow(
        heading='WORLD RADIO',
        status_text='%s countries  |  Select a country.' % len(items),
        items=items,
        on_select=_open_country,
        art_path=world_radio_art(),
        empty_title='World Radio',
        empty_meta='Choose a country',
        empty_overview='Highlight a country to see how many stations it has, then select it to load them.',
        allow_search=True,
        search_heading='Search country',
        search_button_text='Search country',
        list_heading='COUNTRIES'
    )
    window.doModal()
    del window


def _open_country(item):
    country = item.get('data') or {}
    name = country.get('name') or 'Country'
    page = busy_fetch(
        lambda: load_station_page(country, 0, ''),
        'Loading %s...' % name
    )
    if page is None:
        return
    if not page.get('stations'):
        notify('No stations found for %s.' % name)
        return

    window = StationBrowseWindow(country, page)
    window.doModal()
    del window


class StationBrowseWindow(SportsBrowseWindow):
    def __init__(self, country, page):
        self.country = country or {}
        self.page = page or {}
        self.offset = int(self.page.get('offset') or 0)
        self.query = self.page.get('query') or ''
        name = self.country.get('name') or 'Stations'
        super(StationBrowseWindow, self).__init__(
            heading=name.upper(),
            status_text=page_status(self.country, self.page),
            items=station_page_items(self.country, self.page),
            on_select=self.handle_select,
            art_path=world_radio_art(),
            empty_title=name,
            empty_meta='Select a station',
            empty_overview='Search or highlight a station, then select it to view streams. Use Next 50 for more pages.',
            allow_search=True,
            search_heading='Search station',
            search_button_text='Search station',
            list_heading='STATIONS'
        )
        self.prev_button = pyxbmct.Button('Previous 50')
        self.placeControl(self.prev_button, 76, 3, 8, 14)
        self.connect(self.prev_button, self.go_previous)
        self.next_button = pyxbmct.Button('Next 50')
        self.placeControl(self.next_button, 86, 3, 8, 14)
        self.connect(self.next_button, self.go_next)
        if self.search_button is not None:
            self.search_button.controlDown(self.prev_button)
            self.prev_button.controlUp(self.search_button)
        else:
            self.back_button.controlDown(self.prev_button)
            self.prev_button.controlUp(self.back_button)
        self.prev_button.controlDown(self.next_button)
        self.prev_button.controlRight(self.results_list)
        self.next_button.controlUp(self.prev_button)
        self.next_button.controlRight(self.results_list)

    def handle_select(self, item):
        data = (item or {}).get('data') or {}
        if data.get('page') == 'prev':
            self.go_previous()
            return
        if data.get('page') == 'next':
            self.go_next()
            return
        _open_station_sources(item)

    def go_previous(self):
        if self.offset <= 0:
            notify('Already on the first page.')
            return
        self.goto_page(max(0, self.offset - PAGE_SIZE))

    def go_next(self):
        if not self.page.get('has_more'):
            notify('No more stations.')
            return
        self.goto_page(self.offset + PAGE_SIZE)

    def goto_page(self, offset):
        name = self.country.get('name') or 'stations'
        page = busy_fetch(
            lambda: load_station_page(self.country, offset, self.query),
            'Loading %s...' % name
        )
        if page is None:
            return
        if not page.get('stations'):
            notify('No stations on that page.')
            return
        self.page = page
        self.offset = int(page.get('offset') or 0)
        self.all_items = station_page_items(self.country, page)
        self.populate_list()
        self.status_label.setLabel(page_status(self.country, page))
        focus_index = 1 if self.offset > 0 else 0
        try:
            self.results_list.selectItem(focus_index)
        except Exception:
            pass
        self.setFocus(self.results_list)

    def search_items(self):
        keyboard = xbmc.Keyboard(self.query, self.search_heading)
        keyboard.doModal()
        if not keyboard.isConfirmed():
            return
        self.query = _safe_search(keyboard.getText())
        self.goto_page(0)


def _open_station_sources(item):
    station = item.get('data') or {}
    streams = fmstream.playable_streams(station)
    title = station.get('name') or 'Station'
    if not streams:
        notify('No playable streams for that station.')
        return

    total = len(streams)
    items = [
        stream_item(stream, station, index, total)
        for index, stream in enumerate(streams, start=1)
    ]
    window = SportsBrowseWindow(
        heading=title.upper(),
        status_text='%s sources  |  Select a source to play.' % total,
        items=items,
        on_select=_play_stream_item,
        art_path=world_radio_art(),
        empty_title=title,
        empty_meta='Select a source',
        empty_overview='Highlight a stream, then select it to play.',
        allow_search=False,
        list_heading='SOURCES'
    )
    window.doModal()
    del window


def _play_stream_item(item):
    data = item.get('data') or {}
    url = (data.get('url') or '').strip()
    title = data.get('title') or 'World Radio'
    if not url:
        notify('That source has no stream URL.')
        return
    player.play_audio(title, url)


def musical_movies_art(focused=False):
    selected = paths.MUSICAL_MOVIES_FOCUS_PATH
    normal = paths.MUSICAL_MOVIES_PATH
    if focused and os.path.exists(selected):
        return selected
    if os.path.exists(normal):
        return normal
    return paths.ICON_PATH


def open_musical_movies():
    from resources.lib.gui.movies import open_musical_movies_window
    open_musical_movies_window()


HUB_OPTIONS = (
    {
        'key': 'radio',
        'caption': 'WORLD RADIO',
        'title': 'World Radio',
        'meta': 'Countries  |  Stations  |  Streams',
        'overview': (
            'Browse live radio stations from around the world. Pick a country, '
            'choose a station, then select a stream to play.'
        ),
        'art': world_radio_art,
        'action': None,
    },
    {
        'key': 'musicals',
        'caption': 'MUSICAL MOVIES',
        'title': 'Musical Movies',
        'meta': 'Musicals  |  Movie page  |  Play',
        'overview': (
            'Browse films classed as Music / Musical. Select a movie to open the same '
            'movie page used in Movies & Shows, then get links and play.'
        ),
        'art': musical_movies_art,
        'action': None,
    },
    {
        'key': 'podcasts',
        'caption': 'PODCASTS',
        'title': 'Podcasts',
        'meta': 'Trending  |  Genre  |  Episodes  |  Search',
        'overview': (
            'Browse trending podcasts, pick a genre, play trending episodes, or search for a show. '
            'Select a podcast to page through episodes, then play.'
        ),
        'art': podcast_art,
        'action': None,
    },
    {
        'key': 'mp3',
        'caption': 'MP3',
        'title': 'MP3',
        'meta': 'Albums  |  Tracks  |  A-Z  |  Search',
        'overview': (
            'Browse latest albums and tracks, search, or jump A-Z. '
            'Play a single song, or play a whole album so the next track starts on its own.'
        ),
        'art': mp3_art,
        'action': None,
    },
)


class MusicHubWindow(ColossusFullWindow):
    def __init__(self):
        super(MusicHubWindow, self).__init__('')
        self.option_images = {}
        self.option_buttons = {}
        self.option_captions = {}
        self.setup_canvas()
        self.set_controls()
        self.set_navigation()
        self.focus_world_radio()

    def onInit(self):
        self.focus_world_radio()

    def focus_world_radio(self):
        radio = self.option_buttons.get('radio')
        if radio is None:
            return
        try:
            self.setFocus(radio)
        except Exception:
            pass
        self.update_hub_preview()

    def set_controls(self):
        self.add_fanart(paths.BACKDROP_PATH or paths.FANART_PATH)

        self.back_button = pyxbmct.Button('Back')
        self.placeControl(self.back_button, 2, 2, 6, 10)
        self.connect(self.back_button, self.close)

        self.header_label = pyxbmct.Label(
            '[B]MUSIC[/B]',
            font='font13',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.header_label, 2, 14, 6, 30)

        self.status_label = pyxbmct.Label(
            'Choose World Radio, Musical Movies, Podcasts, or MP3.',
            font='font12',
            textColor='0xFFD0D6DE',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.status_label, 2, 46, 6, 50)

        self.poster = pyxbmct.Image(world_radio_art(focused=True), aspectRatio=0)
        self.placeControl(self.poster, 12, 3, 16, 16)

        self.title_label = pyxbmct.Label(
            '[B]World Radio[/B]',
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

        layouts = ((40, 5), (40, 28), (40, 51), (40, 74))
        actions = {
            'radio': open_world_radio,
            'musicals': open_musical_movies,
            'podcasts': open_podcasts,
            'mp3': open_mp3,
        }
        for option, (row, column) in zip(HUB_OPTIONS, layouts):
            art = option['art'](focused=(option['key'] == 'radio'))
            image = pyxbmct.Image(art if os.path.exists(art) else paths.ICON_PATH, aspectRatio=0)
            self.option_images[option['key']] = image
            self.placeControl(image, row, column, 40, 22, pad_x=0, pad_y=0)

            button = pyxbmct.Button('', noFocusTexture='', focusTexture='')
            self.option_buttons[option['key']] = button
            self.placeControl(button, row, column, 40, 22, pad_x=0, pad_y=0)
            self.connect(button, actions[option['key']])

            caption = pyxbmct.Label(
                '[COLOR aqua][B]%s[/B][/COLOR]' % option['caption'] if option['key'] == 'radio' else '[B]%s[/B]' % option['caption'],
                font='font13',
                textColor='0xFFFFFFFF',
                alignment=pyxbmct.ALIGN_CENTER
            )
            self.option_captions[option['key']] = caption
            self.placeControl(caption, 80, column, 6, 22)

    def set_navigation(self):
        radio = self.option_buttons['radio']
        musicals = self.option_buttons['musicals']
        podcasts = self.option_buttons['podcasts']
        mp3 = self.option_buttons['mp3']

        self.back_button.controlDown(radio)
        self.back_button.controlRight(radio)

        radio.controlUp(self.back_button)
        radio.controlRight(musicals)

        musicals.controlUp(self.back_button)
        musicals.controlLeft(radio)
        musicals.controlRight(podcasts)

        podcasts.controlUp(self.back_button)
        podcasts.controlLeft(musicals)
        podcasts.controlRight(mp3)

        mp3.controlUp(self.back_button)
        mp3.controlLeft(podcasts)

    def onAction(self, action):
        super(MusicHubWindow, self).onAction(action)
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


def open_music():
    window = MusicHubWindow()
    window.show()
    xbmc.sleep(50)
    window.focus_world_radio()
    window.doModal()
    del window
