from __future__ import absolute_import

import os

import pyxbmct
import xbmc
import xbmcgui

from resources.lib.core import debrid
from resources.lib.core import paths
from resources.lib.core import prowlarr
from resources.lib.core import tmdb
from resources.lib.gui.details import ColossusFullWindow


def panel_texture():
    if os.path.exists(paths.FRAME_PATH):
        return paths.FRAME_PATH
    return os.path.join(
        os.path.dirname(pyxbmct.__file__),
        'textures',
        'estuary',
        'AddonWindow',
        'ContentPanel.png'
    )


def dialog_background_texture():
    background = os.path.join(paths.MEDIA_PATH, 'dialog_bg.png')
    if os.path.exists(background):
        return background
    return panel_texture()


def truncate(text, limit):
    text = text or ''
    return text if len(text) <= limit else text[:limit - 3] + '...'


class ColossusDialog(pyxbmct.BlankDialogWindow):
    def __init__(self):
        super(ColossusDialog, self).__init__()
        self.setGeometry(1050, 650, 100, 100)
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def add_panel(self):
        self.panel_background = pyxbmct.Image(dialog_background_texture())
        self.placeControl(self.panel_background, 0, 0, 100, 100, pad_x=0, pad_y=0)
        if os.path.exists(paths.FRAME_PATH):
            self.panel_frame = pyxbmct.Image(paths.FRAME_PATH)
            self.placeControl(self.panel_frame, 0, 0, 100, 100, pad_x=0, pad_y=0)

    def add_header(self, title, subtitle=''):
        self.title_label = pyxbmct.Label('[B]%s[/B]' % title, alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.title_label, 3, 8, 7, 84)
        self.status_label = pyxbmct.Label(subtitle, alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.status_label, 11, 8, 7, 84)


class MoviesWindow(ColossusFullWindow):
    def __init__(self, heading=None, genre_id=None):
        super(MoviesWindow, self).__init__('')
        self.window_heading = heading or 'MOVIES & SHOWS'
        self.genre_id = genre_id
        self.tmdb_results = []
        self.current_index = -1
        self.page_number = 1
        self.total_pages = 1
        self.query = ''
        self.prev_button = None
        self.next_button = None
        self.setup_canvas()
        self.set_controls()
        self.set_navigation()
        if self.genre_id:
            self.load_page(1)
            self.setFocus(self.results_list if self.tmdb_results else self.search_button)
        else:
            self.setFocus(self.search_button)

    def set_controls(self):
        self.add_fanart(paths.BACKDROP_PATH or paths.FANART_PATH)

        self.back_button = pyxbmct.Button('Back')
        self.placeControl(self.back_button, 2, 2, 6, 10)
        self.connect(self.back_button, self.close)

        self.header_label = pyxbmct.Label(
            '[B]%s[/B]' % self.window_heading,
            font='font13',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.header_label, 2, 14, 6, 50)

        if self.genre_id:
            status_text = 'Browse TMDB musical movies, then select one to open the movie page.'
            empty_title = 'Musical Movies'
            empty_meta = 'TMDB Music / Musical genre'
            empty_overview = (
                'These films are tagged as Music on TMDB. Highlight one to preview it, '
                'then select it to open the same movie page used in Movies & Shows.'
            )
            search_label = 'Search movie'
            list_heading = 'MUSICALS'
        else:
            status_text = 'Search TMDB for a movie or TV show.'
            empty_title = 'Search Colossus'
            empty_meta = 'Movie or TV show'
            empty_overview = (
                'Search TMDB, then highlight a result to preview its poster, fanart, and overview. '
                'Select a movie to open the movie page, or a show to open seasons and episodes.'
            )
            search_label = 'Search'
            list_heading = 'RESULTS'

        self.status_label = pyxbmct.Label(
            status_text,
            font='font12',
            textColor='0xFFD0D6DE',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.status_label, 2, 64, 6, 32)

        self.poster = pyxbmct.Image(paths.ICON_PATH, aspectRatio=2)
        self.placeControl(self.poster, 12, 3, 56, 20)

        self.title_label = pyxbmct.Label(
            '[B]%s[/B]' % empty_title,
            font='font30',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.title_label, 12, 25, 10, 40)

        self.meta_label = pyxbmct.Label(
            empty_meta,
            font='font13',
            textColor='0xFFD0D6DE',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.meta_label, 23, 25, 6, 40)

        self.overview_box = pyxbmct.TextBox(font='font13', textColor='0xFFE8EEF4')
        self.placeControl(self.overview_box, 30, 25, 32, 40)
        self.overview_box.setText(empty_overview)

        self.search_button = pyxbmct.Button(search_label)
        self.placeControl(self.search_button, 66, 3, 8, 18)
        self.connect(self.search_button, self.search)

        self.resolveurl_button = pyxbmct.Button('ResolveURL')
        self.placeControl(self.resolveurl_button, 66, 22, 8, 16)
        self.connect(self.resolveurl_button, self.open_resolveurl_settings)

        if self.genre_id:
            self.prev_button = pyxbmct.Button('Previous')
            self.placeControl(self.prev_button, 76, 3, 8, 18)
            self.connect(self.prev_button, self.go_previous)
            self.next_button = pyxbmct.Button('Next page')
            self.placeControl(self.next_button, 86, 3, 8, 18)
            self.connect(self.next_button, self.go_next)

        self.list_heading = pyxbmct.Label(
            '[B]%s[/B]' % list_heading,
            font='font13',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.list_heading, 8, 68, 6, 28)

        self.results_list = pyxbmct.List()
        self.placeControl(self.results_list, 14, 66, 78, 32)
        self.connect(self.results_list, self.handle_selected)

    def set_navigation(self):
        self.back_button.controlRight(self.search_button)
        self.back_button.controlDown(self.search_button)
        self.search_button.controlUp(self.back_button)
        self.search_button.controlLeft(self.back_button)
        self.search_button.controlRight(self.resolveurl_button)
        self.resolveurl_button.controlUp(self.back_button)
        self.resolveurl_button.controlLeft(self.search_button)
        self.resolveurl_button.controlRight(self.results_list)

        if self.prev_button is not None and self.next_button is not None:
            self.search_button.controlDown(self.prev_button)
            self.resolveurl_button.controlDown(self.prev_button)
            self.prev_button.controlUp(self.search_button)
            self.prev_button.controlDown(self.next_button)
            self.prev_button.controlRight(self.results_list)
            self.next_button.controlUp(self.prev_button)
            self.next_button.controlRight(self.results_list)
            self.results_list.controlLeft(self.search_button)
            self.results_list.controlUp(self.search_button)
        else:
            self.search_button.controlDown(self.results_list)
            self.resolveurl_button.controlDown(self.results_list)
            self.results_list.controlLeft(self.search_button)
            self.results_list.controlUp(self.search_button)

    def onAction(self, action):
        super(MoviesWindow, self).onAction(action)
        self.update_preview()

    def search(self):
        query = self.get_query()
        if query is None:
            return
        self.query = query
        self.page_number = 1
        if self.genre_id:
            self.load_page(1)
            return

        if not query:
            return

        self.tmdb_results = []
        self.current_index = -1
        self.results_list.reset()
        self.status_label.setLabel('Searching TMDB...')
        try:
            xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
            self.tmdb_results = tmdb.search(query)
        except Exception as error:
            self.show_error('TMDB error: %s' % error)
            return
        finally:
            xbmc.executebuiltin('Dialog.Close(busydialognocancel)')

        if not self.tmdb_results:
            self.show_error('No TMDB movie or show results found.')
            return

        self.results_list.reset()
        self.status_label.setLabel('%s results  |  Select a movie or show.' % len(self.tmdb_results))
        for item in self.tmdb_results:
            self.results_list.addItem(self.format_tmdb_result(item))
        self.setFocus(self.results_list)
        self.update_preview(force=True)

    def load_page(self, page):
        page = max(1, int(page or 1))
        self.page_number = page
        self.tmdb_results = []
        self.current_index = -1
        self.results_list.reset()
        self.status_label.setLabel('Loading musical movies...')
        try:
            xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
            if self.query:
                payload = tmdb.search_movies(self.query, genre_id=self.genre_id, page=page)
            else:
                payload = tmdb.discover_movies(self.genre_id, page=page)
        except Exception as error:
            self.show_error('TMDB error: %s' % error)
            return
        finally:
            xbmc.executebuiltin('Dialog.Close(busydialognocancel)')

        self.tmdb_results = payload.get('results') or []
        self.total_pages = max(1, int(payload.get('total_pages') or 1))
        self.page_number = int(payload.get('page') or page)
        if not self.tmdb_results:
            self.show_error('No musical movies found.')
            return

        self.results_list.reset()
        total = int(payload.get('total_results') or len(self.tmdb_results))
        self.status_label.setLabel(
            'Page %s of %s  |  %s films  |  Select a movie.' % (
                self.page_number,
                self.total_pages,
                total
            )
        )
        for item in self.tmdb_results:
            self.results_list.addItem(self.format_tmdb_result(item))
        self.setFocus(self.results_list)
        self.update_preview(force=True)

    def go_previous(self):
        if self.page_number <= 1:
            xbmcgui.Dialog().notification(
                paths.ADDON_NAME,
                'Already on the first page.',
                paths.ICON_PATH,
                2500
            )
            return
        self.load_page(self.page_number - 1)

    def go_next(self):
        if self.page_number >= self.total_pages:
            xbmcgui.Dialog().notification(
                paths.ADDON_NAME,
                'No more pages.',
                paths.ICON_PATH,
                2500
            )
            return
        self.load_page(self.page_number + 1)

    def handle_selected(self):
        index = self.results_list.getSelectedPosition()
        if index < 0 or index >= len(self.tmdb_results):
            return
        open_media_details(self.tmdb_results[index])

    def update_preview(self, force=False):
        if not self.tmdb_results:
            return
        try:
            index = self.results_list.getSelectedPosition()
        except Exception:
            return
        if index < 0 or index >= len(self.tmdb_results):
            return
        if not force and index == self.current_index:
            return
        self.current_index = index
        item = self.tmdb_results[index]
        media_type = 'Movie' if item.get('media_type') == 'movie' else 'TV Show'
        year = item.get('year') or ''
        self.title_label.setLabel('[B]%s[/B]' % (item.get('title') or 'Unknown'))
        self.meta_label.setLabel('   |   '.join([part for part in (media_type, year) if part]))
        self.overview_box.setText(item.get('overview') or 'No overview available from TMDB.')
        try:
            self.poster.setImage(item.get('poster') or paths.ICON_PATH)
        except Exception:
            pass
        backdrop = item.get('backdrop') or paths.BACKDROP_PATH or paths.FANART_PATH
        try:
            self.backdrop.setImage(backdrop)
        except Exception:
            pass

    def get_query(self):
        heading = 'Search movie' if self.genre_id else 'Search Movies & Shows'
        keyboard = xbmc.Keyboard(self.query if self.genre_id else '', heading)
        keyboard.doModal()
        if keyboard.isConfirmed():
            return keyboard.getText().strip()
        return None

    def open_resolveurl_settings(self):
        debrid.open_resolveurl_settings()

    def show_error(self, message):
        self.tmdb_results = []
        self.current_index = -1
        self.results_list.reset()
        self.status_label.setLabel(message)
        self.title_label.setLabel('[B]No results[/B]')
        self.meta_label.setLabel('')
        self.overview_box.setText(message)
        xbmcgui.Dialog().notification(paths.ADDON_NAME, message, paths.ICON_PATH, 3500)

    def format_tmdb_result(self, item):
        media_type = 'Movie' if item.get('media_type') == 'movie' else 'TV'
        year = item.get('year') or ''
        title = item.get('title') or 'Unknown'
        if year:
            return '%s    %s    %s' % (title, year, media_type)
        return '%s    %s' % (title, media_type)


class SourceWindow(ColossusDialog):
    def __init__(self, media, episode=None):
        super(SourceWindow, self).__init__()
        self.media = media
        self.episode = episode
        self.sources = []
        self.set_controls()
        self.set_navigation()
        self.search_sources()
        self.setFocus(self.list_control)

    def set_controls(self):
        self.add_panel()
        self.add_header(self.media.get('title', 'Sources'), 'Prowlarr results sorted by quality and seeders')
        self.list_control = pyxbmct.List()
        self.placeControl(self.list_control, 20, 5, 62, 90)
        self.back_button = pyxbmct.Button('Back')
        self.placeControl(self.back_button, 87, 30, 8, 18)
        self.close_button = pyxbmct.Button('Close')
        self.placeControl(self.close_button, 87, 55, 8, 18)
        self.connect(self.list_control, self.play_selected)
        self.connect(self.back_button, self.close)
        self.connect(self.close_button, self.close)

    def set_navigation(self):
        self.list_control.controlDown(self.back_button)
        self.list_control.controlUp(self.back_button)
        self.back_button.controlUp(self.list_control)
        self.back_button.controlRight(self.close_button)
        self.close_button.controlUp(self.list_control)
        self.close_button.controlLeft(self.back_button)

    def search_sources(self):
        query = build_prowlarr_query(self.media, self.episode)
        self.list_control.reset()
        self.list_control.addItem('Searching Prowlarr for "%s"...' % query)
        try:
            self.sources = prowlarr.search(query)
        except Exception as error:
            self.list_control.reset()
            self.list_control.addItem('Prowlarr error: %s' % error)
            return
        self.list_control.reset()
        if not self.sources:
            self.list_control.addItem('No Prowlarr results found for "%s"' % query)
            return
        for source in self.sources:
            self.list_control.addItem(format_source(source))

    def play_selected(self):
        index = self.list_control.getSelectedPosition()
        if index < 0 or index >= len(self.sources):
            return
        source = self.sources[index]
        self.status_label.setLabel('Resolving %s...' % source.get('quality', 'source'))
        try:
            stream_url = debrid.resolve_magnet(source['magnet'])
        except Exception as error:
            self.list_control.reset()
            self.list_control.addItem('ResolveURL error: %s' % error)
            self.status_label.setLabel('ResolveURL error: %s' % error)
            return
        list_item = xbmcgui.ListItem(label=source.get('title', 'Colossus Stream'))
        list_item.setPath(stream_url)
        xbmc.Player().play(stream_url, list_item)


def load_media_details(media):
    try:
        return tmdb.details(media['media_type'], media['id'])
    except Exception:
        return media


def build_prowlarr_query(media, episode=None):
    title = media.get('title', '').strip()
    if episode:
        return '%s S%02dE%02d' % (
            title,
            int(episode.get('season_number') or 0),
            int(episode.get('episode_number') or 0)
        )
    year = media.get('year', '').strip()
    if media.get('media_type') == 'movie' and year:
        return '%s %s' % (title, year)
    return title


def format_source(source):
    return '%s | %s seeds | %s | %s | %s' % (
        source.get('quality', 'unknown').upper(),
        source.get('seeders', 0),
        format_size(source.get('size', 0)),
        source.get('indexer', 'Prowlarr'),
        truncate(source.get('title', 'Unknown'), 90)
    )


def format_size(size):
    try:
        size = float(size)
    except Exception:
        return '? GB'
    if size <= 0:
        return '? GB'
    return '%.2f GB' % (size / (1024 ** 3))


def open_media_details(media):
    from resources.lib.gui.details import open_media_info_window
    open_media_info_window(media)


def open_season_window(show):
    from resources.lib.gui.details import open_media_info_window
    open_media_info_window(show)


def open_episode_window(show, season):
    from resources.lib.gui.details import open_episode_info_window
    open_episode_info_window(show, season)


def open_source_window(media, episode=None):
    window = SourceWindow(media, episode)
    window.doModal()
    del window


def open_media_from_home(media):
    open_media_details(media)


def open_movies_window():
    window = MoviesWindow()
    window.doModal()
    del window


def open_musical_movies_window():
    window = MoviesWindow(heading='MUSICAL MOVIES', genre_id=tmdb.MUSIC_GENRE_ID)
    window.doModal()
    del window
