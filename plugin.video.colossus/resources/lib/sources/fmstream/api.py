                                                               

from __future__ import absolute_import

from resources.lib.core.remote import RemoteError, call


PAGE_SIZE = 50


class FmstreamError(Exception):
    pass


class FmstreamBlocked(FmstreamError):
    pass


def _run(name, *args, **kwargs):
    try:
        return call('fmstream', name, list(args), kwargs)
    except RemoteError as exc:
        if exc.exc == 'FmstreamBlocked':
            raise FmstreamBlocked(str(exc))
        raise FmstreamError(str(exc))


def get_countries():
    return _run('get_countries')


def get_station_page(country_code, offset=0, search=''):
    return _run('get_station_page', country_code, offset, search)


def playable_streams(station):
    streams = []
    for stream in (station or {}).get('streams') or []:
        codec = (stream.get('codec') or '').lower()
        url = (stream.get('url') or '').strip()
        if not url or codec == 'web':
            continue
        if url.lower().startswith('javascript:'):
            continue
        streams.append(stream)
    streams.sort(key=lambda item: int(item.get('bitrate') or 0), reverse=True)
    return streams


def format_kbps(bitrate):
    try:
        value = int(bitrate or 0)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    if value >= 1000:
        return '%s kbps' % int(round(value / 1000.0))
    return '%s kbps' % value


def format_stream_label(stream, index=None, total=None):
    codec = (stream.get('codec') or '').upper()
    if codec == 'VOR':
        codec = 'OGG'
    elif codec == 'OPU':
        codec = 'OPUS'
    parts = [part for part in (format_kbps(stream.get('bitrate')), codec) if part]
    region = stream.get('region') or ''
    label = ' '.join(parts) if parts else 'Stream'
    if region:
        label = '%s  |  %s' % (label, region)
    elif stream.get('profile'):
        label = '%s  |  %s' % (label, stream.get('profile'))
    if index and total:
        return '%s    (%s/%s)' % (label, index, total)
    return label
