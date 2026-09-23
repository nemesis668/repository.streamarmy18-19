from __future__ import absolute_import

import json
import os
import time

import pyxbmct
import xbmc
import xbmcgui

from resources.lib.core import paths
from resources.lib.core import player
from resources.lib.gui.sports import SportsBrowseWindow, busy_fetch, notify
from resources.lib.sources.mp3lib import api as mp3lib
from resources.lib.sources.mp3lib.api import CATEGORIES, LETTERS, PAGE_SIZE


CACHE_TTL = 8 * 3600
CACHE_FOLDER = 'mp3lib'


def mp3_art(focused=False):
    selected = paths.MP3_FOCUS_PATH
    normal = paths.MP3_PATH
    if focused and os.path.exists(selected):
        return selected
    if os.path.exists(normal):
        return normal
    return paths.ICON_PATH


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


def _safe_name(value):
    return ''.join(ch if ch.isalnum() else '_' for ch in (value or ''))[:80]


def load_category(category_id, page=1):
    cache_name = 'cat_%s_%s.json' % (int(category_id), int(page or 1))
    cached = _cache_get(cache_name)
    if cached:
        return cached
    listing = mp3lib.get_category_page(category_id, page)
    if listing and listing.get('items'):
        _cache_set(cache_name, listing)
    return listing


def load_search(query, page=1):
    return mp3lib.search(query, page)


def load_letter(letter):
    cache_name = 'letter_%s.json' % _safe_name(letter)
    cached = _cache_get(cache_name)
    if cached:
        return cached
    items = mp3lib.get_letter_items(letter)
    if items:
        _cache_set(cache_name, items)
    return items


def load_release(post_id=None, link='', slug=''):
    cache_name = 'rel_%s.json' % _safe_name(str(post_id or slug or link))
    cached = _cache_get(cache_name)
    if cached:
        return cached
    release = mp3lib.get_release(post_id=post_id, link=link, slug=slug)
    if release and release.get('tracks'):
        _cache_set(cache_name, release)
    return release


def _play_headers(link):
    return {
        'User-Agent': mp3lib.USER_AGENT,
        'Referer': link or mp3lib.REFERER,
        'Accept': '*/*',
    }


def release_item(row):
    title = row.get('title') or 'Release'
    artist = row.get('artist') or ''
    date = row.get('date') or ''
    meta_parts = [part for part in (artist, date) if part]
    return {
        'label': title,
        'title': title,
        'meta': '  |  '.join(meta_parts) or 'Select to view tracks',
        'overview': 'Open this release to play a track, or play the whole album in order.',
        'search': ' '.join([title, artist, row.get('slug') or '']),
        'data': row,
    }


def pager_item(kind, page):
    if kind == 'prev':
        return {
            'label': '[B]<< Previous %s[/B]' % PAGE_SIZE,
            'title': 'Previous %s' % PAGE_SIZE,
            'meta': 'Page %s' % max(1, page - 1),
            'overview': 'Load the previous page.',
            'data': {'page': 'prev'},
        }
    return {
        'label': '[B]Next %s >>[/B]' % PAGE_SIZE,
        'title': 'Next %s' % PAGE_SIZE,
        'meta': 'Page %s' % (page + 1),
        'overview': 'Load the next page.',
        'data': {'page': 'next'},
    }


def listing_items(listing):
    page = int((listing or {}).get('page') or 1)
    rows = (listing or {}).get('items') or []
    items = []
    if page > 1:
        items.append(pager_item('prev', page))
    for row in rows:
        items.append(release_item(row))
    if listing.get('has_more'):
        items.append(pager_item('next', page))
    return items


def listing_status(listing, noun='releases'):
    rows = (listing or {}).get('items') or []
    page = int((listing or {}).get('page') or 1)
    total = int((listing or {}).get('total') or 0)
    start = (page - 1) * PAGE_SIZE + 1 if rows else 0
    end = (page - 1) * PAGE_SIZE + len(rows)
    if total:
        return '%s-%s of %s  |  Select a %s.' % (start, end, total, noun[:-1] if noun.endswith('s') else noun)
    return '%s %s  |  Select an item.' % (len(rows), noun)


class PagedListWindow(SportsBrowseWindow):
    def __init__(self, heading, listing, noun='releases', search_remote=False, search_heading='', query=''):
        self.listing = listing or {}
        self.noun = noun
        self.search_remote = search_remote
        self.query = query or ''
        super(PagedListWindow, self).__init__(
            heading=heading,
            status_text=listing_status(self.listing, noun),
            items=listing_items(self.listing),
            on_select=self.handle_select,
            art_path=mp3_art(),
            empty_title=heading.title(),
            empty_meta='Select a release',
            empty_overview='Highlight a release, then select it to view tracks. Use Play album to queue every song.',
            allow_search=True,
            search_heading=search_heading or 'Search music',
            search_button_text=search_heading or 'Search music',
            list_heading=noun.upper()
        )
        self.prev_button = pyxbmct.Button('Previous %s' % PAGE_SIZE)
        self.placeControl(self.prev_button, 76, 3, 8, 14)
        self.connect(self.prev_button, self.go_previous)
        self.next_button = pyxbmct.Button('Next %s' % PAGE_SIZE)
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
        _open_release(data)

    def search_items(self):
        if self.search_remote:
            _search_music()
            return
        super(PagedListWindow, self).search_items()

    def go_previous(self):
        raise NotImplementedError

    def go_next(self):
        raise NotImplementedError

    def replace_listing(self, listing):
        self.listing = listing or {}
        self.all_items = listing_items(self.listing)
        self.populate_list()
        self.status_label.setLabel(listing_status(self.listing, self.noun))
        focus_index = 1 if int(self.listing.get('page') or 1) > 1 else 0
        try:
            self.results_list.selectItem(min(focus_index, max(0, len(self.visible_items) - 1)))
        except Exception:
            pass
        self.setFocus(self.results_list)


class CategoryListWindow(PagedListWindow):
    def __init__(self, category, listing):
        self.category = category or {}
        super(CategoryListWindow, self).__init__(
            heading=(category.get('title') or 'MP3').upper(),
            listing=listing,
            noun='releases',
            search_remote=True,
            search_heading='Search music'
        )

    def go_previous(self):
        page = int(self.listing.get('page') or 1)
        if page <= 1:
            notify('Already on the first page.')
            return
        self.goto_page(page - 1)

    def go_next(self):
        if not self.listing.get('has_more'):
            notify('No more results.')
            return
        self.goto_page(int(self.listing.get('page') or 1) + 1)

    def goto_page(self, page):
        listing = busy_fetch(
            lambda: load_category(self.category.get('id'), page),
            'Loading %s...' % (self.category.get('title') or 'music')
        )
        if listing is None:
            return
        if not listing.get('items'):
            notify('No results on that page.')
            return
        self.replace_listing(listing)


class SearchListWindow(PagedListWindow):
    def __init__(self, listing):
        super(SearchListWindow, self).__init__(
            heading='SEARCH',
            listing=listing,
            noun='results',
            search_remote=True,
            search_heading='Search music',
            query=listing.get('query') or ''
        )

    def go_previous(self):
        page = int(self.listing.get('page') or 1)
        if page <= 1:
            notify('Already on the first page.')
            return
        self.goto_page(page - 1)

    def go_next(self):
        if not self.listing.get('has_more'):
            notify('No more results.')
            return
        self.goto_page(int(self.listing.get('page') or 1) + 1)

    def goto_page(self, page):
        listing = busy_fetch(
            lambda: load_search(self.query, page),
            'Searching...'
        )
        if listing is None:
            return
        if not listing.get('items'):
            notify('No results on that page.')
            return
        self.replace_listing(listing)


def _open_category(category):
    listing = busy_fetch(
        lambda: load_category(category.get('id'), 1),
        'Loading %s...' % (category.get('title') or 'music')
    )
    if listing is None:
        return
    if not listing.get('items'):
        notify('Nothing found.')
        return
    window = CategoryListWindow(category, listing)
    window.doModal()
    del window


def _open_letters():
    items = []
    for letter in LETTERS:
        items.append({
            'label': letter,
            'title': 'Letter %s' % letter,
            'meta': 'Browse titles starting with %s' % letter,
            'overview': 'Open titles filed under %s, then pick a release to play.' % letter,
            'data': {'letter': letter},
        })
    window = SportsBrowseWindow(
        heading='A-Z',
        status_text='Pick a letter.',
        items=items,
        on_select=_open_letter,
        art_path=mp3_art(),
        empty_title='A-Z',
        empty_meta='Choose a letter',
        empty_overview='Select a letter to browse matching albums and tracks.',
        allow_search=False,
        list_heading='LETTERS'
    )
    window.doModal()
    del window


def _open_letter(item):
    letter = ((item or {}).get('data') or {}).get('letter') or 'A'
    rows = busy_fetch(lambda: load_letter(letter), 'Loading %s...' % letter)
    if rows is None:
        return
    if not rows:
        notify('Nothing found for %s.' % letter)
        return
    items = [release_item(row) for row in rows]
    window = SportsBrowseWindow(
        heading='A-Z  %s' % letter,
        status_text='%s titles  |  Select a release.' % len(items),
        items=items,
        on_select=lambda chosen: _open_release(chosen.get('data') or {}),
        art_path=mp3_art(),
        empty_title=letter,
        empty_meta='Select a release',
        empty_overview='Select a release to view tracks. Use Play album to queue the whole album.',
        allow_search=True,
        search_heading='Search this letter',
        search_button_text='Search this letter',
        list_heading='TITLES'
    )
    window.doModal()
    del window


def _search_music():
    keyboard = xbmc.Keyboard('', 'Search music')
    keyboard.doModal()
    if not keyboard.isConfirmed():
        return
    query = (keyboard.getText() or '').strip()
    if not query:
        return
    listing = busy_fetch(lambda: load_search(query, 1), 'Searching...')
    if listing is None:
        return
    if not listing.get('items'):
        notify('No matches for %s.' % query)
        return
    window = SearchListWindow(listing)
    window.doModal()
    del window


def _open_release(row):
    title = (row or {}).get('title') or 'Release'
    release = busy_fetch(
        lambda: load_release(row.get('id'), row.get('link') or '', row.get('slug') or ''),
        'Loading %s...' % title
    )
    if release is None:
        return
    tracks = release.get('tracks') or []
    if not tracks:
        notify('No playable tracks found.')
        return
    window = TrackBrowseWindow(release, tracks)
    if len(tracks) == 1:
        window.play_index(0)
    window.doModal()
    del window


class TrackBrowseWindow(SportsBrowseWindow):
    def __init__(self, release, tracks):
        self.release = release or {}
        self.tracks = list(tracks or [])
        self.album_mode = len(self.tracks) > 1
        self.link = self.release.get('link') or ''
        self.base_status = (
            '%s tracks  |  Play album or pick a song.' % len(self.tracks)
            if self.album_mode else
            '1 track  |  Playing in the background. Use Stop to end it.'
        )
        items = []
        if self.album_mode:
            items.append({
                'label': '[B]Play album[/B]',
                'title': 'Play album',
                'meta': '%s tracks  |  Plays in order' % len(self.tracks),
                'overview': 'Play every track in order. Use Next song and Previous song to skip.',
                'data': {'kind': 'album'},
            })
        for index, track in enumerate(self.tracks, start=1):
            items.append({
                'label': '%s.  %s' % (index, track.get('title') or 'Track'),
                'title': track.get('title') or 'Track',
                'meta': '  |  '.join([part for part in (
                    track.get('artist'),
                    track.get('album'),
                    'Track %s of %s' % (index, len(self.tracks))
                ) if part]),
                'overview': 'Play this track. Stop ends playback. Next and Previous skip tracks in the album.',
                'data': {'kind': 'track', 'index': index - 1},
            })
        super(TrackBrowseWindow, self).__init__(
            heading=(self.release.get('title') or 'MP3').upper(),
            status_text=self.base_status,
            items=items,
            on_select=self.handle_select,
            art_path=mp3_art(),
            empty_title=self.release.get('title') or 'MP3',
            empty_meta=self.release.get('artist') or 'Select a track',
            empty_overview='Play album queues every song. Select a track to start from that song. Use Stop, Previous song, and Next song while music is playing.',
            allow_search=False,
            list_heading='TRACKS'
        )
        self.stop_button = pyxbmct.Button('Stop')
        self.placeControl(self.stop_button, 66, 3, 8, 14)
        self.connect(self.stop_button, self.stop_playback)
        self.prev_track_button = pyxbmct.Button('Previous song')
        self.placeControl(self.prev_track_button, 76, 3, 8, 14)
        self.connect(self.prev_track_button, self.previous_song)
        self.next_track_button = pyxbmct.Button('Next song')
        self.placeControl(self.next_track_button, 86, 3, 8, 14)
        self.connect(self.next_track_button, self.next_song)

        self.back_button.controlDown(self.stop_button)
        self.stop_button.controlUp(self.back_button)
        self.stop_button.controlDown(self.prev_track_button)
        self.stop_button.controlRight(self.results_list)
        self.prev_track_button.controlUp(self.stop_button)
        self.prev_track_button.controlDown(self.next_track_button)
        self.prev_track_button.controlRight(self.results_list)
        self.next_track_button.controlUp(self.prev_track_button)
        self.next_track_button.controlRight(self.results_list)
        self.results_list.controlLeft(self.stop_button)
        self.refresh_playback_controls()

    def handle_select(self, item):
        data = (item or {}).get('data') or {}
        if data.get('kind') == 'album':
            self.play_index(0)
            return
        if data.get('kind') == 'track':
            self.play_index(int(data.get('index') or 0))

    def play_index(self, index):
        if not self.tracks:
            notify('No playable tracks found.')
            return
        index = max(0, min(int(index or 0), len(self.tracks) - 1))
        headers = _play_headers(self.link)
        if self.album_mode:
            ok = player.play_audio_items(self.tracks, headers=headers, startpos=index)
            if not ok:
                notify('Could not start the album playlist.')
                return
        else:
            track = self.tracks[index]
            url = (track.get('url') or '').strip()
            if not url:
                notify('No playable tracks found.')
                return
            player.play_audio(
                track.get('title') or 'Track',
                url,
                headers=headers,
                artist=track.get('artist') or 'MP3'
            )
        xbmc.sleep(250)
        self.refresh_playback_controls()

    def stop_playback(self):
        player.stop_audio()
        xbmc.sleep(150)
        self.refresh_playback_controls()

    def next_song(self):
        if not player.is_playing_audio() or player.music_playlist_size() < 2:
            notify('Play the album to skip tracks.')
            return
        player.play_next_audio()
        xbmc.sleep(200)
        self.refresh_playback_controls()

    def previous_song(self):
        if not player.is_playing_audio() or player.music_playlist_size() < 2:
            notify('Play the album to skip tracks.')
            return
        player.play_previous_audio()
        xbmc.sleep(200)
        self.refresh_playback_controls()

    def refresh_playback_controls(self):
        playing = player.is_playing_audio()
        album_playing = playing and player.music_playlist_size() > 1
        try:
            self.stop_button.setVisible(playing)
            self.stop_button.setEnabled(playing)
        except Exception:
            pass
        try:
            self.prev_track_button.setVisible(album_playing)
            self.next_track_button.setVisible(album_playing)
            self.prev_track_button.setEnabled(album_playing)
            self.next_track_button.setEnabled(album_playing)
        except Exception:
            pass
        if playing:
            self.back_button.controlDown(self.stop_button)
            self.results_list.controlLeft(self.stop_button)
        else:
            self.back_button.controlDown(self.results_list)
            self.results_list.controlLeft(self.back_button)
        now_playing = ''
        if playing:
            try:
                tag = xbmc.Player().getMusicInfoTag()
                now_playing = (tag.getTitle() or '').strip()
            except Exception:
                now_playing = ''
        if now_playing:
            self.status_label.setLabel('Playing  %s  |  Stop  |  Previous  |  Next' % now_playing)
        else:
            self.status_label.setLabel(self.base_status)

    def onAction(self, action):
        action_id = action.getId() if hasattr(action, 'getId') else action
        if action_id == 13:
            self.stop_playback()
            return
        if action_id == 14:
            self.next_song()
            return
        if action_id == 15:
            self.previous_song()
            return
        super(TrackBrowseWindow, self).onAction(action)
        self.refresh_playback_controls()


class Mp3HomeWindow(SportsBrowseWindow):
    def search_items(self):
        _search_music()


def _open_section(item):
    key = ((item or {}).get('data') or {}).get('key')
    if key == 'az':
        _open_letters()
        return
    for category in CATEGORIES:
        if category['key'] == key:
            _open_category(category)
            return


def open_mp3():
    items = [
        {
            'label': 'Latest albums',
            'title': 'Latest albums',
            'meta': 'New full albums',
            'overview': 'Browse new albums a page at a time, then play a track or the whole album.',
            'data': {'key': 'albums'},
        },
        {
            'label': 'Latest tracks',
            'title': 'Latest tracks',
            'meta': 'New singles',
            'overview': 'Browse recently added singles and play them straight away.',
            'data': {'key': 'tracks'},
        },
        {
            'label': 'Old albums',
            'title': 'Old albums',
            'meta': 'Older full albums',
            'overview': 'Browse older albums, then play a track or queue the whole album.',
            'data': {'key': 'old'},
        },
        {
            'label': 'A-Z',
            'title': 'A-Z',
            'meta': 'Browse by letter',
            'overview': 'Pick a letter, then open a matching album or track.',
            'data': {'key': 'az'},
        },
    ]
    window = Mp3HomeWindow(
        heading='MP3',
        status_text='Albums, tracks, or A-Z  |  Search from the button.',
        items=items,
        on_select=_open_section,
        art_path=mp3_art(),
        empty_title='MP3',
        empty_meta='Choose a section',
        empty_overview='Open latest albums or tracks, browse A-Z, or search. Albums can play all songs in order.',
        allow_search=True,
        search_heading='Search music',
        search_button_text='Search music',
        list_heading='BROWSE'
    )
    window.doModal()
    del window
