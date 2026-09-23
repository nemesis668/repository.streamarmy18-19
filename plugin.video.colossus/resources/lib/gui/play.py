from __future__ import absolute_import

import random

import requests
import xbmcgui
import xbmc

from resources.lib.core import paths


USER_AGENTS = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 '
    '(KHTML, like Gecko) Version/18.1 Safari/605.1.15',
)

DEFAULT_TIMEOUT = 20

api_url = 'https://api.framextv.tech/api/stream'

               


class ApiError(Exception):
    pass


def random_headers(extra_headers=None):
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': '*/*',
    }

    if extra_headers:
        headers.update(extra_headers)

    return headers


def request_type(media=None, media_type=None):
    if media_type:
        return media_type

    if media:
        if media.get('type'):
            return media.get('type')

        if media.get('media_type'):
            return media.get('media_type')

        if media.get('mediatype'):
            return media.get('mediatype')

    return 'movie'


def media_payload(media=None, media_type=None, media_id=None, extra=None, episode=None,
                  season=None, episode_number=None):
    payload = {}

    if extra:
        payload.update(extra)

    if 'type' not in payload:
        payload['type'] = request_type(
            media=media,
            media_type=media_type
        )

    if 'id' not in payload:
        resolved_id = media_id

        if resolved_id is None and media:
            resolved_id = media.get('id')

        if resolved_id not in (None, ''):
            payload['id'] = resolved_id

    if episode:
        if season is None:
            season = episode.get('season_number')

        if episode_number is None:
            episode_number = episode.get('episode_number')

    if season not in (None, ''):
        payload['season'] = season

    if episode_number not in (None, ''):
        payload['episode'] = episode_number

    return payload


def api_get(url, payload=None, params=None, extra_headers=None, timeout=DEFAULT_TIMEOUT,
            media=None, media_type=None, media_id=None):
    query = media_payload(
        media=media,
        media_type=media_type,
        media_id=media_id,
        extra=payload
    )

    if params:
        query.update(params)

    try:
        response = requests.get(
            url,
            params=query,
            headers=random_headers(extra_headers),
            timeout=timeout,
        )
        response.raise_for_status()
        return response
    except requests.RequestException as error:
        raise ApiError(str(error))


def api_post(url, payload=None, extra_headers=None, timeout=DEFAULT_TIMEOUT):
    try:
        response = requests.post(
            url,
            json=payload,
            headers=random_headers(extra_headers),
            timeout=timeout,
        )
        response.raise_for_status()
        return response
    except requests.RequestException as error:
        raise ApiError(str(error))


def api_get_json(url, payload=None, params=None, extra_headers=None, timeout=DEFAULT_TIMEOUT,
                 media=None, media_type=None, media_id=None):
    response = api_get(
        url,
        payload=payload,
        params=params,
        extra_headers=extra_headers,
        timeout=timeout,
        media=media,
        media_type=media_type,
        media_id=media_id,
    )

    try:
        return response.json()
    except ValueError as error:
        raise ApiError(str(error))


def quality_value(source):
    quality = str(source.get('quality') or '').lower()

    values = {
        '2160p': 2160,
        '1440p': 1440,
        '1080p': 1080,
        '720p': 720,
        '576p': 576,
        '480p': 480,
        '360p': 360,
        '240p': 240,
    }

    return values.get(quality, 0)


def open_play_window(media, episode=None):
    payload = media_payload(media, episode=episode)

    if payload.get('type') in ('movie', 'tv'):
        request_payload = {
            'type': payload.get('type'),
            'id': payload.get('id')
        }

        if payload.get('type') == 'tv':
            request_payload['season'] = payload.get('season')
            request_payload['episode'] = payload.get('episode')

        xbmcgui.Dialog().notification(
            paths.ADDON_NAME,
            'Getting links...',
            xbmcgui.NOTIFICATION_INFO,
            3000
        )

        get_sources = api_get_json(
            api_url,
            payload=request_payload
        )

        sources = get_sources.get('sources', [])

        if not sources:
            xbmcgui.Dialog().ok(
                paths.ADDON_NAME,
                'No playable sources found.'
            )
            return

        sources = sorted(
            sources,
            key=quality_value,
            reverse=True
        )

        xbmcgui.Dialog().notification(
            paths.ADDON_NAME,
            'Found %d links' % len(sources),
            xbmcgui.NOTIFICATION_INFO,
            3000
        )

        labels = []

        for index, source in enumerate(sources, 1):
            labels.append(
                'Link %d :: Quality %s' % (
                    index,
                    source.get('quality', 'Unknown')
                )
            )

        selected = xbmcgui.Dialog().select(
            'Select Stream',
            labels
        )

        if selected < 0:
            return

        source = sources[selected]

        stream_url = source.get('url')

        if not stream_url:
            xbmcgui.Dialog().ok(
                paths.ADDON_NAME,
                'Selected source has no URL.'
            )
            return

        source_headers = source.get('headers') or {}
        response_headers = get_sources.get('headers') or {}

        headers = {}

        if source_headers:
            headers.update(source_headers)

        if response_headers:
            headers.update(response_headers)

        if not headers:
            headers = random_headers()

        header_string = '&'.join(
            '%s=%s' % (key, value)
            for key, value in headers.items()
        )

        stream_url = '%s|%s' % (
            stream_url,
            header_string
        )

        xbmcgui.Dialog().notification(
            paths.ADDON_NAME,
            'Enjoy your stream!',
            xbmcgui.NOTIFICATION_INFO,
            3000
        )

        xbmc.Player().play(stream_url)

    else:
        xbmcgui.Dialog().ok(
            paths.ADDON_NAME,
            'Type: %s\nID: %s\nSeason: %s\nEpisode: %s' % (
                payload.get('type'),
                payload.get('id'),
                payload.get('season'),
                payload.get('episode')
            )
        )
