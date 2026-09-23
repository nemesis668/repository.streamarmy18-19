from __future__ import absolute_import

import json
import os
import sys
import threading
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pyxbmct
import xbmc
import xbmcgui
import xbmcplugin

from resources.lib.core import paths
from resources.lib.core import presence
from resources.lib.gui.sections import open_section


TMDB_API_KEY = '5135334daa33251bc407e5f24cb1c6a5'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w500'

LIVE_NOW_LAYOUT = (22, 42, 36, 42)

CAROUSEL_MOVIES = 20
CAROUSEL_SHOWS = 20

TMDB_CAROUSEL_LAYOUT = (
    (64, 42, 22, 9),
    (64, 53, 22, 9),
    (64, 64, 22, 9),
    (64, 75, 22, 9),
)

SECTION_LAYOUT = (
    ('Sports', 22, 3, 18, 10),
    ('Movies & Shows', 22, 15, 18, 10),
    ('Cartoons & Anime', 42, 3, 18, 10),
    ('Music', 42, 15, 18, 10),
    ('XXX', 62, 3, 18, 10),
    ('Community Lists', 62, 15, 18, 10),
)

SECTION_ART = {
    'Sports': (paths.SPORTS_BUTTON_PATH, paths.SPORTS_BUTTON_FOCUS_PATH),
    'XXX': (paths.ADULT_BUTTON_PATH, paths.ADULT_BUTTON_FOCUS_PATH),
    'Movies & Shows': (paths.MS_BUTTON_PATH, paths.MS_BUTTON_FOCUS_PATH),
    'Music': (paths.MUSIC_BUTTON_PATH, paths.MUSIC_BUTTON_FOCUS_PATH),
    'Cartoons & Anime': (paths.AC_BUTTON_PATH, paths.AC_BUTTON_FOCUS_PATH),
    'Community Lists': (paths.CL_BUTTON_PATH, paths.CL_BUTTON_FOCUS_PATH),
}


class ColossusHomeWindow(pyxbmct.AddonFullWindow):
    def __init__(self):
        super(ColossusHomeWindow, self).__init__('Colossus')
        self.quit_requested = False
        self.carousel_items = self.load_tmdb_carousel()
        self.carousel_start = 0
        self.carousel_images = []
        self.carousel_buttons = []
        self.carousel_glows = []
        self.live_now_event = None
        self.live_now_placeholder = None
        self.live_now_label = None
        self.live_now_fill = None
        self.live_now_image = None
        self.live_now_caption = None
        self.live_now_frame = None
        self.live_now_glow = None
        self.live_now_button = None
        self.section_buttons = {}
        self.section_images = {}
        self.section_layout = self.visible_section_layout()
        self.utility_buttons = {}
        self.reopen = False
        self.setGeometry(1280, 720, 100, 100)
        self.hide_default_chrome()
        self.connect(pyxbmct.ACTION_NAV_BACK, self.quit_addon)
        self.set_controls()
        self.set_navigation()
        self._start_live_now_loader()

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

    def doModal(self):
        xbmcgui.Window.show(self)
        xbmc.sleep(200)
        self.focus_sports()
        self._schedule_focus_sports()
        xbmcgui.Window.doModal(self)

    def _schedule_focus_sports(self):
        def later():
            monitor = xbmc.Monitor()
            for wait in (0.1, 0.25, 0.5):
                if monitor.waitForAbort(wait) or self.quit_requested:
                    return
                try:
                    self.focus_sports()
                except Exception:
                    return

        thread = threading.Thread(target=later)
        thread.daemon = True
        thread.start()

    def focus_sports(self):
        sports = self.section_buttons.get('Sports')
        if sports is None:
            return
        try:
            self.setFocus(sports)
        except Exception:
            try:
                self.setFocusId(sports.getId())
            except Exception:
                pass
        self.update_section_art(focused=sports)
        self.update_live_now_art()
        self.update_focus_rings()

    def set_controls(self):
        self.add_background()
        self.add_section_buttons()
        self.add_live_now_button()
        self.add_featured_label()
        self.add_carousel_buttons()
        self.add_utility_buttons()

        self.version_label = xbmcgui.ControlLabel(
            28,
            684,
            280,
            28,
            'Version %s' % paths.ADDON.getAddonInfo('version'),
            textColor='0xFFFFFFFF'
        )
        self.addControl(self.version_label)

    def add_background(self):
        try:
            background_path = paths.BACKDROP2_PATH
            if not os.path.exists(background_path):
                background_path = paths.BACKDROP_PATH
            if not os.path.exists(background_path):
                background_path = paths.FANART_PATH
            self.background = xbmcgui.ControlImage(
                0,
                0,
                1280,
                720,
                background_path
            )
            self.addControl(self.background)
        except Exception:
                                                                           
            pass

    def visible_section_layout(self):
        if paths.ADDON.getSetting('disable_adult') != 'true':
            return SECTION_LAYOUT
        return tuple(item for item in SECTION_LAYOUT if item[0] != 'XXX')

    def add_section_buttons(self):
        self.section_images = {}
        for section_name, row, column, height, width in self.section_layout:
            button = self.create_section_button(section_name)
            self.section_buttons[section_name] = button
            self.placeControl(button, row, column, height, width, pad_x=0, pad_y=0)
            self.connect(button, self.make_section_opener(section_name))

    def add_utility_buttons(self):
        normal = paths.SETTINGS_BUTTON_PATH
        focused = paths.SETTINGS_BUTTON_FOCUS_PATH
        if not os.path.exists(focused):
            focused = normal
        self.utility_buttons['Settings'] = pyxbmct.Button(
            '',
            noFocusTexture=normal,
            focusTexture=focused
        )
        self.placeControl(self.utility_buttons['Settings'], 3, 90, 12, 7, pad_x=0, pad_y=0)
        self.connect(self.utility_buttons['Settings'], self.open_settings)

    def add_live_now_button(self):
        row, column, height, width = LIVE_NOW_LAYOUT
        placeholder = paths.LIVE_NOW_BUTTON_PATH if os.path.exists(paths.LIVE_NOW_BUTTON_PATH) else ''

        if placeholder:
            self.live_now_placeholder = pyxbmct.Image(placeholder, aspectRatio=0)
            self.placeControl(self.live_now_placeholder, row, column, height, width, pad_x=0, pad_y=0)

        if os.path.exists(paths.LIVE_NOW_FILL_PATH):
            self.live_now_fill = pyxbmct.Image(paths.LIVE_NOW_FILL_PATH, aspectRatio=0)
            self.placeControl(self.live_now_fill, row, column, height, width, pad_x=0, pad_y=0)
            self.live_now_fill.setVisible(False)

        self.live_now_image = pyxbmct.Image(paths.ICON_PATH, aspectRatio=0)
        self.placeControl(self.live_now_image, row, column, height, width, pad_x=0, pad_y=0)
        self.live_now_image.setVisible(False)

        if os.path.exists(paths.LIVE_NOW_CAPTION_PATH):
            self.live_now_caption = pyxbmct.Image(paths.LIVE_NOW_CAPTION_PATH, aspectRatio=0)
            self.placeControl(self.live_now_caption, row, column, height, width, pad_x=0, pad_y=0)
            self.live_now_caption.setVisible(False)

        frame_path = paths.LIVE_NOW_FRAME_PATH if os.path.exists(paths.LIVE_NOW_FRAME_PATH) else ''
        if frame_path:
            self.live_now_frame = pyxbmct.Image(frame_path, aspectRatio=0)
            self.placeControl(self.live_now_frame, row, column, height, width, pad_x=0, pad_y=0)
            self.live_now_frame.setVisible(False)

        self.live_now_label = pyxbmct.Label(
            '[B]NOTHING LIVE[/B]',
            font='font30',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_CENTER
        )
        self.placeControl(self.live_now_label, row + height - 10, column + 1, 8, width - 2, pad_x=0, pad_y=0)
        self.live_now_label.setVisible(False)

        if os.path.exists(paths.LIVE_GLOW_PATH):
            self.live_now_glow = pyxbmct.Image(paths.LIVE_GLOW_PATH, aspectRatio=0)
            self.placeControl(self.live_now_glow, row, column, height, width, pad_x=-22, pad_y=-22)
            self.live_now_glow.setVisible(False)

        blank = paths.BLANK_TEXTURE_PATH if os.path.exists(paths.BLANK_TEXTURE_PATH) else ''
        self.live_now_button = pyxbmct.Button(
            '',
            noFocusTexture=blank,
            focusTexture=blank
        )
        self.placeControl(self.live_now_button, row, column, height, width, pad_x=0, pad_y=0)
        self.connect(self.live_now_button, self.open_live_now)

    def add_featured_label(self):
        self.featured_label = pyxbmct.Label(
            '[B]FEATURED[/B]',
            font='font12',
            textColor='0xFFFFFFFF',
            alignment=pyxbmct.ALIGN_RIGHT + pyxbmct.ALIGN_CENTER_Y
        )
        self.placeControl(self.featured_label, 64, 26, 22, 14, pad_x=0, pad_y=0)

    def _start_live_now_loader(self):
        thread = threading.Thread(target=self._load_live_now_in_background)
        thread.daemon = True
        thread.start()

    def _load_live_now_in_background(self):
        event = None
        try:
            from resources.lib.gui.sports import load_live_now_event
            event = load_live_now_event(timeout=7)
        except Exception:
            event = None
        self._apply_live_now_event(event)

    def _apply_live_now_event(self, event):
        self.live_now_event = event if event and event.get('poster') else None
        has_live = bool(self.live_now_event and os.path.exists(self.live_now_event.get('poster') or ''))
        try:
            if has_live:
                poster = self.live_now_event['poster']
                if self.live_now_image:
                    self.live_now_image.setImage(poster)
                    self.live_now_image.setVisible(True)
                if self.live_now_caption:
                    self.live_now_caption.setVisible(True)
                if self.live_now_fill:
                    self.live_now_fill.setVisible(True)
                if self.live_now_frame:
                    self.live_now_frame.setVisible(False)
                if self.live_now_placeholder:
                    self.live_now_placeholder.setVisible(False)
                if self.live_now_label:
                    self.live_now_label.setVisible(False)
            else:
                if self.live_now_fill:
                    self.live_now_fill.setVisible(False)
                if self.live_now_image:
                    self.live_now_image.setVisible(False)
                if self.live_now_caption:
                    self.live_now_caption.setVisible(False)
                if self.live_now_frame:
                    self.live_now_frame.setVisible(False)
                if self.live_now_placeholder:
                    self.live_now_placeholder.setVisible(True)
                if self.live_now_label:
                    self.live_now_label.setVisible(True)
            self.update_live_now_art()
        except Exception:
            pass

    def add_carousel_buttons(self):
        for index, (row, column, height, width) in enumerate(TMDB_CAROUSEL_LAYOUT):
            item = self.get_carousel_item(index)
            poster = item.get('poster', '') if item else ''
            image = pyxbmct.Image(poster or paths.ICON_PATH, aspectRatio=0)
            self.carousel_images.append(image)
            self.placeControl(image, row, column, height, width)

            if os.path.exists(paths.FEATURED_GLOW_PATH):
                glow = pyxbmct.Image(paths.FEATURED_GLOW_PATH, aspectRatio=0)
                self.placeControl(glow, row, column, height, width, pad_x=-18, pad_y=-18)
                glow.setVisible(False)
                self.carousel_glows.append(glow)

            button = self.create_carousel_button(item)
            self.carousel_buttons.append(button)
            self.placeControl(button, row, column, height, width)
            self.connect(button, lambda index=index: self.open_visible_carousel_item(index))

    def section_art_paths(self, section_name):
        art = SECTION_ART.get(section_name)
        if not art:
            return None
        normal, focused = art
        if not os.path.exists(normal):
            return None
        if not os.path.exists(focused):
            focused = normal
        return (normal, focused)

    def create_section_button(self, section_name):
        art = self.section_art_paths(section_name)
        if art:
            normal, focused = art
            return pyxbmct.Button(
                '',
                noFocusTexture=normal,
                focusTexture=focused
            )

        label = section_name.upper()
        if section_name == 'Movies & Shows':
            label = 'MOVIES &\nSHOWS'
        elif section_name == 'Cartoons & Anime':
            label = 'CARTOONS &\nANIME'
        elif section_name == 'Community Lists':
            label = 'COMMUNITY\nLISTS'
        return pyxbmct.Button('[B]%s[/B]' % label)

    def create_carousel_button(self, item):
        blank = paths.BLANK_TEXTURE_PATH if os.path.exists(paths.BLANK_TEXTURE_PATH) else ''
        return pyxbmct.Button(
            '',
            noFocusTexture=blank,
            focusTexture=blank
        )

    def get_carousel_item(self, index):
        if not self.carousel_items:
            fallback = ['Top Movie', 'Top Show', 'Top Movie', 'Top Show']
            return {'title': fallback[index], 'media_type': 'placeholder'}
        return self.carousel_items[(self.carousel_start + index) % len(self.carousel_items)]

    def open_visible_carousel_item(self, index):
        self.open_carousel_item(self.get_carousel_item(index))

    def open_carousel_item(self, item):
        if not item or item.get('media_type') not in ('movie', 'tv'):
            return
        from resources.lib.gui.movies import open_media_from_home
        open_media_from_home(item)

    def open_live_now(self):
        event = self.live_now_event or {}
        if event.get('channels'):
            from resources.lib.gui.sports import open_event_sources
            open_event_sources(event)
            return
        xbmcgui.Dialog().ok(paths.ADDON_NAME, 'No events live currently.')

    def open_settings(self):
        from resources.lib.core import adult_lock
        adult_lock.sync_reset_label()
        before = paths.ADDON.getSetting('disable_adult')
        lock_before = paths.ADDON.getSetting('protect_adult') == 'true'
        adult_lock.mark_settings_session(True)
        try:
            paths.ADDON.openSettings()
        finally:
            adult_lock.mark_settings_session(False)
        adult_lock.confirm_disable(lock_before)
        turned_lock_on = (not lock_before) and paths.ADDON.getSetting('protect_adult') == 'true'
        if turned_lock_on and adult_lock.has_password():
            adult_lock.arm()
        if turned_lock_on and not adult_lock.has_password():
            if not adult_lock.create_password() and not adult_lock.has_password():
                paths.ADDON.setSetting('protect_adult', 'false')
                xbmcgui.Dialog().ok(
                    paths.ADDON_NAME,
                    'Password protect adult was turned off because no password was set.'
                )
        if paths.ADDON.getSetting('disable_adult') != before:
            self.reopen = True
            self.close()

    def rotate_carousel(self, direction, focus_index):
        if not self.carousel_items:
            return

        self.carousel_start = (self.carousel_start + direction) % len(self.carousel_items)
        for index, image in enumerate(self.carousel_images):
            item = self.get_carousel_item(index)
            poster = item.get('poster', '') if item else ''
            image.setImage(poster or paths.ICON_PATH)

        try:
            self.setFocus(self.carousel_buttons[focus_index])
        except Exception:
            pass

    def load_tmdb_carousel(self):
        try:
            movie_items = self.fetch_tmdb_items('movie', '/movie/popular', CAROUSEL_MOVIES)
            tv_items = self.fetch_tmdb_items('tv', '/tv/popular', CAROUSEL_SHOWS)
            return self.interleave_tmdb_items(movie_items, tv_items)
        except Exception:
            return []

    def interleave_tmdb_items(self, movie_items, tv_items):
        items = []
        for index in range(max(len(movie_items), len(tv_items))):
            if index < len(movie_items):
                items.append(movie_items[index])
            if index < len(tv_items):
                items.append(tv_items[index])
        return items

    def fetch_tmdb_items(self, media_type, endpoint, limit):
        params = urlencode({
            'api_key': TMDB_API_KEY,
            'language': 'en-US',
            'page': '1'
        })
        url = '%s%s?%s' % (TMDB_BASE_URL, endpoint, params)
        request = Request(url, headers={'User-Agent': 'Colossus/0.0.1'})
        response = urlopen(request, timeout=8)
        data = json.loads(response.read().decode('utf-8'))

        items = []
        for raw_item in data.get('results', [])[:limit]:
            title = raw_item.get('title') or raw_item.get('name') or 'TMDB'
            poster = self.cache_tmdb_poster(media_type, raw_item.get('id'), raw_item.get('poster_path'))
            items.append({
                'id': raw_item.get('id'),
                'title': title,
                'media_type': media_type,
                'poster': poster
            })
        return items

    def cache_tmdb_poster(self, media_type, tmdb_id, poster_path):
        if not poster_path or not tmdb_id:
            return ''

        cache_dir = os.path.join(paths.PROFILE_PATH, 'tmdb_posters')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        extension = os.path.splitext(poster_path)[1] or '.jpg'
        poster_file = os.path.join(cache_dir, '%s_%s%s' % (media_type, tmdb_id, extension))
        if os.path.exists(poster_file):
            return poster_file

        request = Request(TMDB_IMAGE_BASE + poster_path, headers={'User-Agent': 'Colossus/0.0.1'})
        response = urlopen(request, timeout=8)
        with open(poster_file, 'wb') as poster:
            poster.write(response.read())
        return poster_file

    def make_section_opener(self, section_name):
        return lambda: open_section(section_name)

    def quit_addon(self):
        self.quit_requested = True
        presence.stop()
        self.close()

    def onAction(self, action):
        try:
            action_id = action.getId()
        except Exception:
            action_id = action

        if action_id in (pyxbmct.ACTION_PREVIOUS_MENU, pyxbmct.ACTION_NAV_BACK):
            self.quit_addon()
            return

        try:
            focused_id = self.getFocusId()
        except Exception:
            focused_id = None

        if not focused_id:
            self.focus_sports()
            return

        if (
            action_id == pyxbmct.ACTION_MOVE_RIGHT
            and self.carousel_buttons
            and focused_id == self.carousel_buttons[-1].getId()
        ):
            self.rotate_carousel(1, len(self.carousel_buttons) - 1)
            return

        if (
            action_id == pyxbmct.ACTION_MOVE_LEFT
            and self.carousel_buttons
            and focused_id == self.carousel_buttons[0].getId()
        ):
            self.rotate_carousel(-1, 0)
            return

        super(ColossusHomeWindow, self).onAction(action)
        self.update_section_art()
        self.update_live_now_art()
        self.update_focus_rings()

    def update_live_now_art(self):
        has_live = bool(
            self.live_now_event
            and os.path.exists((self.live_now_event or {}).get('poster') or '')
        )
        if has_live:
            if self.live_now_placeholder:
                try:
                    self.live_now_placeholder.setVisible(False)
                except Exception:
                    pass
            if self.live_now_label:
                try:
                    self.live_now_label.setVisible(False)
                except Exception:
                    pass
            if self.live_now_caption:
                try:
                    self.live_now_caption.setVisible(True)
                except Exception:
                    pass
            if self.live_now_frame:
                try:
                    self.live_now_frame.setVisible(False)
                except Exception:
                    pass
            return

        if not self.live_now_placeholder:
            return
        normal = paths.LIVE_NOW_BUTTON_PATH
        if not os.path.exists(normal):
            return
        try:
            self.live_now_placeholder.setImage(normal)
            self.live_now_placeholder.setVisible(True)
            if self.live_now_caption:
                self.live_now_caption.setVisible(False)
            if self.live_now_label:
                self.live_now_label.setVisible(False)
        except Exception:
            pass

    def update_focus_rings(self):
        try:
            focused = self.getFocus()
        except Exception:
            focused = None
        if self.live_now_frame:
            try:
                self.live_now_frame.setVisible(False)
            except Exception:
                pass
        if self.live_now_glow:
            try:
                self.live_now_glow.setVisible(focused == self.live_now_button)
            except Exception:
                pass
        for glow, button in zip(self.carousel_glows, self.carousel_buttons):
            try:
                glow.setVisible(focused == button)
            except Exception:
                pass

    def update_section_art(self, focused=None):
        if focused is None:
            try:
                focused = self.getFocus()
            except Exception:
                focused = self.section_buttons.get('Sports')
        for section_name, image in self.section_images.items():
            art = self.section_art_paths(section_name)
            if not art:
                continue
            normal, selected = art
            try:
                image.setImage(selected if focused == self.section_buttons.get(section_name) else normal)
            except Exception:
                pass

    def set_navigation(self):
        sports = self.section_buttons['Sports']
        adult = self.section_buttons.get('XXX')
        movies = self.section_buttons['Movies & Shows']
        music = self.section_buttons['Music']
        anime = self.section_buttons['Cartoons & Anime']
        community = self.section_buttons['Community Lists']
        posters = self.carousel_buttons
        live_now = self.live_now_button
        settings = self.utility_buttons['Settings']

        settings.controlLeft(movies)
        settings.controlRight(settings)
        settings.controlUp(settings)
        settings.controlDown(live_now)

        sports.controlLeft(sports)
        sports.controlRight(movies)
        sports.controlUp(sports)
        sports.controlDown(anime)

        movies.controlLeft(sports)
        movies.controlRight(live_now)
        movies.controlUp(movies)
        movies.controlDown(music)

        anime.controlLeft(anime)
        anime.controlRight(music)
        anime.controlUp(sports)
        anime.controlDown(adult or community)

        music.controlLeft(anime)
        music.controlRight(live_now)
        music.controlUp(movies)
        music.controlDown(community)

        if adult is not None:
            adult.controlLeft(adult)
            adult.controlRight(community)
            adult.controlUp(anime)
            adult.controlDown(adult)

        community.controlLeft(adult or anime)
        community.controlRight(posters[0])
        community.controlUp(music)
        community.controlDown(community)

        live_now.controlLeft(movies)
        live_now.controlRight(live_now)
        live_now.controlUp(settings)
        live_now.controlDown(posters[0])

        for index, poster in enumerate(posters):
            poster.controlUp(live_now)
            poster.controlDown(poster)
            poster.controlLeft(posters[index - 1] if index else poster)
            poster.controlRight(posters[index + 1] if index < len(posters) - 1 else poster)


def _release_plugin():
    try:
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False, cacheToDisc=False)
    except Exception:
        pass


def _go_home():
    xbmc.executebuiltin('ReplaceWindow(Home)')


def run():
    from resources.lib.core import adult_lock
    adult_lock.sync_reset_label()
    adult_lock.start_guard()
    presence.stop()
    from resources.lib.gui.access import StartupCover, allow_entry
    cover = StartupCover()
    cover.present()
    _release_plugin()
    try:
        if not allow_entry():
            cover.close()
            cover = None
            _go_home()
            return
        presence.start()
        quit_requested = False
        try:
            while True:
                window = ColossusHomeWindow()
                xbmcgui.Window.show(window)
                xbmc.sleep(50)
                if cover is not None:
                    cover.close()
                    cover = None
                window.doModal()
                quit_requested = window.quit_requested
                reopen = window.reopen
                del window
                if not reopen:
                    break
        finally:
            presence.stop()
        if quit_requested:
            _go_home()
    finally:
        if cover is not None:
            cover.close()
