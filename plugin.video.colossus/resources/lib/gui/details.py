from __future__ import absolute_import

import os

import pyxbmct
import xbmc
import xbmcgui

from resources.lib.core import paths
from resources.lib.core import tmdb


class ColossusFullWindow(pyxbmct.AddonFullWindow):
    def __new__(cls, *args, **kwargs):
        return super(ColossusFullWindow, cls).__new__(cls, '')

    def setup_canvas(self):
        self.setGeometry(1280, 720, 100, 100)
        self.x = 0
        self.y = 0
        self.grid_x = 0
        self.grid_y = 0
        self.tile_width = 12
        self.tile_height = 7
        self.hide_default_chrome()
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)

    def hide_default_chrome(self):
        for name in ('window_close_button', 'title_bar', 'title_background', 'background'):
            control = getattr(self, name, None)
            if control is None:
                continue
            try:
                control.setVisible(False)
                control.setEnabled(False)
            except Exception:
                pass

    def add_fanart(self, backdrop):
        blackout = os.path.join(paths.MEDIA_PATH, 'dialog_bg.png')
        if os.path.exists(blackout):
            self.blackout = xbmcgui.ControlImage(0, 0, 1280, 720, blackout)
            self.addControl(self.blackout)
        image = backdrop or paths.BACKDROP_PATH or paths.FANART_PATH
        self.backdrop = xbmcgui.ControlImage(0, 0, 1280, 720, image)
        self.addControl(self.backdrop)
        dim_path = paths.MEDIA_DIM_PATH if os.path.exists(paths.MEDIA_DIM_PATH) else ''
        if dim_path:
            self.dim = xbmcgui.ControlImage(0, 0, 1280, 720, dim_path)
            self.addControl(self.dim)


class MediaInfoWindow(ColossusFullWindow):
    def __init__(self, media):
        super(MediaInfoWindow, self).__init__('')
        self.media = media
        self.seasons = media.get('seasons') or []
        self.cast_images = []
        self.cast_labels = []
        self.setup_canvas()
        self.set_controls()
        self.set_navigation()
        if self.media.get('media_type') == 'tv' and self.seasons:
            self.setFocus(self.season_list)
        else:
            self.setFocus(self.primary_button)

    def set_controls(self):
        self.add_fanart(self.media.get('backdrop'))
        self.add_poster()
        self.add_info()
        self.add_cast()
        self.add_actions()

    def add_poster(self):
        poster = self.media.get('poster') or paths.ICON_PATH
        self.poster = pyxbmct.Image(poster, aspectRatio=2)
        self.placeControl(self.poster, 8, 3, 66, 20)

    def add_info(self):
        title = self.media.get('title') or 'Unknown'
        self.title_label = pyxbmct.Label(
            '[B]%s[/B]' % title,
            font='font30',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.title_label, 8, 25, 10, 40)

        self.meta_label = pyxbmct.Label(
            self.build_meta_line(),
            font='font13',
            textColor='0xFFD0D6DE',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.meta_label, 18, 25, 6, 40)

        tagline = self.media.get('tagline') or ''
        self.tagline_label = pyxbmct.Label(
            '[I]%s[/I]' % tagline if tagline else '',
            font='font13',
            textColor='0xFFB8C0C8',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.tagline_label, 24, 25, 5, 40)

        self.overview_box = pyxbmct.TextBox(font='font13', textColor='0xFFE8EEF4')
        self.placeControl(self.overview_box, 30, 25, 22, 40)
        self.overview_box.setText(self.media.get('overview') or 'No overview available from TMDB.')
        try:
            self.overview_box.autoScroll(8000, 3000, 5000)
        except Exception:
            pass

        credit_line = self.build_credit_line()
        self.credit_label = pyxbmct.Label(
            credit_line,
            font='font12',
            textColor='0xFFC5CDD6',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.credit_label, 53, 25, 6, 40)

        if self.media.get('media_type') == 'tv':
            self.season_heading = pyxbmct.Label(
                '[B]SEASONS[/B]',
                font='font13',
                textColor='0xFFFFFFFF',
                alignment=pyxbmct.ALIGN_LEFT
            )
            self.placeControl(self.season_heading, 8, 68, 6, 28)
            self.season_list = pyxbmct.List()
            self.placeControl(self.season_list, 14, 66, 58, 30)
            if not self.seasons:
                try:
                    self.seasons = tmdb.seasons(self.media['id'])
                except Exception:
                    self.seasons = []
            if self.seasons:
                for season in self.seasons:
                    self.season_list.addItem(
                        '%s    %s episodes' % (
                            season.get('name', 'Season'),
                            season.get('episode_count', 0)
                        )
                    )
            else:
                self.season_list.addItem('No seasons found')
            self.connect(self.season_list, self.open_selected_season)
        else:
            self.season_list = None

    def add_cast(self):
        self.cast_heading = pyxbmct.Label(
            '[B]CAST & CREW[/B]',
            font='font13',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.cast_heading, 76, 3, 5, 20)

        cast = [person for person in (self.media.get('cast') or []) if person.get('photo')][:8]
        for index, person in enumerate(cast):
            column = 3 + (index * 12)
            image = pyxbmct.Image(person['photo'], aspectRatio=2)
            self.cast_images.append(image)
            self.placeControl(image, 81, column, 13, 11)
            name = pyxbmct.Label(
                person.get('name', ''),
                font='font12',
                textColor='0xFFD0D6DE',
                alignment=pyxbmct.ALIGN_CENTER
            )
            self.cast_labels.append(name)
            self.placeControl(name, 94, column, 4, 11)

    def add_actions(self):
        self.back_button = pyxbmct.Button('Back')
        self.placeControl(self.back_button, 2, 2, 6, 10)
        self.connect(self.back_button, self.close)

        if self.media.get('media_type') == 'movie':
            self.primary_button = pyxbmct.Button('Play')
            self.placeControl(self.primary_button, 40, 68, 10, 26)
            self.connect(self.primary_button, self.search_movie_sources)
        else:
            self.play_button = pyxbmct.Button('Play')
            self.placeControl(self.play_button, 62, 25, 8, 14)
            self.connect(self.play_button, self.open_show_play)
            self.primary_button = self.play_button

    def set_navigation(self):
        if self.media.get('media_type') == 'tv' and self.season_list:
            self.back_button.controlRight(self.season_list)
            self.back_button.controlDown(self.play_button)
            self.play_button.controlUp(self.back_button)
            self.play_button.controlRight(self.season_list)
            self.season_list.controlLeft(self.play_button)
            self.season_list.controlUp(self.back_button)
            return

        self.back_button.controlRight(self.primary_button)
        self.back_button.controlDown(self.primary_button)
        self.primary_button.controlLeft(self.back_button)
        self.primary_button.controlUp(self.back_button)

    def build_meta_line(self):
        parts = []
        rating = self.media.get('rating') or 0
        if rating:
            parts.append('%.1f' % float(rating))
        if self.media.get('year'):
            parts.append(str(self.media.get('year')))
        if self.media.get('certification'):
            parts.append(self.media.get('certification'))
        if self.media.get('runtime_label'):
            parts.append(self.media.get('runtime_label'))
        genres = self.media.get('genres') or []
        if genres:
            parts.append(' / '.join(genres[:4]))
        if self.media.get('media_type') == 'tv' and self.media.get('season_count'):
            count = self.media.get('season_count')
            parts.append('%s Season%s' % (count, '' if count == 1 else 's'))
        return '   |   '.join(parts)

    def build_credit_line(self):
        names = self.media.get('creators') or []
        if not names:
            return ''
        label = 'Created by' if self.media.get('media_type') == 'tv' else 'Director'
        return '%s: %s' % (label, ' / '.join(names[:3]))

    def open_selected_season(self):
        index = self.season_list.getSelectedPosition()
        if index < 0 or index >= len(self.seasons):
            return
        open_episode_info_window(self.media, self.seasons[index])

    def search_movie_sources(self):
        from resources.lib.gui.play import open_play_window
        open_play_window(self.media)

    def open_show_play(self):
        from resources.lib.gui.play import open_play_window
        open_play_window(self.media)


class MovieInfoWindow(ColossusFullWindow):
    def __init__(self, media):
        super(MovieInfoWindow, self).__init__('')
        self.media = media
        self.cast_images = []
        self.cast_labels = []
        self.setup_canvas()
        self.set_controls()
        self.set_navigation()
        self.setFocus(self.play_button)

    def set_controls(self):
        self.add_fanart(self.media.get('backdrop'))
        self.back_button = pyxbmct.Button('Back')
        self.placeControl(self.back_button, 2, 2, 6, 10)
        self.connect(self.back_button, self.close)

        self.title_label = pyxbmct.Label(
            '[B][COLOR FFE50914]%s[/COLOR][/B]' % (self.media.get('title') or 'Unknown'),
            font='font30',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.title_label, 16, 5, 12, 70)

        self.meta_label = pyxbmct.Label(
            self.build_meta_line(),
            font='font13',
            textColor='0xFFD0D6DE',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.meta_label, 29, 5, 6, 80)

        self.credit_label = pyxbmct.Label(
            self.build_credit_line(),
            font='font12',
            textColor='0xFFC5CDD6',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.credit_label, 35, 5, 5, 80)

        tagline = self.media.get('tagline') or ''
        self.tagline_label = pyxbmct.Label(
            '[I]%s[/I]' % tagline if tagline else '',
            font='font13',
            textColor='0xFFB8C0C8',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.tagline_label, 41, 5, 5, 70)

        self.overview_box = pyxbmct.TextBox(font='font13', textColor='0xFFE8EEF4')
        self.placeControl(self.overview_box, 47, 5, 16, 70)
        self.overview_box.setText(self.media.get('overview') or 'No overview available from TMDB.')
        try:
            self.overview_box.autoScroll(8000, 3000, 5000)
        except Exception:
            pass

        self.play_button = pyxbmct.Button('Play')
        self.placeControl(self.play_button, 65, 5, 8, 14)
        self.connect(self.play_button, self.search_movie_sources)

        self.trailer_button = pyxbmct.Button('Trailer')
        self.placeControl(self.trailer_button, 65, 21, 8, 14)
        self.connect(self.trailer_button, self.play_trailer)

        self.add_cast()

    def add_cast(self):
        self.cast_heading = pyxbmct.Label(
            '[B]CAST & CREW[/B]',
            font='font13',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.cast_heading, 76, 5, 5, 20)

        cast = [person for person in (self.media.get('cast') or []) if person.get('photo')][:8]
        for index, person in enumerate(cast):
            column = 5 + (index * 12)
            image = pyxbmct.Image(person['photo'], aspectRatio=2)
            self.cast_images.append(image)
            self.placeControl(image, 81, column, 13, 11)
            name = pyxbmct.Label(
                person.get('name', ''),
                font='font12',
                textColor='0xFFD0D6DE',
                alignment=pyxbmct.ALIGN_CENTER
            )
            self.cast_labels.append(name)
            self.placeControl(name, 94, column, 4, 11)

    def set_navigation(self):
        self.back_button.controlDown(self.play_button)
        self.back_button.controlRight(self.play_button)
        self.play_button.controlUp(self.back_button)
        self.play_button.controlRight(self.trailer_button)
        self.play_button.controlLeft(self.trailer_button)
        self.trailer_button.controlUp(self.back_button)
        self.trailer_button.controlLeft(self.play_button)
        self.trailer_button.controlRight(self.play_button)

    def build_meta_line(self):
        parts = []
        rating = self.media.get('rating') or 0
        if rating:
            parts.append('[COLOR FFF5C518]*[/COLOR] %.1f' % float(rating))
        if self.media.get('year'):
            parts.append(str(self.media.get('year')))
        if self.media.get('runtime_label'):
            parts.append(self.media.get('runtime_label'))
        if self.media.get('certification'):
            parts.append(self.media.get('certification'))
        return '     '.join(parts)

    def build_credit_line(self):
        parts = []
        genres = self.media.get('genres') or []
        if genres:
            parts.append(' / '.join(genres[:4]))
        names = self.media.get('creators') or []
        if names:
            parts.append('Director: %s' % (' / '.join(names[:3])))
        return '   |   '.join(parts)

    def search_movie_sources(self):
        from resources.lib.gui.play import open_play_window
        open_play_window(self.media)

    def play_trailer(self):
        key = self.media.get('trailer_key')
        if not key:
            xbmcgui.Dialog().notification(
                paths.ADDON_NAME,
                'No TMDB trailer found for this movie.',
                paths.ICON_PATH,
                3000
            )
            return
        if not xbmc.getCondVisibility('System.HasAddon(plugin.video.youtube)'):
            xbmcgui.Dialog().notification(
                paths.ADDON_NAME,
                'Install the YouTube addon to play trailers.',
                paths.ICON_PATH,
                3500
            )
            return
        url = 'plugin://plugin.video.youtube/play/?video_id=%s' % key
        list_item = xbmcgui.ListItem(label=self.media.get('trailer_name') or 'Trailer')
        list_item.setPath(url)
        xbmc.Player().play(url, list_item)


class EpisodeInfoWindow(ColossusFullWindow):
    def __init__(self, show, season):
        super(EpisodeInfoWindow, self).__init__('')
        self.show = show
        self.season = season
        self.episodes = []
        self.current_index = -1
        self.setup_canvas()
        self.set_controls()
        self.set_navigation()
        self.load_episodes()
        if self.episodes:
            self.setFocus(self.episode_list)
            self.update_episode_panel()

    def set_controls(self):
        self.add_fanart(self.show.get('backdrop'))
        self.back_button = pyxbmct.Button('Back')
        self.placeControl(self.back_button, 2, 2, 6, 10)
        self.connect(self.back_button, self.close)

        self.header_label = pyxbmct.Label(
            '[B]%s[/B]   |   %s' % (
                self.show.get('title', 'TV Show'),
                self.season.get('name', 'Season')
            ),
            font='font13',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.header_label, 2, 14, 6, 50)

        still = self.show.get('poster') or paths.ICON_PATH
        self.still = pyxbmct.Image(still, aspectRatio=0)
        self.placeControl(self.still, 12, 3, 32, 36)

        self.episode_title = pyxbmct.Label(
            '',
            font='font30',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.episode_title, 12, 41, 8, 26)

        self.episode_meta = pyxbmct.Label(
            '',
            font='font13',
            textColor='0xFFD0D6DE',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.episode_meta, 21, 41, 6, 26)

        self.episode_overview = pyxbmct.TextBox(font='font13', textColor='0xFFE8EEF4')
        self.placeControl(self.episode_overview, 28, 41, 32, 26)
        self.episode_overview.setText('')

        self.list_heading = pyxbmct.Label(
            '[B]EPISODES[/B]',
            font='font13',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_LEFT
        )
        self.placeControl(self.list_heading, 8, 70, 6, 26)

        self.episode_list = pyxbmct.List()
        self.placeControl(self.episode_list, 14, 68, 78, 30)
        self.connect(self.episode_list, self.play_selected_episode)

    def set_navigation(self):
        self.back_button.controlRight(self.episode_list)
        self.back_button.controlDown(self.episode_list)
        self.episode_list.controlLeft(self.back_button)
        self.episode_list.controlUp(self.back_button)

    def load_episodes(self):
        self.episode_list.reset()
        try:
            self.episodes = tmdb.episodes(self.show['id'], self.season['season_number'])
        except Exception as error:
            self.episode_list.addItem('TMDB episode error: %s' % error)
            self.episodes = []
            return
        if not self.episodes:
            self.episode_list.addItem('No episodes found')
            return
        for episode in self.episodes:
            self.episode_list.addItem(
                '%s.  %s' % (
                    episode.get('episode_number') or 0,
                    episode.get('name', 'Episode')
                )
            )

    def onAction(self, action):
        super(EpisodeInfoWindow, self).onAction(action)
        self.update_episode_panel()

    def update_episode_panel(self):
        if not self.episodes:
            return
        try:
            index = self.episode_list.getSelectedPosition()
        except Exception:
            return
        if index < 0 or index >= len(self.episodes) or index == self.current_index:
            return
        self.current_index = index
        episode = self.episodes[index]
        still = episode_still_path(episode, self.show)
        try:
            self.still.setImage(still)
        except Exception:
            pass
        number = episode.get('episode_number') or 0
        self.episode_title.setLabel('[B]%s. %s[/B]' % (number, episode.get('name', 'Episode')))
        self.episode_meta.setLabel(episode_meta_line(episode))
        self.episode_overview.setText(
            episode.get('overview') or 'No overview available from TMDB.'
        )

    def play_selected_episode(self):
        if not self.episodes:
            return
        index = self.episode_list.getSelectedPosition()
        if index < 0 or index >= len(self.episodes):
            return
        from resources.lib.gui.play import open_play_window
        open_play_window(self.show, self.episodes[index])


def episode_still_path(episode, show):
    still = episode.get('still') or ''
    if still:
        cached = tmdb._cache_image(
            still,
            'still_%s.jpg' % (episode.get('id') or episode.get('episode_number'))
        )
        if cached:
            episode['still'] = cached
            return cached
    return show.get('poster') or paths.ICON_PATH


def episode_meta_line(episode):
    parts = []
    season = int(episode.get('season_number') or 0)
    number = int(episode.get('episode_number') or 0)
    parts.append('S%s E%s' % (season, number))
    air_date = format_air_date(episode.get('air_date'))
    if air_date:
        parts.append(air_date)
    if episode.get('runtime_label'):
        parts.append(episode.get('runtime_label'))
    return '   |   '.join(parts)


def format_air_date(value):
    parts = (value or '').split('-')
    if len(parts) != 3:
        return value or ''
    months = (
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    )
    try:
        return '%s %s %s' % (int(parts[2]), months[int(parts[1]) - 1], parts[0])
    except Exception:
        return value


def open_media_info_window(media):
    try:
        xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
        media = tmdb.details(media.get('media_type'), media.get('id'))
    except Exception as error:
        xbmcgui.Dialog().notification(
            paths.ADDON_NAME,
            'TMDB error: %s' % error,
            paths.ICON_PATH,
            3500
        )
        return
    finally:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')

    window = MovieInfoWindow(media) if media.get('media_type') == 'movie' else MediaInfoWindow(media)
    window.doModal()
    del window


def open_episode_info_window(show, season):
    try:
        xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
        window = EpisodeInfoWindow(show, season)
    except Exception as error:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
        xbmcgui.Dialog().notification(
            paths.ADDON_NAME,
            'TMDB error: %s' % error,
            paths.ICON_PATH,
            3500
        )
        return
    xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
    window.doModal()
    del window
