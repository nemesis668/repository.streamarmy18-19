                                                          

from __future__ import absolute_import

from resources.lib.core.remote import RemoteError, call


class AnimeError(Exception):
    pass


def _run(name, *args, **kwargs):
    try:
        return call('anime', name, list(args), kwargs)
    except RemoteError as exc:
        raise AnimeError(str(exc))


def latest_titles():
    return _run('latest_titles')


def top_titles(period='day'):
    return _run('top_titles', period)


def most_viewed(page=1):
    return _run('most_viewed', page)


def az_titles(letter='All', page=1):
    return _run('az_titles', letter, page)


def random_episode():
    return _run('random_episode')


def search_titles(keyword):
    return _run('search_titles', keyword)


def episodes_for(show):
    return _run('episodes_for', show)


def servers_for(episode):
    return _run('servers_for', episode)


def resolve_server(server):
    return _run('resolve_server', server)
