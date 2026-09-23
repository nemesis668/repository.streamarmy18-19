from __future__ import absolute_import

import hashlib
import os
import random
import re
import threading
import time

import pyxbmct
import xbmc
import xbmcgui

from resources.lib.core import paths
from resources.lib.core import player
from resources.lib.gui.details import ColossusFullWindow
from resources.lib.sources.source2 import api as source2


HUB_OPTIONS = (
    {
        'key': 'live',
        'caption': 'LIVE SPORTS',
        'title': 'Live Sports',
        'meta': 'Categories  |  Live events  |  Sources',
        'overview': 'Browse live categories, pick an event, then choose a source to play. '
                    'This is the same Source Two flow used in SportsZone.',
        'art': lambda: paths.SPORTS_LIVE_PATH,
        'action': None,
    },
    {
        'key': 'upcoming',
        'caption': 'UPCOMING',
        'title': 'Upcoming Events',
        'meta': 'Scheduled matches  |  Sources when available',
        'overview': 'See what is coming up next. Select an event to view every available source.',
        'art': lambda: paths.SPORTS_UPCOMING_PATH,
        'action': None,
    },
    {
        'key': 'channels',
        'caption': '24/7 CHANNELS',
        'title': '24/7 Channels',
        'meta': 'Always on  |  Searchable channel list',
        'overview': 'Open the full 24/7 channel list, search for a channel, and play it with the required headers.',
        'art': lambda: paths.SPORTS_247_PATH,
        'action': None,
    },
)


def focus_texture():
    return os.path.join(
        os.path.dirname(pyxbmct.__file__),
        'textures',
        'estuary',
        'Button',
        'KeyboardKey.png'
    )


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
        xbmcgui.Dialog().ok(paths.ADDON_NAME, 'Request failed.\n%s' % holder['error'])
        return None
    return holder['data']


def notify(message):
    xbmcgui.Dialog().notification(paths.ADDON_NAME, message, paths.ICON_PATH, 3000)


SOURCE_ONE_LIVE_URL = 'https://streamed.pk/api/matches/live'
SOURCE_ONE_IMAGE_BASE = 'https://streamed.pk'


def _norm_title(text):
    text = (text or '').lower()
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    return ' '.join(text.split())


def _title_teams(text):
    normalized = re.sub(r'^(mlb|nfl|nba|nhl|wnba|mls)\s+', '', _norm_title(text))
    if ' vs ' not in normalized:
        return None
    left, right = normalized.split(' vs ', 1)
    left = left.strip()
    right = right.strip()
    if left and right:
        return (left, right)
    return None


def titles_match(left, right):
    a = _norm_title(left)
    b = _norm_title(right)
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    teams_a = _title_teams(left)
    teams_b = _title_teams(right)
    if teams_a and all(part in b for part in teams_a):
        return True
    if teams_b and all(part in a for part in teams_b):
        return True
    return False


def _poster_url(poster):
    poster = (poster or '').strip()
    if not poster:
        return ''
    if poster.startswith('http://') or poster.startswith('https://'):
        return poster
    if poster.startswith('/'):
        return SOURCE_ONE_IMAGE_BASE + poster
    return SOURCE_ONE_IMAGE_BASE + '/' + poster.lstrip('/')


LIVE_TILE_SIZE = (1100, 560)
LIVE_TILE_RADIUS = 64


def _rounded_mask(size, radius):
    from PIL import Image, ImageDraw
    width, height = size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    radius = max(1, min(int(radius), width // 2, height // 2))
    draw.rectangle([radius, 0, width - radius - 1, height - 1], fill=255)
    draw.rectangle([0, radius, width - 1, height - radius - 1], fill=255)
    draw.pieslice([0, 0, radius * 2, radius * 2], 180, 270, fill=255)
    draw.pieslice([width - radius * 2 - 1, 0, width - 1, radius * 2], 270, 360, fill=255)
    draw.pieslice([0, height - radius * 2 - 1, radius * 2, height - 1], 90, 180, fill=255)
    draw.pieslice([width - radius * 2 - 1, height - radius * 2 - 1, width - 1, height - 1], 0, 90, fill=255)
    return mask


def _decode_image_wic(path):
                                                                                
    if os.name != 'nt':
        return None
    import ctypes
    import uuid
    from ctypes import (
        HRESULT, POINTER, Structure, byref, c_double, c_ubyte, c_uint,
        c_void_p, c_wchar_p, windll, wintypes,
    )

    class GUID(Structure):
        _fields_ = [
            ('Data1', wintypes.DWORD),
            ('Data2', wintypes.WORD),
            ('Data3', wintypes.WORD),
            ('Data4', wintypes.BYTE * 8),
        ]

    def make_guid(text):
        value = uuid.UUID(text)
        data4 = (wintypes.BYTE * 8).from_buffer_copy(value.bytes[8:])
        return GUID(value.time_low, value.time_mid, value.time_hi_version, data4)

    def release(pointer):
        if not pointer:
            return
        table = ctypes.cast(pointer, POINTER(POINTER(c_void_p)))[0]
        ctypes.WINFUNCTYPE(ctypes.c_ulong, c_void_p)(table[2])(pointer)

    ole32 = windll.ole32
    started = ole32.CoInitialize(None)
    factory = c_void_p()
    decoder = c_void_p()
    frame = c_void_p()
    converter = c_void_p()
    try:
        result = ole32.CoCreateInstance(
            byref(make_guid('CACAF262-9370-4615-A13B-9F5539DA4C0A')),
            None,
            1,
            byref(make_guid('EC5EC8A9-C395-4314-9C77-54D7A935FF70')),
            byref(factory)
        )
        if result != 0 or not factory.value:
            return None
        factory_table = ctypes.cast(factory, POINTER(POINTER(c_void_p)))[0]
        create_decoder = ctypes.WINFUNCTYPE(
            HRESULT, c_void_p, c_wchar_p, c_void_p, wintypes.DWORD, c_uint, POINTER(c_void_p)
        )(factory_table[3])
        create_converter = ctypes.WINFUNCTYPE(
            HRESULT, c_void_p, POINTER(c_void_p)
        )(factory_table[10])
        if create_decoder(factory, path, None, 0x80000000, 1, byref(decoder)) != 0:
            return None
        decoder_table = ctypes.cast(decoder, POINTER(POINTER(c_void_p)))[0]
        get_frame = ctypes.WINFUNCTYPE(
            HRESULT, c_void_p, c_uint, POINTER(c_void_p)
        )(decoder_table[13])
        if get_frame(decoder, 0, byref(frame)) != 0:
            return None
        if create_converter(factory, byref(converter)) != 0:
            return None
        converter_table = ctypes.cast(converter, POINTER(POINTER(c_void_p)))[0]
        initialize = ctypes.WINFUNCTYPE(
            HRESULT, c_void_p, c_void_p, POINTER(GUID), c_uint, c_void_p, c_double, c_uint
        )(converter_table[8])
        pixel_format = make_guid('6FDDC324-4E03-4BFE-B185-3D77768DC90F')
        if initialize(converter, frame, byref(pixel_format), 0, None, 0.0, 0) != 0:
            return None
        get_size = ctypes.WINFUNCTYPE(
            HRESULT, c_void_p, POINTER(c_uint), POINTER(c_uint)
        )(converter_table[3])
        width = c_uint()
        height = c_uint()
        if get_size(converter, byref(width), byref(height)) != 0 or not width.value or not height.value:
            return None
        copy_pixels = ctypes.WINFUNCTYPE(
            HRESULT, c_void_p, c_void_p, c_uint, c_uint, POINTER(c_ubyte)
        )(converter_table[7])
        stride = width.value * 4
        raw = (c_ubyte * (stride * height.value))()
        if copy_pixels(converter, None, stride, stride * height.value, raw) != 0:
            return None
        from PIL import Image
        image = Image.frombuffer('RGBA', (width.value, height.value), bytes(raw), 'raw', 'BGRA', 0, 1)
        image.load()
        return image
    except Exception:
        return None
    finally:
        release(converter)
        release(frame)
        release(decoder)
        release(factory)
        if started == 0:
            ole32.CoUninitialize()


def _open_rgba(path):
    from PIL import Image
    try:
        return Image.open(path).convert('RGBA')
    except Exception:
        decoded = _decode_image_wic(path)
        if decoded is None:
            raise
        return decoded


def _round_live_poster(src_path, dest_path):
    try:
        from PIL import Image, ImageChops
    except ImportError:
        return ''
    try:
        source = _open_rgba(src_path)
        tile_w, tile_h = LIVE_TILE_SIZE
        scale = max(float(tile_w) / source.size[0], float(tile_h) / source.size[1])
        resized = source.resize(
            (max(1, int(source.size[0] * scale)), max(1, int(source.size[1] * scale))),
            Image.LANCZOS
        )
        left = max(0, (resized.size[0] - tile_w) // 2)
        top = max(0, (resized.size[1] - tile_h) // 2)
        cropped = resized.crop((left, top, left + tile_w, top + tile_h))
        mask = _rounded_mask((tile_w, tile_h), LIVE_TILE_RADIUS)
        cropped.putalpha(ImageChops.multiply(cropped.split()[-1], mask))
        cropped.save(dest_path, 'PNG')
        return dest_path
    except Exception:
        return ''


def _cache_live_poster(url, title, timeout=5):
    if not url:
        return ''
    cache_dir = os.path.join(paths.PROFILE_PATH, 'live_now')
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    digest = hashlib.md5((title + '|' + url).encode('utf-8')).hexdigest()
    extension = os.path.splitext(url.split('?')[0])[1] or '.webp'
    poster_file = os.path.join(cache_dir, digest + extension)
    tile_file = os.path.join(cache_dir, digest + '_tile.png')
    if os.path.exists(tile_file) and os.path.getsize(tile_file) > 1000:
        return tile_file
    if not os.path.exists(poster_file) or os.path.getsize(poster_file) <= 1000:
        import requests
        try:
            requests.packages.urllib3.disable_warnings()
        except Exception:
            pass
        response = requests.get(
            url,
            timeout=timeout,
            verify=False,
            headers={'User-Agent': 'Colossus/0.1', 'Accept': 'image/*,*/*'}
        )
        response.raise_for_status()
        with open(poster_file, 'wb') as handle:
            handle.write(response.content)
    rounded = _round_live_poster(poster_file, tile_file)
    return rounded or poster_file


def _fetch_source_one_live(timeout=5):
    import requests
    try:
        requests.packages.urllib3.disable_warnings()
    except Exception:
        pass
    response = requests.get(
        SOURCE_ONE_LIVE_URL,
        timeout=timeout,
        verify=False,
        headers={'User-Agent': 'Colossus/0.1', 'Accept': 'application/json'}
    )
    response.raise_for_status()
    data = response.json()
    return data if isinstance(data, list) else []


LIVE_NOW_TIMEOUT = 7


def load_live_now_event(timeout=LIVE_NOW_TIMEOUT):
                                                                              
    holder = {'result': None}

    def worker():
        try:
            holder['result'] = _load_live_now_event_inner(timeout)
        except Exception:
            holder['result'] = None

    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    thread.join(max(1.0, float(timeout)))
    return holder.get('result')


def _load_live_now_event_inner(timeout):
    deadline = time.time() + max(1.0, float(timeout))

    def remaining():
        return max(0.8, deadline - time.time())

    try:
        live_rows = _fetch_source_one_live(timeout=min(4.0, remaining()))
    except Exception:
        return None
    if not live_rows or time.time() >= deadline:
        return None
    try:
        events = source2.get_live_sports_events(
            source2.BASE_URL,
            'Live Sports',
            timeout=min(4.0, remaining()),
            allow_proxy=False,
        )
    except Exception:
        return None
    if not events or time.time() >= deadline:
        return None

    matched = []
    for row in live_rows:
        poster = _poster_url(row.get('poster'))
        if not poster:
            continue
        title = row.get('title') or ''
        for event in events:
            if not titles_match(title, event.get('title') or ''):
                continue
            item = dict(event)
            item['poster_url'] = poster
            item['popular'] = bool(row.get('popular'))
            item['live_title'] = title
            matched.append(item)
            break

    if not matched:
        return None
    popular = [item for item in matched if item.get('popular')]
    chosen = random.choice(popular or matched)
    chosen['poster'] = _cache_live_poster(
        chosen.get('poster_url'),
        chosen.get('live_title') or chosen.get('title') or 'live',
        timeout=min(3.0, remaining())
    )
    chosen['poster_rounded'] = bool(chosen.get('poster') and chosen['poster'].endswith('_tile.png'))
    return chosen if chosen.get('poster') else None


def open_event_sources(event):
    _open_event_sources({'data': event or {}})


def category_item(title, url, count):
    return {
        'label': '%s    (%s)' % (title, count),
        'title': title,
        'meta': '%s live events' % count,
        'overview': 'Open %s to view live and scheduled events, then choose a source to play.' % title,
        'data': {'title': title, 'url': url, 'count': count},
    }


def event_item(event):
    title = event.get('title') or 'Event'
    event_time = event.get('time') or ''
    category = event.get('cat') or ''
    channels = event.get('channels') or []
    label = '%s    %s' % (event_time, title) if event_time else title
    meta_parts = [part for part in (event_time, category, '%s sources' % len(channels)) if part]
    return {
        'label': label,
        'title': title,
        'meta': '   |   '.join(meta_parts),
        'overview': 'Select this event to see every available source, then play one.',
        'data': event,
    }


def channel_item(channel, meta='24/7 channel', overview=None):
    title = channel.get('title') or 'Channel'
    return {
        'label': title,
        'title': title,
        'meta': meta,
        'overview': overview or 'Play this channel now. Colossus will resolve the stream and start playback.',
        'data': channel,
    }


def _select_live_sports_item(item):
    data = item.get('data') or {}
    if data.get('type') == 'daddylive_event':
        _open_event_sources(item)
        return
    _open_live_category(item)


def _search_live_events(query, cache):
    query = (query or '').strip().lower()
    if not query:
        return None
    if cache.get('items') is None:
        events = busy_fetch(
            lambda: source2.get_live_sports_events(source2.BASE_URL, 'Live Sports'),
            'Searching events...'
        )
        if events is None:
            return None
        cache['items'] = [event_item(event) for event in events]
    matched = []
    for item in cache['items']:
        event = item.get('data') or {}
        channels = ' '.join(channel.get('title') or '' for channel in (event.get('channels') or []))
        haystack = ' '.join([
            item.get('title') or '',
            item.get('label') or '',
            event.get('time') or '',
            event.get('cat') or '',
            channels,
        ]).lower()
        if query in haystack:
            matched.append(item)
    return matched


def open_live_sports():
    categories = busy_fetch(source2.get_live_sports_categories, 'Loading Live Sports...')
    if categories is None:
        return
    if not categories:
        notify('No live sports found.')
        return

    items = []
    total = sum(int(item.get('count') or 0) for item in categories)
    items.append(category_item('All', source2.BASE_URL, total))
    for category in categories:
        title = category.get('title') or 'Category'
        count = int(category.get('count') or 0)
        items.append(category_item(title, category.get('url') or source2.BASE_URL, count))

    event_cache = {'items': None}
    window = SportsBrowseWindow(
        heading='LIVE SPORTS',
        status_text='%s categories  |  Select a category.' % len(items),
        items=items,
        on_select=_select_live_sports_item,
        art_path=paths.SPORTS_LIVE_PATH,
        empty_title='Live Sports',
        empty_meta='Choose a category',
        empty_overview='Highlight a category to preview it, then select it to load events.',
        allow_search=True,
        search_heading='Search events',
        list_heading='CATEGORIES',
        search_source=lambda query: _search_live_events(query, event_cache),
        search_list_heading='EVENTS'
    )
    window.doModal()
    del window


def _open_live_category(item):
    data = item.get('data') or {}
    title = data.get('title') or 'Live Sports'
    url = data.get('url') or source2.BASE_URL
    events = busy_fetch(
        lambda: source2.get_live_sports_events(url, category_title=title),
        'Loading %s...' % title
    )
    if events is None:
        return
    _open_event_list(title.upper(), events, paths.SPORTS_LIVE_PATH)


def open_upcoming_events():
    events = busy_fetch(source2.get_upcoming_events, 'Loading Upcoming Events...')
    if events is None:
        return
    _open_event_list('UPCOMING EVENTS', events, paths.SPORTS_UPCOMING_PATH)


def open_247_channels():
    channels = busy_fetch(source2.get_247_channels, 'Loading 24/7 Channels...')
    if channels is None:
        return
    if not channels:
        notify('No 24/7 channels found.')
        return

    items = [channel_item(channel) for channel in channels]
    window = SportsBrowseWindow(
        heading='24/7 CHANNELS',
        status_text='%s channels  |  Select a channel to play.' % len(items),
        items=items,
        on_select=_play_channel_item,
        art_path=paths.SPORTS_247_PATH,
        empty_title='24/7 Channels',
        empty_meta='Always on',
        empty_overview='Search or highlight a channel, then select it to play.',
        allow_search=True,
        search_heading='Search channels',
        list_heading='CHANNELS'
    )
    window.doModal()
    del window


def _open_event_list(heading, events, art_path):
    if not events:
        notify('No events found.')
        return

    items = [event_item(event) for event in events]
    window = SportsBrowseWindow(
        heading=heading,
        status_text='%s events  |  Select an event.' % len(items),
        items=items,
        on_select=_open_event_sources,
        art_path=art_path,
        empty_title=heading.title(),
        empty_meta='Select an event',
        empty_overview='Highlight an event to preview it, then select it to view sources.',
        allow_search=True,
        search_heading='Search events',
        list_heading='EVENTS'
    )
    window.doModal()
    del window


def _open_event_sources(item):
    event = item.get('data') or {}
    channels = event.get('channels') or []
    title = event.get('title') or 'Event'
    if not channels:
        notify('No sources found for that event.')
        return

    items = []
    total = len(channels)
    for index, channel in enumerate(channels, start=1):
        items.append(channel_item(
            channel,
            meta='Source %s of %s' % (index, total),
            overview='Play this source for %s.' % title
        ))

    window = SportsBrowseWindow(
        heading=title.upper(),
        status_text='%s sources  |  Select a source to play.' % total,
        items=items,
        on_select=_play_channel_item,
        art_path=event.get('poster') or paths.SPORTS_LIVE_PATH,
        empty_title=title,
        empty_meta='Select a source',
        empty_overview='Highlight a source, then select it to resolve and play.',
        allow_search=False,
        list_heading='SOURCES'
    )
    window.doModal()
    del window


def _play_channel_item(item):
    player.resolve_and_play(item.get('data') or {})


class SportsHubWindow(ColossusFullWindow):
    def __init__(self):
        super(SportsHubWindow, self).__init__('')
        self.option_images = {}
        self.option_buttons = {}
        self.option_captions = {}
        self.setup_canvas()
        self.set_controls()
        self.set_navigation()
        self.setFocus(self.option_buttons['live'])
        self.update_hub_preview()

    def set_controls(self):
        self.add_fanart(paths.BACKDROP_PATH or paths.FANART_PATH)

        self.back_button = pyxbmct.Button('Back')
        self.placeControl(self.back_button, 2, 2, 6, 10)
        self.connect(self.back_button, self.close)

        self.header_label = pyxbmct.Label(
            '[B]SPORTS[/B]',
            font='font13',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.header_label, 2, 14, 6, 30)

        self.status_label = pyxbmct.Label(
            'Choose Live Sports, Upcoming, or 24/7.',
            font='font12',
            textColor='0xFFD0D6DE',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.status_label, 2, 46, 6, 50)

        self.poster = pyxbmct.Image(paths.SPORTS_LIVE_PATH, aspectRatio=0)
        self.placeControl(self.poster, 12, 3, 16, 16)

        self.title_label = pyxbmct.Label(
            '[B]Live Sports[/B]',
            font='font30',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.title_label, 12, 22, 8, 74)

        self.meta_label = pyxbmct.Label(
            'Categories  |  Live events  |  Sources',
            font='font13',
            textColor='0xFFD0D6DE',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.meta_label, 20, 22, 5, 74)

        self.overview_box = pyxbmct.TextBox(font='font13', textColor='0xFFE8EEF4')
        self.placeControl(self.overview_box, 26, 22, 10, 74)
        self.overview_box.setText(HUB_OPTIONS[0]['overview'])

        layouts = ((40, 8), (40, 37), (40, 66))
        actions = {
            'live': open_live_sports,
            'upcoming': open_upcoming_events,
            'channels': open_247_channels,
        }
        for option, (row, column) in zip(HUB_OPTIONS, layouts):
            art = option['art']()
            image = pyxbmct.Image(art if os.path.exists(art) else paths.ICON_PATH, aspectRatio=0)
            self.option_images[option['key']] = image
            self.placeControl(image, row, column, 40, 26, pad_x=0, pad_y=0)

            button = pyxbmct.Button('', noFocusTexture='', focusTexture=focus_texture())
            self.option_buttons[option['key']] = button
            self.placeControl(button, row, column, 40, 26, pad_x=0, pad_y=0)
            self.connect(button, actions[option['key']])

            caption = pyxbmct.Label(
                '[B]%s[/B]' % option['caption'],
                font='font13',
                textColor='0xFFFFFFFF',
                alignment=pyxbmct.ALIGN_CENTER
            )
            self.option_captions[option['key']] = caption
            self.placeControl(caption, 80, column, 6, 26)

    def set_navigation(self):
        live = self.option_buttons['live']
        upcoming = self.option_buttons['upcoming']
        channels = self.option_buttons['channels']

        self.back_button.controlDown(live)
        self.back_button.controlRight(live)

        live.controlUp(self.back_button)
        live.controlRight(upcoming)

        upcoming.controlUp(self.back_button)
        upcoming.controlLeft(live)
        upcoming.controlRight(channels)

        channels.controlUp(self.back_button)
        channels.controlLeft(upcoming)

    def onAction(self, action):
        super(SportsHubWindow, self).onAction(action)
        self.update_hub_preview()

    def update_hub_preview(self):
        try:
            focused = self.getFocus()
        except Exception:
            return

        current = HUB_OPTIONS[0]
        for option in HUB_OPTIONS:
            caption = self.option_captions[option['key']]
            if focused == self.option_buttons[option['key']]:
                current = option
                caption.setLabel('[COLOR aqua][B]%s[/B][/COLOR]' % option['caption'])
            else:
                caption.setLabel('[B]%s[/B]' % option['caption'])

        art = current['art']()
        try:
            self.poster.setImage(art if os.path.exists(art) else paths.ICON_PATH)
        except Exception:
            pass
        self.title_label.setLabel('[B]%s[/B]' % current['title'])
        self.meta_label.setLabel(current['meta'])
        self.overview_box.setText(current['overview'])


class SportsBrowseWindow(ColossusFullWindow):
    def __init__(
        self,
        heading,
        status_text,
        items,
        on_select,
        art_path,
        empty_title,
        empty_meta,
        empty_overview,
        allow_search=False,
        search_heading='Search',
        search_button_text='Search',
        list_heading='RESULTS',
        search_source=None,
        search_list_heading='EVENTS'
    ):
        super(SportsBrowseWindow, self).__init__('')
        self.heading = heading
        self.status_text = status_text
        self.all_items = list(items or [])
        self.visible_items = list(self.all_items)
        self.on_select = on_select
        self.art_path = art_path if os.path.exists(art_path) else paths.ICON_PATH
        self.empty_title = empty_title
        self.empty_meta = empty_meta
        self.empty_overview = empty_overview
        self.allow_search = allow_search
        self.search_heading = search_heading
        self.search_button_text = search_button_text or 'Search'
        self.list_heading_text = list_heading
        self.search_source = search_source
        self.search_list_heading = search_list_heading or list_heading
        self.current_index = -1
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

        self.poster = pyxbmct.Image(self.art_path, aspectRatio=0)
        self.placeControl(self.poster, 12, 3, 48, 20)

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

        if self.allow_search:
            self.search_button = pyxbmct.Button(self.search_button_text)
            self.placeControl(self.search_button, 66, 3, 8, 18)
            self.connect(self.search_button, self.search_items)
        else:
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
        if self.search_button is not None:
            self.back_button.controlRight(self.search_button)
            self.back_button.controlDown(self.search_button)
        else:
            self.back_button.controlRight(self.results_list)
            self.back_button.controlDown(self.results_list)

        if self.search_button is not None:
            self.search_button.controlUp(self.back_button)
            self.search_button.controlLeft(self.back_button)
            self.search_button.controlRight(self.results_list)
            self.search_button.controlDown(self.results_list)
            self.results_list.controlLeft(self.search_button)
            self.results_list.controlUp(self.search_button)
        else:
            self.results_list.controlLeft(self.back_button)
            self.results_list.controlUp(self.back_button)

    def onAction(self, action):
        super(SportsBrowseWindow, self).onAction(action)
        self.update_preview()

    def populate_list(self, query=''):
        query = (query or '').strip().lower()
        self.results_list.reset()
        self.current_index = -1
        searched_events = False
        if query and self.search_source:
            found = self.search_source(query)
            if found is None:
                self.visible_items = list(self.all_items)
            else:
                self.visible_items = list(found)
                searched_events = True
        elif query:
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
        try:
            self.list_heading.setLabel(
                '[B]%s[/B]' % (self.search_list_heading if searched_events else self.list_heading_text)
            )
        except Exception:
            pass

        if not self.visible_items:
            self.results_list.addItem('No matches')
            self.status_label.setLabel('0 matches  |  Try another search.')
            self.title_label.setLabel('[B]No matches[/B]')
            self.meta_label.setLabel('')
            self.overview_box.setText('No items matched that search.')
            return

        for item in self.visible_items:
            self.results_list.addItem(item.get('label') or '')
        count_label = 'matches' if query else self.list_heading_text.lower()
        self.status_label.setLabel('%s %s  |  %s' % (
            len(self.visible_items),
            count_label,
            'Select an item.'
        ))
        self.update_preview(force=True)

    def search_items(self):
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
        try:
            self.poster.setImage(self.art_path)
        except Exception:
            pass


def open_sports():
    window = SportsHubWindow()
    window.doModal()
    del window
