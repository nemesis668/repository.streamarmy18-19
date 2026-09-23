from __future__ import absolute_import

from urllib.parse import quote

import xbmc
import xbmcgui

from resources.lib.core import paths
from resources.lib.sources.source2 import api as source2


def log(message):
    xbmc.log('[Colossus] %s' % message, xbmc.LOGINFO)


def encode_headers(headers):
    parts = []
    for key, value in (headers or {}).items():
        if value is None or value == '':
            continue
        parts.append('%s=%s' % (key, quote(str(value), safe='')))
    return '&'.join(parts)


def stream_looks_live(play_url, headers=None, timeout=6):
    if not play_url:
        return False
    try:
        import requests
        req_headers = {'User-Agent': source2.USER_AGENT, 'Accept': '*/*'}
        if headers:
            req_headers.update(headers)
        response = requests.get(
            play_url,
            timeout=timeout,
            headers=req_headers,
            stream=True,
            verify=False
        )
        try:
            if response.status_code != 200:
                return False
            if '.m3u8' not in play_url.lower():
                return True
            text = ''
            for chunk in response.iter_content(chunk_size=2048):
                if chunk:
                    text += chunk.decode('utf-8', 'ignore')
                if len(text) > 4096:
                    break
            return '#EXTM3U' in text
        finally:
            response.close()
    except Exception as exc:
        log('Stream check failed: %s' % exc)
        return False


def _inputstream_available():
    try:
        return xbmc.getCondVisibility('System.HasAddon(inputstream.adaptive)') == 1
    except Exception:
        return False


def play_audio(title, url, headers=None, artist=None):
    headers = dict(headers or {})
    if not headers.get('User-Agent') and not headers.get('user-agent'):
        headers['User-Agent'] = source2.USER_AGENT
    if not headers.get('Accept'):
        headers['Accept'] = '*/*'
    if not headers.get('Referer'):
        headers['Referer'] = 'https://fmstream.org/'
    if not headers.get('Icy-MetaData'):
        headers['Icy-MetaData'] = '1'

    header_string = encode_headers(headers)
    play_path = '%s|%s' % (url, header_string) if header_string else url
    lowered = (url or '').lower()
    is_hls = '.m3u8' in lowered
    is_dash = '.mpd' in lowered
    use_isa = (is_hls or is_dash) and _inputstream_available()
    item_path = url if use_isa else play_path

    log('Playing radio %s via %s' % (title, 'inputstream.adaptive' if use_isa else 'default player'))
    list_item = xbmcgui.ListItem(label=title, path=item_path)
    list_item.setInfo('music', {'title': title, 'artist': artist or 'World Radio'})
    list_item.setInfo('video', {'title': title, 'mediatype': 'music'})
    list_item.setProperty('IsPlayable', 'true')
    try:
        list_item.setContentLookup(False)
    except Exception:
        pass

    if is_hls:
        list_item.setMimeType('application/vnd.apple.mpegurl')
        if use_isa:
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            list_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            if header_string:
                list_item.setProperty('inputstream.adaptive.stream_headers', header_string)
                list_item.setProperty('inputstream.adaptive.manifest_headers', header_string)
                list_item.setProperty('inputstream.adaptive.common_headers', header_string)
    elif is_dash:
        list_item.setMimeType('application/dash+xml')
        if use_isa:
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            list_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            if header_string:
                list_item.setProperty('inputstream.adaptive.stream_headers', header_string)
                list_item.setProperty('inputstream.adaptive.manifest_headers', header_string)
                list_item.setProperty('inputstream.adaptive.common_headers', header_string)

    xbmc.Player().play(item_path, list_item, False)


def play_audio_items(tracks, headers=None, startpos=0):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    playlist.clear()
    count = 0
    for track in tracks or []:
        url = (track.get('url') or '').strip()
        title = track.get('title') or 'Track'
        if not url:
            continue
        item_headers = dict(headers or track.get('headers') or {})
        if not item_headers.get('User-Agent') and not item_headers.get('user-agent'):
            item_headers['User-Agent'] = source2.USER_AGENT
        if not item_headers.get('Accept'):
            item_headers['Accept'] = '*/*'
        header_string = encode_headers(item_headers)
        play_path = '%s|%s' % (url, header_string) if header_string else url
        list_item = xbmcgui.ListItem(label=title, path=play_path)
        info = {
            'title': title,
            'artist': track.get('artist') or '',
        }
        if track.get('album'):
            info['album'] = track.get('album')
        list_item.setInfo('music', info)
        list_item.setProperty('IsPlayable', 'true')
        try:
            list_item.setContentLookup(False)
        except Exception:
            pass
        if '.mp3' in url.lower():
            list_item.setMimeType('audio/mpeg')
        playlist.add(play_path, list_item)
        count += 1
    if count < 1:
        return False
    if startpos < 0 or startpos >= count:
        startpos = 0
    log('Playing music playlist with %s tracks (start %s)' % (count, startpos))
    xbmc.Player().play(playlist, None, False, startpos)
    return True


def stop_audio():
    try:
        xbmc.Player().stop()
    except Exception:
        pass


def play_next_audio():
    try:
        xbmc.Player().playnext()
    except Exception:
        pass


def play_previous_audio():
    try:
        xbmc.Player().playprevious()
    except Exception:
        pass


def is_playing_audio():
    try:
        return bool(xbmc.Player().isPlayingAudio())
    except Exception:
        return False


def music_playlist_size():
    try:
        return xbmc.PlayList(xbmc.PLAYLIST_MUSIC).size()
    except Exception:
        return 0


def play_stream(title, url, headers=None, subtitles=None):
    headers = dict(headers or {})
    if not headers.get('User-Agent') and not headers.get('user-agent'):
        headers['User-Agent'] = source2.USER_AGENT
    if not headers.get('Accept'):
        headers['Accept'] = '*/*'

    header_string = encode_headers(headers)
    play_path = '%s|%s' % (url, header_string) if header_string else url
    use_isa = '.m3u8' in (url or '').lower() and _inputstream_available()
    item_path = url if use_isa else play_path

    log('Playing %s via %s' % (title, 'inputstream.adaptive' if use_isa else 'default player'))
    list_item = xbmcgui.ListItem(label=title, path=item_path)
    list_item.setInfo('video', {'title': title, 'mediatype': 'video'})
    list_item.setProperty('IsPlayable', 'true')
    try:
        list_item.setContentLookup(False)
    except Exception:
        pass
    subtitle_urls = [item for item in (subtitles or []) if item]
    if subtitle_urls:
        try:
            list_item.setSubtitles(subtitle_urls)
        except Exception:
            pass

    if '.m3u8' in (url or '').lower():
        list_item.setMimeType('application/vnd.apple.mpegurl')
        if use_isa:
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            list_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            if header_string:
                list_item.setProperty('inputstream.adaptive.stream_headers', header_string)
                list_item.setProperty('inputstream.adaptive.manifest_headers', header_string)
                list_item.setProperty('inputstream.adaptive.common_headers', header_string)

    xbmc.Player().play(item_path, list_item, False)


def resolve_and_play(channel):
    title = channel.get('title') or 'Sports'
    watch_url = channel.get('url')
    if not watch_url:
        xbmcgui.Dialog().notification(
            paths.ADDON_NAME,
            'No stream URL on that source.',
            paths.ICON_PATH,
            3000
        )
        return

    progress = xbmcgui.DialogProgress()
    progress.create(paths.ADDON_NAME, 'Resolving %s...' % title)
    try:
        log('Resolving Source Two: %s (%s)' % (title, watch_url))
        resolved = source2.resolve_247_channel(
            watch_url,
            referer=channel.get('referer') or source2.REFERER
        )
        if progress.iscanceled():
            return
        play_url = resolved.get('url')
        play_headers = resolved.get('headers') or {}
        resolver = resolved.get('resolver') or 'direct'
        log('Resolved via %s: %s' % (resolver, str(play_url)[:160]))
        if not play_url:
            raise RuntimeError('No play URL returned')

        try:
            progress.update(70, 'Checking stream...')
        except Exception:
            pass
        if progress.iscanceled():
            return
        if not stream_looks_live(play_url, play_headers):
            progress.close()
            xbmcgui.Dialog().ok(
                paths.ADDON_NAME,
                'Stream is down.\nPlease try another source.'
            )
            return

        progress.close()
        play_stream(title, play_url, play_headers)
    except Exception as exc:
        log('Source Two resolve failed: %s' % exc)
        try:
            progress.close()
        except Exception:
            pass
        xbmcgui.Dialog().ok(
            paths.ADDON_NAME,
            'Could not start the stream.\n%s' % exc
        )
