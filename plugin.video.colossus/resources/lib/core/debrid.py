from __future__ import absolute_import

import json
import os
import time
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import xbmcaddon

from resources.lib.core import paths


RD_BASE_URL = 'https://api.real-debrid.com/rest/1.0'
RESOLVEURL_ID = 'script.module.resolveurl'
CACHE_SECONDS = 600
VIDEO_EXTENSIONS = (
    '.mkv', '.mp4', '.avi', '.mov', '.m4v', '.wmv', '.flv',
    '.mpg', '.mpeg', '.ts', '.m2ts', '.webm'
)


class DebridError(Exception):
    pass


def is_authorised():
    return bool(_setting('RealDebridResolver_token'))


def open_resolveurl_settings():
    import resolveurl
    resolveurl.display_settings()


def filter_cached_sources(sources):
    if not is_authorised():
        raise DebridError('Real-Debrid is not authorised in ResolveURL.')

    hashes = [source['info_hash'] for source in sources if source.get('info_hash')]
    availability = _load_cached_availability(hashes)
    cached_sources = []

    missing_hashes = [info_hash for info_hash in hashes if info_hash not in availability]
    sources_by_hash = dict((source.get('info_hash'), source) for source in sources if source.get('info_hash'))
    for info_hash in missing_hashes:
        availability[info_hash] = _is_cached(sources_by_hash[info_hash])

    _save_cached_availability(availability)

    for source in sources:
        if availability.get(source.get('info_hash')):
            source['cached'] = True
            cached_sources.append(source)

    return cached_sources


def resolve_magnet(magnet):
    if not is_authorised():
        raise DebridError('Real-Debrid is not authorised in ResolveURL.')

    from resolveurl.plugins.realdebrid import RealDebridResolver
    return RealDebridResolver().get_media_url('www.real-debrid.com', magnet, cached_only=False)


def _is_cached(source):
                                                                          
                                                                               
                                                                      
    torrent_id = ''
    try:
        torrent_id = _add_magnet(source['magnet'])
        torrent_info = _torrent_info(torrent_id)
        return _torrent_ready(torrent_info)
    finally:
        if torrent_id:
            try:
                _delete_torrent(torrent_id)
            except Exception:
                pass


def _request_json(url):
    request = Request(url, headers={
        'Authorization': 'Bearer %s' % _setting('RealDebridResolver_token'),
        'User-Agent': 'Colossus/0.0.1',
    })
    response = urlopen(request, timeout=20)
    return json.loads(response.read().decode('utf-8'))


def _post_json(path, data):
    return _request_json_with_retry(
        '%s/%s' % (RD_BASE_URL, path),
        data=urlencode(data).encode('utf-8'),
        method='POST'
    )


def _get_json(path):
    return _request_json_with_retry('%s/%s' % (RD_BASE_URL, path))


def _delete(path):
    return _request_json_with_retry('%s/%s' % (RD_BASE_URL, path), method='DELETE', allow_empty=True)


def _request_json_with_retry(url, data=None, method=None, allow_empty=False):
    try:
        return _request_json_request(url, data=data, method=method, allow_empty=allow_empty)
    except HTTPError as error:
        if error.code == 401 and _refresh_token():
            return _request_json_request(url, data=data, method=method, allow_empty=allow_empty)
        raise


def _request_json_request(url, data=None, method=None, allow_empty=False):
    request = Request(url, data=data, method=method, headers={
        'Authorization': 'Bearer %s' % _setting('RealDebridResolver_token'),
        'User-Agent': 'Colossus/0.0.1',
    })
    if data:
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    response = urlopen(request, timeout=25)
    payload = response.read().decode('utf-8')
    if allow_empty and not payload:
        return {}
    return json.loads(payload) if payload else {}


def _add_magnet(magnet):
    response = _post_json('torrents/addMagnet', {'magnet': magnet})
    torrent_id = response.get('id', '')
    if not torrent_id:
        raise DebridError('Real-Debrid did not accept the magnet.')
    return torrent_id


def _torrent_info(torrent_id):
    return _get_json('torrents/info/%s' % torrent_id)


def _delete_torrent(torrent_id):
    return _delete('torrents/delete/%s' % torrent_id)


def _torrent_ready(torrent_info):
    if not torrent_info or torrent_info.get('error'):
        return False
    status = torrent_info.get('status')
    if status not in ('downloaded', 'waiting_files_selection'):
        return False
    files = torrent_info.get('files') or []
    if not files:
        return bool(torrent_info.get('links'))
    return any(_is_video_file(item.get('path', '')) for item in files)


def _is_video_file(path):
    lower_path = (path or '').lower()
    return any(lower_path.endswith(extension) for extension in VIDEO_EXTENSIONS)


def _refresh_token():
    try:
        from resolveurl.plugins.realdebrid import RealDebridResolver
        RealDebridResolver().refresh_token()
        return is_authorised()
    except Exception:
        return False


def _setting(setting_id):
    try:
        return xbmcaddon.Addon(id=RESOLVEURL_ID).getSetting(setting_id)
    except Exception:
        return ''


def _cache_file():
    cache_dir = os.path.join(paths.PROFILE_PATH, 'cache')
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return os.path.join(cache_dir, 'rd_availability.json')


def _load_cached_availability(hashes):
    try:
        with open(_cache_file(), 'r') as cache:
            payload = json.load(cache)
    except Exception:
        return {}

    now = int(time.time())
    availability = {}
    wanted = set([item.lower() for item in hashes])
    for info_hash, item in payload.items():
        if info_hash in wanted and now - int(item.get('timestamp', 0)) < CACHE_SECONDS:
            availability[info_hash] = bool(item.get('cached'))
    return availability


def _save_cached_availability(availability):
    now = int(time.time())
    payload = {}
    for info_hash, cached in availability.items():
        payload[info_hash.lower()] = {
            'cached': bool(cached),
            'timestamp': now,
        }
    with open(_cache_file(), 'w') as cache:
        json.dump(payload, cache)
