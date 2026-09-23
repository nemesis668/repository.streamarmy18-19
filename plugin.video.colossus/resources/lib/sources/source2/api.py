                                                           

from __future__ import absolute_import

from resources.lib.core.remote import RemoteError, call


BASE_URL = "https://dlive.sx"
REFERER = BASE_URL + "/"
STREAM_REFERER = "https://hamis.romponalis.st/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
)


def _run(name, *args, **kwargs):
    try:
        return call('sports', name, list(args), kwargs)
    except RemoteError as exc:
        raise RuntimeError(str(exc))


def get_247_channels(timeout=15):
    return _run('get_247_channels', timeout=timeout)


def get_live_sports_categories(timeout=15):
    return _run('get_live_sports_categories', timeout=timeout)


def get_live_sports_events(category_url, category_title="Live Sports", timeout=15, allow_proxy=True):
    return _run(
        'get_live_sports_events',
        category_url,
        category_title=category_title,
        timeout=timeout,
        allow_proxy=allow_proxy,
    )


def get_upcoming_events(timeout=15):
    return _run('get_upcoming_events', timeout=timeout)


def search(query, timeout=15):
    return _run('search', query, timeout=timeout)


def resolve_247_channel(channel_url, timeout=15, referer=REFERER):
    return _run('resolve_247_channel', channel_url, timeout=timeout, referer=referer)
