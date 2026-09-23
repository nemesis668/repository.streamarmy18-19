                                                            

from __future__ import absolute_import

from resources.lib.core.remote import RemoteError, call


class CartoonError(Exception):
    pass


def _run(name, *args, **kwargs):
    try:
        return call('cartoon', name, list(args), kwargs)
    except RemoteError as exc:
        raise CartoonError(str(exc))


def shows_for_letter(letter):
    return _run('shows_for_letter', letter)


def search_shows(keyword):
    return _run('search_shows', keyword)


def episodes_for(show):
    return _run('episodes_for', show)


def resolve_episode(episode_url):
    return _run('resolve_episode', episode_url)
