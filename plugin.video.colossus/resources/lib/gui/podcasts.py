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
from resources.lib.sources.podbay import api as podbay
from resources.lib.sources.podbay.api import (
    CHART_PAGE_SIZE,
    EPISODE_PAGE_SIZE,
)


CACHE_TTL = 8 * 3600
CACHE_FOLDER = 'podbay'


def podcast_art(focused=False):
    selected = paths.PODCAST_FOCUS_PATH
    normal = paths.PODCAST_PATH
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


def load_genres():
    cached = _cache_get('genres.json')
    if cached:
        return cached
    genres = podbay.get_genres()
    if genres:
        _cache_set('genres.json', genres)
    return genres


def load_chart(slug, page=0, kind='podcasts'):
    cache_name = 'chart_%s_%s_%s.json' % (_safe_name(slug), kind, int(page or 0))
    cached = _cache_get(cache_name)
    if cached:
        return cached
    chart = podbay.get_chart(slug, page, kind)
    if chart and chart.get('items'):
        _cache_set(cache_name, chart)
    return chart


def load_podcast(slug='', page=0, feed_url='', itunes_id=''):
    cache_name = 'show_%s_%s_%s.json' % (
        _safe_name(slug or itunes_id or feed_url),
        _safe_name(itunes_id),
        int(page or 0)
    )
    cached = _cache_get(cache_name)
    if cached:
        return cached
    show = podbay.get_podcast(slug, page, feed_url, itunes_id)
    if show and show.get('episodes'):
        _cache_set(cache_name, show)
    return show


def load_search(query):
    return podbay.search(query)


def _podcast_overview(item):
    parts = [
        podbay.strip_html(item.get('description') or ''),
        'Author: %s' % item.get('author') if item.get('author') else '',
    ]
    return '\n'.join([part for part in parts if part]) or 'Select this podcast to browse episodes.'


def podcast_item(item, ranked=False):
    title = item.get('title') or 'Podcast'
    author = item.get('author') or ''
    number = item.get('number')
    label = title
    if ranked and number:
        label = '%s.  %s' % (number, title)
    meta_parts = [author]
    if item.get('explicit'):
        meta_parts.append('Explicit')
    count = item.get('episodeCount')
    if count:
        meta_parts.append('%s episodes' % count)
    return {
        'label': label,
        'title': title,
        'meta': '  |  '.join([part for part in meta_parts if part]),
        'overview': _podcast_overview(item),
        'search': ' '.join([title, author, item.get('slug') or '']),
        'data': {
            'kind': 'podcast',
            'slug': item.get('slug') or '',
            'feed_url': item.get('feed_url') or item.get('feedUrl') or '',
            'itunes_id': str(item.get('itunes_id') or item.get('collectionId') or ''),
            'title': title,
            'item': item,
        },
    }


def episode_item(item, show=None, ranked=False):
    show = show or item.get('podcast') or {}
    title = item.get('title') or 'Episode'
    show_title = show.get('title') or ''
    number = item.get('number')
    label = title
    if show_title:
        label = '%s  -  %s' % (show_title, title)
    if ranked and number:
        label = '%s.  %s' % (number, label)
    meta_parts = [
        show.get('author') or '',
        podbay.format_published(item.get('published')),
        podbay.format_duration(item.get('duration')),
    ]
    overview = podbay.strip_html(item.get('description') or item.get('descriptionText') or '')
    if not overview:
        overview = 'Play this episode.'
    return {
        'label': label,
        'title': title,
        'meta': '  |  '.join([part for part in meta_parts if part]),
        'overview': overview,
        'search': ' '.join([title, show_title, show.get('author') or '']),
        'data': {
            'kind': 'episode',
            'title': title,
            'show': show_title,
            'url': podbay.play_url(item),
            'slug': show.get('slug') or '',
            'feed_url': show.get('feed_url') or show.get('feedUrl') or '',
            'itunes_id': str(show.get('itunes_id') or show.get('collectionId') or ''),
        },
    }


def genre_item(genre):
    name = genre.get('name') or 'Genre'
    return {
        'label': name,
        'title': name,
        'meta': 'Trending podcasts and episodes',
        'overview': 'Open %s to browse trending podcasts, then select a show to play episodes.' % name,
        'search': '%s %s' % (name, genre.get('slug') or ''),
        'data': genre,
    }


def pager_item(kind, page, page_size, noun):
    if kind == 'prev':
        start = max(1, (page - 1) * page_size + 1)
        end = page * page_size
        return {
            'label': '[B]<< Previous %s[/B]' % page_size,
            'title': 'Previous %s' % page_size,
            'meta': '%s %s-%s' % (noun, start, end) if page else 'Previous page',
            'overview': 'Load the previous %s %s.' % (page_size, noun.lower()),
            'data': {'page': 'prev'},
        }
    start = page * page_size + 1
    end = (page + 1) * page_size
    return {
        'label': '[B]Next %s >>[/B]' % page_size,
        'title': 'Next %s' % page_size,
        'meta': '%s %s-%s' % (noun, start, end),
        'overview': 'Load the next %s %s.' % (page_size, noun.lower()),
        'data': {'page': 'next'},
    }


def chart_items(chart):
    kind = (chart or {}).get('kind') or 'podcasts'
    page = int((chart or {}).get('page') or 0)
    rows = (chart or {}).get('items') or []
    items = []
    if page > 0:
        items.append(pager_item('prev', page, CHART_PAGE_SIZE, 'Results'))
    for row in rows:
        if kind == 'episodes':
            items.append(episode_item(row, ranked=True))
        else:
            items.append(podcast_item(row, ranked=True))
    if chart.get('has_more'):
        items.append(pager_item('next', page + 1, CHART_PAGE_SIZE, 'Results'))
    return items


def chart_status(chart):
    rows = (chart or {}).get('items') or []
    page = int((chart or {}).get('page') or 0)
    start = page * CHART_PAGE_SIZE + 1 if rows else 0
    end = page * CHART_PAGE_SIZE + len(rows)
    noun = 'episodes' if chart.get('kind') == 'episodes' else 'podcasts'
    return '%s-%s  |  Select a %s.' % (start, end, noun[:-1] if end else noun)


def episode_page_items(show):
    page = int((show or {}).get('page') or 0)
    rows = (show or {}).get('episodes') or []
    podcast = (show or {}).get('podcast') or {}
    items = []
    if page > 0:
        items.append(pager_item('prev', page, EPISODE_PAGE_SIZE, 'Episodes'))
    for row in rows:
        items.append(episode_item(row, podcast))
    if show.get('has_more'):
        items.append(pager_item('next', page + 1, EPISODE_PAGE_SIZE, 'Episodes'))
    return items


def episode_status(show):
    rows = (show or {}).get('episodes') or []
    page = int((show or {}).get('page') or 0)
    total = int((show or {}).get('episode_count') or 0)
    start = page * EPISODE_PAGE_SIZE + 1 if rows else 0
    end = page * EPISODE_PAGE_SIZE + len(rows)
    if total:
        return '%s-%s of %s  |  Select an episode.' % (start, end, total)
    return '%s-%s  |  Select an episode.' % (start, end)


class PagedBrowseWindow(SportsBrowseWindow):
    def __init__(self, heading, status_text, items, empty_title, empty_meta, empty_overview, list_heading,
                 search_heading='', search_button_text='', allow_search=False):
        super(PagedBrowseWindow, self).__init__(
            heading=heading,
            status_text=status_text,
            items=items,
            on_select=self.handle_select,
            art_path=podcast_art(),
            empty_title=empty_title,
            empty_meta=empty_meta,
            empty_overview=empty_overview,
            allow_search=allow_search,
            search_heading=search_heading,
            search_button_text=search_button_text,
            list_heading=list_heading
        )
        self.prev_button = pyxbmct.Button(self.prev_label())
        self.placeControl(self.prev_button, 76, 3, 8, 14)
        self.connect(self.prev_button, self.go_previous)
        self.next_button = pyxbmct.Button(self.next_label())
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

    def prev_label(self):
        return 'Previous'

    def next_label(self):
        return 'Next'

    def handle_select(self, item):
        data = (item or {}).get('data') or {}
        if data.get('page') == 'prev':
            self.go_previous()
            return
        if data.get('page') == 'next':
            self.go_next()
            return
        self.select_row(item)

    def select_row(self, item):
        raise NotImplementedError

    def go_previous(self):
        raise NotImplementedError

    def go_next(self):
        raise NotImplementedError

    def replace_items(self, items, status_text, focus_index=0):
        self.all_items = items
        self.populate_list()
        self.status_label.setLabel(status_text)
        try:
            self.results_list.selectItem(min(focus_index, max(0, len(self.visible_items) - 1)))
        except Exception:
            pass
        self.setFocus(self.results_list)


class ChartBrowseWindow(PagedBrowseWindow):
    def __init__(self, chart):
        self.chart = chart or {}
        kind = self.chart.get('kind') or 'podcasts'
        heading = (self.chart.get('name') or 'Podcasts').upper()
        noun = 'episodes' if kind == 'episodes' else 'podcasts'
        super(ChartBrowseWindow, self).__init__(
            heading=heading,
            status_text=chart_status(self.chart),
            items=chart_items(self.chart),
            empty_title=self.chart.get('name') or 'Podcasts',
            empty_meta='Select a %s' % noun[:-1],
            empty_overview='Highlight a result, then select it. Use Next %s for more pages.' % CHART_PAGE_SIZE,
            list_heading=noun.upper(),
            allow_search=True,
            search_heading='Search podcast',
            search_button_text='Search podcast'
        )

    def prev_label(self):
        return 'Previous %s' % CHART_PAGE_SIZE

    def next_label(self):
        return 'Next %s' % CHART_PAGE_SIZE

    def select_row(self, item):
        _open_catalog_item(item)

    def search_items(self):
        _search_podcasts()

    def go_previous(self):
        page = int(self.chart.get('page') or 0)
        if page <= 0:
            notify('Already on the first page.')
            return
        self.goto_page(page - 1)

    def go_next(self):
        if not self.chart.get('has_more'):
            notify('No more results.')
            return
        self.goto_page(int(self.chart.get('page') or 0) + 1)

    def goto_page(self, page):
        name = self.chart.get('name') or 'podcasts'
        chart = busy_fetch(
            lambda: load_chart(self.chart.get('slug') or 'top', page, self.chart.get('kind') or 'podcasts'),
            'Loading %s...' % name
        )
        if chart is None:
            return
        if not chart.get('items'):
            notify('No results on that page.')
            return
        self.chart = chart
        focus_index = 1 if int(chart.get('page') or 0) > 0 else 0
        self.replace_items(chart_items(chart), chart_status(chart), focus_index)


class EpisodeBrowseWindow(PagedBrowseWindow):
    def __init__(self, show):
        self.show = show or {}
        podcast = self.show.get('podcast') or {}
        name = podcast.get('title') or 'Podcast'
        super(EpisodeBrowseWindow, self).__init__(
            heading=name.upper(),
            status_text=episode_status(self.show),
            items=episode_page_items(self.show),
            empty_title=name,
            empty_meta='Select an episode',
            empty_overview=podbay.strip_html(podcast.get('description') or '') or 'Select an episode to play.',
            list_heading='EPISODES'
        )

    def prev_label(self):
        return 'Previous %s' % EPISODE_PAGE_SIZE

    def next_label(self):
        return 'Next %s' % EPISODE_PAGE_SIZE

    def select_row(self, item):
        _open_catalog_item(item)

    def go_previous(self):
        page = int(self.show.get('page') or 0)
        if page <= 0:
            notify('Already on the first page.')
            return
        self.goto_page(page - 1)

    def go_next(self):
        if not self.show.get('has_more'):
            notify('No more episodes.')
            return
        self.goto_page(int(self.show.get('page') or 0) + 1)

    def goto_page(self, page):
        slug = self.show.get('slug') or (self.show.get('podcast') or {}).get('slug') or ''
        feed_url = self.show.get('feed_url') or (self.show.get('podcast') or {}).get('feed_url') or ''
        itunes_id = self.show.get('itunes_id') or (self.show.get('podcast') or {}).get('itunes_id') or ''
        name = (self.show.get('podcast') or {}).get('title') or 'podcast'
        show = busy_fetch(
            lambda: load_podcast(slug, page, feed_url, itunes_id),
            'Loading %s...' % name
        )
        if show is None:
            return
        if not show.get('episodes'):
            notify('No episodes on that page.')
            return
        self.show = show
        focus_index = 1 if int(show.get('page') or 0) > 0 else 0
        self.replace_items(episode_page_items(show), episode_status(show), focus_index)


def _open_catalog_item(item):
    data = (item or {}).get('data') or {}
    kind = data.get('kind')
    if kind == 'episode':
        _play_episode(data)
        return
    if kind == 'podcast':
        _open_podcast(
            data.get('slug') or '',
            data.get('title') or 'Podcast',
            data.get('feed_url') or '',
            data.get('itunes_id') or ''
        )
        return


def _open_podcast(slug, title, feed_url='', itunes_id=''):
    if not slug and not feed_url and not itunes_id:
        notify('That podcast has no listing.')
        return
    show = busy_fetch(
        lambda: load_podcast(slug, 0, feed_url, itunes_id),
        'Loading %s...' % title
    )
    if show is None:
        return
    if not show.get('episodes'):
        notify('No episodes found for %s.' % title)
        return
    window = EpisodeBrowseWindow(show)
    window.doModal()
    del window


def _play_episode(data):
    url = (data.get('url') or '').strip()
    title = data.get('title') or 'Podcast'
    if not url:
        _open_podcast(
            data.get('slug') or '',
            data.get('show') or title,
            data.get('feed_url') or '',
            data.get('itunes_id') or ''
        )
        return
    player.play_audio(
        title,
        url,
        headers={
            'User-Agent': podbay.USER_AGENT,
            'Referer': podbay.REFERER,
            'Accept': '*/*',
        },
        artist=data.get('show') or 'Podcasts'
    )


def _open_chart(slug, kind, heading):
    chart = busy_fetch(lambda: load_chart(slug, 0, kind), 'Loading %s...' % heading)
    if chart is None:
        return
    if not chart.get('items'):
        notify('Nothing found in %s.' % heading)
        return
    chart['name'] = heading
    window = ChartBrowseWindow(chart)
    window.doModal()
    del window


def _open_genres():
    genres = busy_fetch(load_genres, 'Loading genres...')
    if genres is None:
        return
    if not genres:
        notify('No genres found.')
        return
    items = [genre_item(genre) for genre in genres]
    window = SportsBrowseWindow(
        heading='GENRES',
        status_text='%s genres  |  Select a genre.' % len(items),
        items=items,
        on_select=_open_genre,
        art_path=podcast_art(),
        empty_title='Genres',
        empty_meta='Choose a genre',
        empty_overview='Highlight a genre, then select it to load trending podcasts.',
        allow_search=True,
        search_heading='Search genre',
        search_button_text='Search genre',
        list_heading='GENRES'
    )
    window.doModal()
    del window


def _open_genre(item):
    genre = item.get('data') or {}
    name = genre.get('name') or 'Genre'
    slug = genre.get('slug') or ''
    _open_chart(slug, 'podcasts', name)


class RemoteSearchBrowseWindow(SportsBrowseWindow):
    def search_items(self):
        _search_podcasts()


def _search_podcasts():
    keyboard = xbmc.Keyboard('', 'Search podcast')
    keyboard.doModal()
    if not keyboard.isConfirmed():
        return
    query = (keyboard.getText() or '').strip()
    if not query:
        return
    results = busy_fetch(lambda: load_search(query), 'Searching...')
    if results is None:
        return
    items = [podcast_item(row) for row in results.get('podcasts') or []]
    items.extend(episode_item(row) for row in results.get('episodes') or [])
    if not items:
        notify('No matches for %s.' % query)
        return
    window = RemoteSearchBrowseWindow(
        heading='SEARCH',
        status_text='%s results for %s  |  Select an item.' % (len(items), query),
        items=items,
        on_select=_open_catalog_item,
        art_path=podcast_art(),
        empty_title=query,
        empty_meta='Search results',
        empty_overview='Podcasts open episode lists. Episodes play directly.',
        allow_search=True,
        search_heading='Search podcast',
        search_button_text='Search podcast',
        list_heading='RESULTS'
    )
    window.doModal()
    del window


def _open_section(item):
    key = ((item or {}).get('data') or {}).get('key')
    if key == 'trending':
        _open_chart('top', 'podcasts', 'Trending')
        return
    if key == 'genres':
        _open_genres()
        return
    if key == 'episodes':
        _open_chart('top', 'episodes', 'Trending episodes')


def open_podcasts():
    items = [
        {
            'label': 'Trending',
            'title': 'Trending',
            'meta': 'Most popular podcasts right now',
            'overview': 'Open the current trending podcast chart, then select a show to browse episodes.',
            'data': {'key': 'trending'},
        },
        {
            'label': 'Genre',
            'title': 'Genre',
            'meta': 'Comedy, news, true crime, and more',
            'overview': 'Pick a genre, then browse its trending podcasts a page at a time.',
            'data': {'key': 'genres'},
        },
        {
            'label': 'Trending episodes',
            'title': 'Trending episodes',
            'meta': 'Popular episodes you can play now',
            'overview': 'Browse trending episodes and play one directly.',
            'data': {'key': 'episodes'},
        },
    ]
    window = RemoteSearchBrowseWindow(
        heading='PODCASTS',
        status_text='Trending, Genre, or Trending episodes  |  Search from the button.',
        items=items,
        on_select=_open_section,
        art_path=podcast_art(),
        empty_title='Podcasts',
        empty_meta='Choose a section',
        empty_overview='Trending and Genre open podcast charts. Trending episodes play audio. Use Search podcast to find a show.',
        allow_search=True,
        search_heading='Search podcast',
        search_button_text='Search podcast',
        list_heading='BROWSE'
    )
    window.doModal()
    del window
