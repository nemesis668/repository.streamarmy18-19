                                                                        

from __future__ import absolute_import

from resources.lib.core.remote import RemoteError, call


class ProwlarrError(Exception):
    pass


def is_configured():
    return True


def search(query):
    try:
        return call('prowlarr', 'search', [query], {})
    except RemoteError as exc:
        raise ProwlarrError(str(exc))
