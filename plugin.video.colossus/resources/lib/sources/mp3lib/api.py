                                                        

from __future__ import absolute_import

from resources.lib.core.remote import RemoteError, call


BASE_URL = 'https://songslover.net'
REFERER = BASE_URL + '/'
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
)
PAGE_SIZE = 20
CATEGORIES = (
    {'key': 'albums', 'id': 162, 'title': 'Latest albums'},
    {'key': 'tracks', 'id': 110, 'title': 'Latest tracks'},
    {'key': 'old', 'id': 83, 'title': 'Old albums'},
)
LETTERS = tuple(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + ['#'])


class Mp3Error(Exception):
    pass


def _run(name, *args, **kwargs):
    try:
        return call('mp3lib', name, list(args), kwargs)
    except RemoteError as exc:
        raise Mp3Error(str(exc))


def get_category_page(category_id, page=1):
    return _run('get_category_page', category_id, page)


def search(query, page=1):
    return _run('search', query, page)


def get_letter_items(letter):
    return _run('get_letter_items', letter)


def get_release(post_id=None, link='', slug=''):
    return _run('get_release', post_id=post_id, link=link, slug=slug)
