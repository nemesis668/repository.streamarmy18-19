from __future__ import absolute_import

import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from resources.lib.core import paths


TMDB_API_KEY = '5135334daa33251bc407e5f24cb1c6a5'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w500'
TMDB_BACKDROP_BASE = 'https://image.tmdb.org/t/p/w1280'
TMDB_PROFILE_BASE = 'https://image.tmdb.org/t/p/w185'
CAST_LIMIT = 8
MUSIC_GENRE_ID = 10402


class TmdbError(Exception):
    pass


def search(query):
    payload = _get_json('search/multi', {
        'query': query,
        'language': 'en-US',
        'include_adult': 'false',
        'page': '1',
    })
    return [
        _normalise(item)
        for item in payload.get('results', [])
        if item.get('media_type') in ('movie', 'tv')
    ]


def discover_movies(genre_id, page=1):
    payload = _get_json('discover/movie', {
        'language': 'en-US',
        'include_adult': 'false',
        'include_video': 'false',
        'sort_by': 'popularity.desc',
        'with_genres': str(genre_id),
        'page': str(max(1, int(page or 1))),
    })
    results = []
    for item in payload.get('results', []):
        item['media_type'] = 'movie'
        results.append(_normalise(item))
    return {
        'results': results,
        'page': int(payload.get('page') or page or 1),
        'total_pages': int(payload.get('total_pages') or 1),
        'total_results': int(payload.get('total_results') or 0),
    }


def search_movies(query, genre_id=None, page=1):
    payload = _get_json('search/movie', {
        'query': query,
        'language': 'en-US',
        'include_adult': 'false',
        'page': str(max(1, int(page or 1))),
    })
    results = []
    for item in payload.get('results', []):
        genre_ids = item.get('genre_ids') or []
        if genre_id and int(genre_id) not in [int(value) for value in genre_ids if value not in (None, '')]:
            continue
        item['media_type'] = 'movie'
        results.append(_normalise(item))
    return {
        'results': results,
        'page': int(payload.get('page') or page or 1),
        'total_pages': int(payload.get('total_pages') or 1),
        'total_results': int(payload.get('total_results') or 0),
    }


def details(media_type, tmdb_id):
    append = 'credits,content_ratings,videos' if media_type == 'tv' else 'credits,release_dates,videos'
    payload = _get_json('%s/%s' % (media_type, tmdb_id), {
        'language': 'en-US',
        'append_to_response': append,
    })
    payload['media_type'] = media_type
    return _normalise_details(payload)


def seasons(tv_id):
    payload = _get_json('tv/%s' % tv_id, {
        'language': 'en-US',
    })
    return _seasons_from_payload(payload, tv_id)


def episodes(tv_id, season_number):
    payload = _get_json('tv/%s/season/%s' % (tv_id, season_number), {
        'language': 'en-US',
    })
    items = []
    for episode in payload.get('episodes', []):
        still_path = episode.get('still_path') or ''
        episode_number = episode.get('episode_number')
        runtime = int(episode.get('runtime') or 0)
        items.append({
            'id': episode.get('id'),
            'tv_id': tv_id,
            'season_number': season_number,
            'episode_number': episode_number,
            'name': episode.get('name') or 'Episode %s' % episode_number,
            'overview': episode.get('overview') or '',
            'air_date': episode.get('air_date') or '',
            'runtime': runtime,
            'runtime_label': _format_runtime(runtime),
            'still': TMDB_IMAGE_BASE + still_path if still_path else '',
            'poster': TMDB_IMAGE_BASE + still_path if still_path else '',
        })
    return items


def _get_json(path, params):
    params = dict(params)
    params['api_key'] = TMDB_API_KEY
    url = '%s/%s?%s' % (TMDB_BASE_URL, path.lstrip('/'), urlencode(params))
    request = Request(url, headers={'User-Agent': 'Colossus/0.0.1'})
    response = urlopen(request, timeout=15)
    return json.loads(response.read().decode('utf-8'))


def _normalise(item):
    media_type = item.get('media_type')
    title = item.get('title') if media_type == 'movie' else item.get('name')
    date = item.get('release_date') if media_type == 'movie' else item.get('first_air_date')
    year = date[:4] if date else ''
    poster_path = item.get('poster_path') or ''
    backdrop_path = item.get('backdrop_path') or ''
    return {
        'id': item.get('id'),
        'title': title or 'Unknown',
        'media_type': media_type,
        'year': year,
        'overview': item.get('overview') or '',
        'poster': TMDB_IMAGE_BASE + poster_path if poster_path else '',
        'backdrop': TMDB_BACKDROP_BASE + backdrop_path if backdrop_path else '',
    }


def _normalise_details(item):
    media_type = item.get('media_type')
    tmdb_id = item.get('id')
    title = item.get('title') if media_type == 'movie' else item.get('name')
    date = item.get('release_date') if media_type == 'movie' else item.get('first_air_date')
    year = date[:4] if date else ''
    poster_path = item.get('poster_path') or ''
    backdrop_path = item.get('backdrop_path') or ''
    genres = [genre.get('name') for genre in item.get('genres') or [] if genre.get('name')]
    credits = item.get('credits') or {}
    cast = _cast_from_credits(credits, tmdb_id)
    runtime = _runtime_from_item(item, media_type)

    return {
        'id': tmdb_id,
        'title': title or 'Unknown',
        'media_type': media_type,
        'year': year,
        'tagline': item.get('tagline') or '',
        'overview': item.get('overview') or '',
        'genres': genres,
        'rating': item.get('vote_average') or 0,
        'votes': item.get('vote_count') or 0,
        'certification': _certification(item, media_type),
        'runtime': runtime,
        'runtime_label': _format_runtime(runtime),
        'creators': _creators(item, credits, media_type),
        'season_count': item.get('number_of_seasons') or 0,
        'episode_count': item.get('number_of_episodes') or 0,
        'poster': _cache_image(
            TMDB_IMAGE_BASE + poster_path if poster_path else '',
            'poster_%s_%s.jpg' % (media_type, tmdb_id)
        ),
        'backdrop': _cache_image(
            TMDB_BACKDROP_BASE + backdrop_path if backdrop_path else '',
            'backdrop_%s_%s.jpg' % (media_type, tmdb_id)
        ),
        'cast': cast,
        'seasons': _seasons_from_payload(item, tmdb_id) if media_type == 'tv' else [],
        'trailer_key': _trailer_key(item),
        'trailer_name': _trailer_name(item),
    }


def _seasons_from_payload(payload, tv_id):
    items = []
    for season in payload.get('seasons', []):
        season_number = season.get('season_number')
        if season_number == 0:
            continue
        poster_path = season.get('poster_path') or payload.get('poster_path') or ''
        items.append({
            'id': season.get('id'),
            'tv_id': tv_id,
            'season_number': season_number,
            'name': season.get('name') or 'Season %s' % season_number,
            'overview': season.get('overview') or '',
            'episode_count': season.get('episode_count') or 0,
            'poster': TMDB_IMAGE_BASE + poster_path if poster_path else '',
        })
    return items


def _cast_from_credits(credits, tmdb_id):
    items = []
    for person in (credits.get('cast') or [])[:CAST_LIMIT]:
        profile_path = person.get('profile_path') or ''
        person_id = person.get('id') or len(items)
        items.append({
            'id': person_id,
            'name': person.get('name') or '',
            'character': person.get('character') or '',
            'photo': _cache_image(
                TMDB_PROFILE_BASE + profile_path if profile_path else '',
                'cast_%s_%s.jpg' % (tmdb_id, person_id)
            ),
        })
    return items


def _creators(item, credits, media_type):
    if media_type == 'tv':
        names = [person.get('name') for person in item.get('created_by') or [] if person.get('name')]
        if names:
            return names
    names = []
    for person in credits.get('crew') or []:
        if person.get('job') == 'Director' and person.get('name'):
            names.append(person.get('name'))
    return names


def _runtime_from_item(item, media_type):
    if media_type == 'movie':
        return int(item.get('runtime') or 0)
    runtimes = item.get('episode_run_time') or []
    return int(runtimes[0]) if runtimes else 0


def _format_runtime(minutes):
    try:
        minutes = int(minutes or 0)
    except Exception:
        return ''
    if minutes <= 0:
        return ''
    hours, remaining = divmod(minutes, 60)
    if hours:
        return '%dh %02dm' % (hours, remaining)
    return '%dm' % minutes


def _certification(item, media_type):
    if media_type == 'tv':
        results = (item.get('content_ratings') or {}).get('results') or []
        return _preferred_value(results, 'rating')
    results = (item.get('release_dates') or {}).get('results') or []
    for country in ('US', 'GB'):
        for result in results:
            if result.get('iso_3166_1') != country:
                continue
            for release in result.get('release_dates') or []:
                certification = (release.get('certification') or '').strip()
                if certification:
                    return certification
    for result in results:
        for release in result.get('release_dates') or []:
            certification = (release.get('certification') or '').strip()
            if certification:
                return certification
    return ''


def _preferred_value(results, key):
    for country in ('US', 'GB'):
        for result in results:
            if result.get('iso_3166_1') == country and result.get(key):
                return result.get(key)
    for result in results:
        if result.get(key):
            return result.get(key)
    return ''


def _video_list(item):
    return (item.get('videos') or {}).get('results') or []


def _best_trailer(item):
    videos = [
        video for video in _video_list(item)
        if (video.get('site') or '').lower() == 'youtube' and video.get('key')
    ]
    trailers = [video for video in videos if (video.get('type') or '').lower() == 'trailer']
    teasers = [video for video in videos if (video.get('type') or '').lower() == 'teaser']
    official = [video for video in trailers if video.get('official')]
    chosen = official or trailers or teasers or videos
    return chosen[0] if chosen else {}


def _trailer_key(item):
    return _best_trailer(item).get('key') or ''


def _trailer_name(item):
    return _best_trailer(item).get('name') or 'Trailer'


def _cache_image(url, filename):
    if not url:
        return ''
    cache_dir = os.path.join(paths.PROFILE_PATH, 'tmdb_cache')
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    cache_file = os.path.join(cache_dir, filename)
    if os.path.exists(cache_file):
        return cache_file
    try:
        request = Request(url, headers={'User-Agent': 'Colossus/0.0.1'})
        response = urlopen(request, timeout=12)
        with open(cache_file, 'wb') as handle:
            handle.write(response.read())
        return cache_file
    except Exception:
        return url
