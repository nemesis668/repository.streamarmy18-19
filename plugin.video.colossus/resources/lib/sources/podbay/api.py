                                                            

from __future__ import absolute_import

import base64
import json
import re
from html import unescape

from resources.lib.core.remote import RemoteError, call


REFERER = 'https://podbay.fm/'
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
)
CHART_PAGE_SIZE = 20
EPISODE_PAGE_SIZE = 10
HTML_RE = re.compile(r'<[^>]+>')


class PodbayError(Exception):
    pass


def _run(name, *args, **kwargs):
    try:
        return call('podbay', name, list(args), kwargs)
    except RemoteError as exc:
        raise PodbayError(str(exc))


def _clean(value):
    if value is None:
        return ''
    text = unescape(str(value)).strip()
    if text.lower() in ('null', 'none'):
        return ''
    return text


def strip_html(value):
    text = HTML_RE.sub(' ', _clean(value))
    return ' '.join(text.split())


def format_duration(seconds):
    if isinstance(seconds, str) and ':' in seconds:
        return seconds.strip()
    try:
        total = int(float(seconds or 0))
    except (TypeError, ValueError):
        return ''
    if total <= 0:
        return ''
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return '%sh %sm' % (hours, minutes)
    if minutes:
        return '%sm' % minutes
    return '%ss' % secs


def format_published(value):
    text = _clean(value)
    if not text:
        return ''
    if 'T' in text:
        return text.split('T', 1)[0]
    parts = text.split()
    if len(parts) >= 4 and parts[1][:1].isalpha():
        return ' '.join(parts[:4])
    return text[:16]


def play_url(item):
    item = item or {}
    url = _clean(
        item.get('mediaURL')
        or item.get('enclosureUrl')
        or item.get('episodeUrl')
        or item.get('previewUrl')
    )
    if url:
        return url
    enclosure = item.get('enclosure') or {}
    if isinstance(enclosure, dict):
        return _clean(enclosure.get('url') or enclosure.get('href'))
    return _clean(enclosure)


def image_url(item):
    item = item or {}
    fallback = _clean(item.get('fallbackImage') or item.get('artworkUrl600') or item.get('artworkUrl100'))
    token = item.get('image') or ''
    if isinstance(token, dict):
        return _clean(token.get('url') or token.get('fallback') or fallback)
    token = _clean(token)
    if token.startswith('http://') or token.startswith('https://'):
        return token
    parts = token.split('.')
    if len(parts) < 2:
        return fallback
    payload = parts[1]
    payload += '=' * ((4 - len(payload) % 4) % 4)
    try:
        data = json.loads(base64.urlsafe_b64decode(payload.encode('ascii')))
    except Exception:
        return fallback
    return _clean(data.get('fallback') or data.get('url') or fallback)


def get_genres():
    return _run('get_genres')


def get_chart(slug='top', page=0, kind='podcasts'):
    return _run('get_chart', slug, page, kind)


def get_podcast(slug='', page=0, feed_url='', itunes_id=''):
    return _run('get_podcast', slug=slug, page=page, feed_url=feed_url, itunes_id=itunes_id)


def search(query):
    return _run('search', query)
