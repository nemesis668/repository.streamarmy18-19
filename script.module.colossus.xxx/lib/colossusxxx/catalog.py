                                                          

from __future__ import absolute_import

import os
import re

from resources.lib.core.remote import RemoteError, call


PLAY_MODES = ('801', '803', '810')
_COLOR_RE = re.compile(r'\[/?COLOR[^\]]*\]', re.I)
_BOLD_RE = re.compile(r'\[/?B\]', re.I)


def _strip_colors(text):
    text = _COLOR_RE.sub('', text or '')
    return _BOLD_RE.sub('', text)


def _icon():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root, 'icon.png')


def _run(name, *args, **kwargs):
    try:
        return call('adult', name, list(args), kwargs)
    except RemoteError as exc:
        raise RuntimeError(str(exc))


def ensure_loaded():
    return None


def image_path(name):
    return _icon()


def is_play_item(payload):
    if not payload:
        return False
    if payload.get('kind') == 'video':
        return True
    mode = str(payload.get('mode') or '').lower()
    if mode in PLAY_MODES:
        return True
    if 'playvid' in mode or mode.endswith('.play') or '.play_' in mode:
        return True
    return False


def list_sites(section):
    items = _run('list_sites', section) or []
    icon = _icon()
    for item in items:
        art = str(item.get('art') or '')
        if not art.startswith('http://') and not art.startswith('https://'):
            item['art'] = icon
    return items


def browse(payload):
    return _run('browse', payload or {}) or []


def search_all(phrase, section='sites', progress=None, per_site=25, workers=4):
    def _on_progress(percent, text):
        if progress is None:
            return False
        message = (text or 'Searching...').replace('\n', '  |  ')
        try:
            progress.update(int(percent or 0), message)
        except TypeError:
            lines = (text or 'Searching...').split('\n')
            while len(lines) < 3:
                lines.append('')
            try:
                progress.update(int(percent or 0), lines[0], lines[1], lines[2])
            except Exception:
                pass
        except Exception:
            pass
        try:
            import xbmc
            xbmc.sleep(1)
        except Exception:
            pass
        try:
            return bool(progress.iscanceled())
        except Exception:
            return False

    try:
        return call(
            'adult',
            'search_all',
            [phrase],
            {'section': section, 'per_site': per_site, 'workers': workers},
            on_progress=_on_progress,
        ) or []
    except RemoteError as exc:
        raise RuntimeError(str(exc))


def play(payload):
    return _run('play', payload or {}) or {}


def gui_site_item(site):
    title = site.get('title') or 'Source'
    section = site.get('section') or 'sites'
    if section == 'cams':
        meta = 'Live cams'
        overview = 'Open this source to browse live rooms and play a stream.'
    elif section == 'movies':
        meta = 'Movies'
        overview = 'Open this source to browse movie titles, then play.'
    else:
        meta = 'Site'
        overview = 'Open this source to browse categories and videos, then play.'
    return {
        'label': title,
        'title': title,
        'meta': meta,
        'overview': overview,
        'art': site.get('art') or '',
        'search': title,
        'data': site,
    }


def gui_list_item(entry, fallback_art=''):
    name = _strip_colors(entry.get('name') or 'Item')
    kind = entry.get('kind') or 'dir'
    if kind == 'video':
        meta = 'Play'
        overview = entry.get('desc') or 'Resolve this item and play it.'
        if entry.get('quality'):
            meta = '%s  |  %s' % (meta, entry['quality'])
        if entry.get('duration'):
            meta = '%s  |  %s' % (meta, entry['duration'])
    elif entry.get('folder') is False:
        meta = 'Action'
        overview = 'Run this action.'
    else:
        meta = 'Open'
        overview = entry.get('desc') or 'Open this folder.'
    art = entry.get('icon') or entry.get('fanart') or fallback_art
    payload = dict(entry)
    if 'source' not in payload:
        payload['source'] = 'site'
    return {
        'label': entry.get('name') or name,
        'title': name,
        'meta': meta,
        'overview': overview,
        'art': art,
        'search': name,
        'data': payload,
    }
