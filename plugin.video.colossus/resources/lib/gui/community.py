from __future__ import absolute_import

import json
import os
import re
import threading
from urllib.parse import urlparse

import pyxbmct
import requests
import xbmc
import xbmcgui

from resources.lib.core import paths
from resources.lib.core import player
from resources.lib.core.presence import user_id as device_user_id
from resources.lib.gui.details import ColossusFullWindow
from resources.lib.gui.sports import SportsBrowseWindow


FEED_URL = 'https://nemzzy.info/colossus/community'
COMMUNITY_PAGE = 'https://nemzzy.info/community'
COMMUNITY_QR_PATH = os.path.join(paths.MEDIA_PATH, 'community_qr.png')
FAV_PATH = os.path.join(paths.PROFILE_PATH, 'community_favs.json')
DIRECT_VIDEO = ('.mp4', '.m3u8')
DIRECT_AUDIO = ('.mp3',)
DIRECT_PLAYLIST = ('.m3u',)
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
)


def kodi_colour(text):
    return re.sub(r'\[COLOR\s*=\s*', '[COLOR ', text or '', flags=re.I)


def plain_title(text):
    text = kodi_colour(text)
    text = re.sub(r'\[/?COLOR[^\]]*\]', '', text, flags=re.I)
    text = re.sub(r'\[/?(?:B|I|CR|UPPERCASE)\]', '', text, flags=re.I)
    return ' '.join(text.replace('\n', ' ').split()) or 'Community'


def safe_image(url):
    url = (url or '').strip()
    if url.startswith('https://') or url.startswith('http://'):
        return url
    return paths.ICON_PATH


def media_kind(url):
    path = urlparse(url or '').path.lower()
    if path.endswith(DIRECT_AUDIO):
        return 'audio'
    if path.endswith('.m3u8'):
        return 'video'
    if path.endswith(DIRECT_PLAYLIST):
        return 'video'
    if path.endswith(DIRECT_VIDEO):
        return 'video'
    return ''


def host_name(url):
    host = (urlparse(url).netloc or '').lower()
    if host.startswith('www.'):
        host = host[4:]
    return host or 'Link'


def item_links(item):
    raw = item.get('links')
    if isinstance(raw, str):
        raw = [raw]
    if not isinstance(raw, list):
        return []
    links = []
    for link in raw:
        if isinstance(link, dict):
            url = str(link.get('url') or '').strip()
            label = str(link.get('label') or '').strip()
        else:
            url = str(link or '').strip()
            label = ''
        if url:
            links.append({'url': url, 'label': label})
    return links


class CommunityWindow(SportsBrowseWindow):
    def set_controls(self):
        super(CommunityWindow, self).set_controls()
        try:
            self.removeControl(self.poster)
        except Exception:
            try:
                self.poster.setVisible(False)
            except Exception:
                pass
        self.poster = pyxbmct.Image(paths.ICON_PATH, aspectRatio=2)
        self.placeControl(self.poster, 12, 3, 48, 20)

    def populate_list(self, query=''):
        super(CommunityWindow, self).populate_list(query)
        if not self.visible_items:
            try:
                self.poster.setImage(paths.ICON_PATH)
            except Exception:
                pass

    def update_preview(self, force=False):
        previous = self.current_index
        super(CommunityWindow, self).update_preview(force=force)
        if not self.visible_items:
            try:
                self.poster.setImage(paths.ICON_PATH)
            except Exception:
                pass
            return
        if not force and self.current_index == previous:
            return
        if self.current_index < 0 or self.current_index >= len(self.visible_items):
            return
        image = self.visible_items[self.current_index].get('image') or paths.ICON_PATH
        try:
            self.poster.setImage(image)
        except Exception:
            pass


def load_favs():
    try:
        if not os.path.exists(FAV_PATH):
            return []
        with open(FAV_PATH, 'r', encoding='utf-8') as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            return []
        return [str(item) for item in data if str(item)]
    except Exception:
        return []


def save_favs(ids):
    try:
        folder = os.path.dirname(FAV_PATH)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
        with open(FAV_PATH, 'w', encoding='utf-8') as handle:
            json.dump(ids, handle)
    except Exception:
        pass


def list_id(item):
    return str(((item or {}).get('data') or {}).get('id') or '')


class CommunityListsWindow(CommunityWindow):
    def __init__(self, items, on_select):
        self.fav_ids = set(load_favs())
        self.favs_only = False
        super(CommunityListsWindow, self).__init__(
            heading='COMMUNITY LISTS',
            status_text='%s lists  |  Select a list.' % len(items or []),
            items=items,
            on_select=on_select,
            art_path=paths.ICON_PATH,
            empty_title='Community Lists',
            empty_meta='',
            empty_overview='Highlight a list and press Favourite to save it. Favourites shows only the lists you saved.',
            allow_search=False,
            list_heading='LISTS',
        )

    def set_controls(self):
        super(CommunityListsWindow, self).set_controls()
        self.fav_button = pyxbmct.Button('Favourite')
        self.placeControl(self.fav_button, 62, 3, 8, 20)
        self.connect(self.fav_button, self.toggle_favourite)
        self.vote_button = pyxbmct.Button('Upvote')
        self.placeControl(self.vote_button, 70, 3, 8, 20)
        self.connect(self.vote_button, self.upvote_current)
        self.filter_button = pyxbmct.Button('Favourites')
        self.placeControl(self.filter_button, 78, 3, 8, 20)
        self.connect(self.filter_button, self.toggle_filter)
        self.create_button = pyxbmct.Button('Create a list')
        self.placeControl(self.create_button, 86, 3, 8, 20)
        self.connect(self.create_button, self.open_create)

    def set_navigation(self):
        self.back_button.controlDown(self.fav_button)
        self.back_button.controlRight(self.results_list)
        self.fav_button.controlUp(self.back_button)
        self.fav_button.controlDown(self.vote_button)
        self.fav_button.controlRight(self.results_list)
        self.vote_button.controlUp(self.fav_button)
        self.vote_button.controlDown(self.filter_button)
        self.vote_button.controlRight(self.results_list)
        self.filter_button.controlUp(self.vote_button)
        self.filter_button.controlDown(self.create_button)
        self.filter_button.controlRight(self.results_list)
        self.create_button.controlUp(self.filter_button)
        self.create_button.controlRight(self.results_list)
        self.results_list.controlLeft(self.fav_button)
        self.results_list.controlUp(self.back_button)

    def _is_fav(self, item):
        return list_id(item) in self.fav_ids

    def _current_item(self):
        if not self.visible_items:
            return None
        index = self.current_index
        if index < 0 or index >= len(self.visible_items):
            try:
                index = self.results_list.getSelectedPosition()
            except Exception:
                return None
        if index < 0 or index >= len(self.visible_items):
            return None
        return self.visible_items[index]

    def populate_list(self, query=''):
        chosen = list(self.all_items)
        if self.favs_only:
            chosen = [item for item in chosen if self._is_fav(item)]
        for item in chosen:
            title = item.get('title') or ''
            item['label'] = ('[COLOR FF7EE0FF]*[/COLOR]  %s' % title) if self._is_fav(item) else title
        saved = self.all_items
        self.all_items = chosen
        try:
            super(CommunityListsWindow, self).populate_list('')
        finally:
            self.all_items = saved
        if self.favs_only and not chosen:
            self.results_list.reset()
            self.results_list.addItem('No favourites yet')
            self.visible_items = []
            self.current_index = -1
            self.status_label.setLabel('No favourite lists yet.')
            self.title_label.setLabel('[B]No favourites[/B]')
            self.meta_label.setLabel('')
            self.overview_box.setText('Highlight a list and press Favourite. Then press Favourites to see only those lists.')
            try:
                self.poster.setImage(paths.ICON_PATH)
            except Exception:
                pass
        elif self.favs_only:
            self.status_label.setLabel('%s favourites  |  Select a list.' % len(chosen))
        try:
            self.list_heading.setLabel('[B]%s[/B]' % ('FAVOURITES' if self.favs_only else 'LISTS'))
        except Exception:
            pass
        self.filter_button.setLabel('All lists' if self.favs_only else 'Favourites')
        self._sync_fav_button()
        self._sync_vote_button()

    def update_preview(self, force=False):
        super(CommunityListsWindow, self).update_preview(force=force)
        item = self._current_item()
        if item and self._is_fav(item):
            text = item.get('overview') or ''
            self.overview_box.setText(text + '\n\nIn your favourites.')
        self._sync_fav_button()
        self._sync_vote_button()

    def _sync_fav_button(self):
        item = self._current_item()
        self.fav_button.setLabel('Unfavourite' if item and self._is_fav(item) else 'Favourite')

    def _sync_vote_button(self):
        item = self._current_item()
        self.vote_button.setLabel('Upvoted' if item and item.get('voted') else 'Upvote')

    def toggle_favourite(self):
        item = self._current_item()
        ident = list_id(item)
        if not ident:
            notify('Highlight a list first.')
            return
        favs = load_favs()
        if ident in favs:
            favs = [entry for entry in favs if entry != ident]
            notify('Removed from favourites.')
        else:
            favs.append(ident)
            notify('Added to favourites.')
        save_favs(favs)
        self.fav_ids = set(favs)
        self.populate_list()
        self.setFocus(self.results_list)

    def upvote_current(self):
        item = self._current_item()
        ident = list_id(item)
        if not ident:
            notify('Highlight a list first.')
            return
        if item.get('voted'):
            notify('You have already upvoted this list.')
            return
        result = busy_fetch(lambda: cast_vote(ident), 'Sending vote...')
        if not isinstance(result, dict):
            return
        data = item.get('data') or {}
        data['votes'] = int(result.get('votes') or 0)
        data['voted'] = True
        item['data'] = data
        item['voted'] = True
        item['meta'] = list_meta(data)
        self.all_items.sort(
            key=lambda row: (
                int((row.get('data') or {}).get('pinned') or 0),
                int((row.get('data') or {}).get('votes') or 0),
            ),
            reverse=True,
        )
        notify('Upvoted.')
        self.populate_list()
        for index, row in enumerate(self.visible_items):
            if list_id(row) == ident:
                try:
                    self.results_list.selectItem(index)
                except Exception:
                    pass
                break
        self.setFocus(self.results_list)

    def toggle_filter(self):
        self.favs_only = not self.favs_only
        self.populate_list()
        self.setFocus(self.results_list)

    def open_create(self):
        window = CreateListWindow()
        window.doModal()
        del window


class CreateListWindow(ColossusFullWindow):
    def __init__(self):
        super(CreateListWindow, self).__init__('')
        self.setup_canvas()
        self.set_controls()
        self.setFocus(self.back_button)

    def set_controls(self):
        self.add_fanart(paths.BACKDROP_PATH or paths.FANART_PATH)
        self.back_button = pyxbmct.Button('Back')
        self.placeControl(self.back_button, 4, 4, 8, 14)
        self.connect(self.back_button, self.close)
        self.back_button.controlRight(self.back_button)
        self.back_button.controlDown(self.back_button)

        qr_path = COMMUNITY_QR_PATH if os.path.exists(COMMUNITY_QR_PATH) else paths.ICON_PATH
        self.qr_image = pyxbmct.Image(qr_path, aspectRatio=2)
        self.placeControl(self.qr_image, 18, 8, 64, 30)

        self.message_box = pyxbmct.TextBox(font='font13', textColor='0xFFFFFFFF')
        self.placeControl(self.message_box, 28, 42, 40, 50)
        self.message_box.setText(
            'Would you like to make your own lists that will appear in this addon?\n\n'
            'Scan the QR code or visit %s to get started.' % COMMUNITY_PAGE
        )


def notify(message):
    xbmcgui.Dialog().notification(paths.ADDON_NAME, message, paths.ICON_PATH, 3000)


def busy_fetch(func, message):
    progress = xbmcgui.DialogProgress()
    progress.create(paths.ADDON_NAME, message)
    holder = {'data': None, 'error': None, 'done': False}

    def worker():
        try:
            holder['data'] = func()
        except Exception as exc:
            holder['error'] = exc
        holder['done'] = True

    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    while not holder['done']:
        if progress.iscanceled():
            try:
                progress.close()
            except Exception:
                pass
            return None
        xbmc.sleep(80)
    try:
        progress.close()
    except Exception:
        pass
    if holder['error'] is not None:
        xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Could not load community lists.\n%s' % holder['error'])
        return None
    return holder['data']


def cast_vote(list_id):
    response = requests.post(
        FEED_URL + '/vote',
        json={'list_id': int(list_id), 'voter_id': device_user_id()},
        timeout=20,
        headers={'User-Agent': 'Colossus', 'Accept': 'application/json'},
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError('Vote was not accepted.')
    return payload


def fetch_lists():
    response = requests.get(
        FEED_URL,
        params={'voter': device_user_id()},
        timeout=25,
        headers={'User-Agent': 'Colossus', 'Accept': 'application/json'},
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        return []
    lists = payload.get('lists') or []
    return lists if isinstance(lists, list) else []


def list_meta(entry):
    items = entry.get('items') if isinstance(entry.get('items'), list) else []
    owner = (entry.get('owner') or '').strip()
    count = '%s item' % len(items) if len(items) == 1 else '%s items' % len(items)
    votes = int(entry.get('votes') or 0)
    vote_text = '1 vote' if votes == 1 else '%s votes' % votes
    return '  |  '.join([part for part in (owner, count, vote_text) if part])


def list_row(entry):
    title = kodi_colour(entry.get('title') or 'Untitled list')
    return {
        'label': title,
        'title': title,
        'meta': list_meta(entry),
        'overview': 'Select this list to browse its items.',
        'image': safe_image(entry.get('image')),
        'voted': bool(entry.get('voted')),
        'data': entry,
    }


def content_row(item):
    title = kodi_colour(item.get('title') or 'Untitled')
    links = item_links(item)
    if len(links) == 1:
        meta = '1 link'
    else:
        meta = '%s links' % len(links)
    description = (item.get('description') or '').strip() or 'No description.'
    return {
        'label': title,
        'title': title,
        'meta': meta,
        'overview': description,
        'image': safe_image(item.get('image')),
        'links': links,
        'plain': plain_title(title),
    }


def open_window(heading, status_text, items, on_select, empty_title, empty_overview, list_heading, allow_search=False):
    window = CommunityWindow(
        heading=heading,
        status_text=status_text,
        items=items,
        on_select=on_select,
        art_path=paths.ICON_PATH,
        empty_title=empty_title,
        empty_meta='',
        empty_overview=empty_overview,
        allow_search=allow_search,
        search_heading='Search',
        list_heading=list_heading,
    )
    window.doModal()
    del window


def play_direct(title, url, kind):
    label = plain_title(title)
    if kind == 'audio':
        header_string = player.encode_headers({
            'User-Agent': USER_AGENT,
            'Accept': '*/*',
        })
        path = '%s|%s' % (url, header_string) if header_string else url
        list_item = xbmcgui.ListItem(label=label, path=path)
        list_item.setInfo('music', {'title': label})
        list_item.setProperty('IsPlayable', 'true')
        xbmc.Player().play(path, list_item, False)
        return
    player.play_stream(label, url)


def play_link(title, url):
    url = (url or '').strip()
    if not url:
        notify('That item has no link.')
        return
    kind = media_kind(url)
    if kind:
        play_direct(title, url, kind)
        return

    progress = xbmcgui.DialogProgressBG()
    progress.create(paths.ADDON_NAME, 'Resolving link...')
    try:
        import resolveurl
        hosted = resolveurl.HostedMediaFile(url=url)
        if not hosted:
            raise RuntimeError('ResolveURL does not support that link.')
        resolved = hosted.resolve()
        if isinstance(resolved, dict):
            resolved = resolved.get('url') or ''
        resolved = str(resolved or '').strip()
        if not resolved.startswith('http'):
            raise RuntimeError('ResolveURL did not return a stream.')
    except Exception as exc:
        xbmc.log('[Colossus] Community resolve failed: %s' % exc, xbmc.LOGINFO)
        xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Could not play that link.\n%s' % exc)
        return
    finally:
        try:
            progress.close()
        except Exception:
            pass
    play_direct(title, resolved, media_kind(resolved) or 'video')


def open_sources(row):
    links = row.get('links') or []
    sources = []
    for index, link in enumerate(links):
        url = link.get('url') or ''
        host = host_name(url)
        label = (link.get('label') or '').strip()
        sources.append({
            'label': kodi_colour(label) if label else 'Source %s    %s' % (index + 1, host),
            'title': row.get('title') or 'Sources',
            'meta': plain_title(label) if label else host,
            'overview': row.get('overview') or '',
            'image': row.get('image') or paths.ICON_PATH,
            'url': url,
            'plain': row.get('plain') or plain_title(row.get('title')),
        })
    open_window(
        'SOURCES',
        '%s sources  |  Select one to play.' % len(sources),
        sources,
        lambda source: play_link(source.get('plain'), source.get('url')),
        plain_title(row.get('title')),
        row.get('overview') or 'Choose a source.',
        'SOURCES',
    )


def open_item(row):
    links = row.get('links') or []
    if not links:
        notify('That item has no link.')
        return
    if len(links) == 1:
        play_link(row.get('plain'), links[0].get('url'))
        return
    open_sources(row)


def open_list(row):
    entry = row.get('data') or {}
    items = entry.get('items') if isinstance(entry.get('items'), list) else []
    rows = [content_row(item) for item in items]
    if not rows:
        notify('That list has no items yet.')
        return
    title = plain_title(entry.get('title') or 'Community list')
    open_window(
        title,
        '%s items  |  Select one to play.' % len(rows),
        rows,
        open_item,
        title,
        'Highlight an item to see its image and description. Select it to play.',
        'ITEMS',
        allow_search=True,
    )


def open_community():
    lists = busy_fetch(fetch_lists, 'Loading community lists...')
    if lists is None:
        return
    rows = [list_row(entry) for entry in lists if isinstance(entry, dict)]
    if not rows:
        notify('No community lists have been approved yet.')
        return
    window = CommunityListsWindow(rows, open_list)
    window.doModal()
    del window
