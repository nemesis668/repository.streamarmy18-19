from __future__ import absolute_import

import os

import xbmc
import xbmcaddon
import xbmcvfs


ADDON_ID = 'plugin.video.colossus'
ADDON = xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME = ADDON.getAddonInfo('name') or 'Colossus'


def translate_path(path):
    if hasattr(xbmcvfs, 'translatePath'):
        return xbmcvfs.translatePath(path)
    return xbmc.translatePath(path)


ADDON_PATH = translate_path(ADDON.getAddonInfo('path'))
PROFILE_PATH = translate_path(ADDON.getAddonInfo('profile'))
ICON_PATH = os.path.join(ADDON_PATH, 'icon.gif')
FANART_PATH = os.path.join(ADDON_PATH, 'fanart.jpg')


def resource_path(*parts):
    return os.path.join(ADDON_PATH, 'resources', *parts)


MEDIA_PATH = resource_path('media')
TITLE_IMAGE_PATH = os.path.join(MEDIA_PATH, 'titleimg.png')
BACKDROP_PATH = os.path.join(MEDIA_PATH, 'backdrop.jpg')
BACKDROP2_PATH = os.path.join(MEDIA_PATH, 'backdrop2.png')
FEATURED_FOCUS_PATH = os.path.join(MEDIA_PATH, 'featured_focus.png')
BLANK_TEXTURE_PATH = os.path.join(MEDIA_PATH, 'blank.png')
LIVE_GLOW_PATH = os.path.join(MEDIA_PATH, 'live_glow.png')
FEATURED_GLOW_PATH = os.path.join(MEDIA_PATH, 'featured_glow.png')
FRAME_PATH = os.path.join(MEDIA_PATH, 'frame.png')
SPORTS_BUTTON_PATH = os.path.join(MEDIA_PATH, 'sports.png')
SPORTS_BUTTON_FOCUS_PATH = os.path.join(MEDIA_PATH, 'sportss.png')
ADULT_BUTTON_PATH = os.path.join(MEDIA_PATH, 'adult.png')
ADULT_BUTTON_FOCUS_PATH = os.path.join(MEDIA_PATH, 'adults.png')
MS_BUTTON_PATH = os.path.join(MEDIA_PATH, 'ms.png')
MS_BUTTON_FOCUS_PATH = os.path.join(MEDIA_PATH, 'mss.png')
MUSIC_BUTTON_PATH = os.path.join(MEDIA_PATH, 'music.png')
MUSIC_BUTTON_FOCUS_PATH = os.path.join(MEDIA_PATH, 'musics.png')
AC_BUTTON_PATH = os.path.join(MEDIA_PATH, 'ac.png')
AC_BUTTON_FOCUS_PATH = os.path.join(MEDIA_PATH, 'acs.png')
ANIME_PATH = os.path.join(MEDIA_PATH, 'anime.png')
ANIME_FOCUS_PATH = os.path.join(MEDIA_PATH, 'animes.png')
CARTOON_PATH = os.path.join(MEDIA_PATH, 'cartoon.png')
CARTOON_FOCUS_PATH = os.path.join(MEDIA_PATH, 'cartoons.png')
CL_BUTTON_PATH = os.path.join(MEDIA_PATH, 'cl.png')
CL_BUTTON_FOCUS_PATH = os.path.join(MEDIA_PATH, 'cls.png')
SETTINGS_BUTTON_PATH = os.path.join(MEDIA_PATH, 'settings.png')
SETTINGS_BUTTON_FOCUS_PATH = os.path.join(MEDIA_PATH, 'settingss.png')
LIVE_NOW_BUTTON_PATH = os.path.join(MEDIA_PATH, 'livenow.png')
LIVE_NOW_BUTTON_FOCUS_PATH = os.path.join(MEDIA_PATH, 'livenowtiles.png')
LIVE_NOW_FILL_PATH = os.path.join(MEDIA_PATH, 'livenow_fill.png')
LIVE_NOW_FRAME_PATH = os.path.join(MEDIA_PATH, 'livenow_frame.png')
LIVE_NOW_CAPTION_PATH = os.path.join(MEDIA_PATH, 'livenow_caption.png')
LIVE_NOW_FOCUS_PATH = os.path.join(MEDIA_PATH, 'livenow_focus.png')
MEDIA_DIM_PATH = os.path.join(MEDIA_PATH, 'media_dim.png')
SPORTS_LIVE_PATH = os.path.join(MEDIA_PATH, 'sports', 'livesports.png')
SPORTS_UPCOMING_PATH = os.path.join(MEDIA_PATH, 'sports', 'upcoming.png')
SPORTS_247_PATH = os.path.join(MEDIA_PATH, 'sports', '247.png')
WORLD_RADIO_PATH = os.path.join(MEDIA_PATH, 'worldradio.png')
WORLD_RADIO_FOCUS_PATH = os.path.join(MEDIA_PATH, 'worldradios.png')
MUSICAL_MOVIES_PATH = os.path.join(MEDIA_PATH, 'musicmovie.png')
MUSICAL_MOVIES_FOCUS_PATH = os.path.join(MEDIA_PATH, 'musicmovies.png')
PODCAST_PATH = os.path.join(MEDIA_PATH, 'podcast.png')
PODCAST_FOCUS_PATH = os.path.join(MEDIA_PATH, 'podcasts.png')
MP3_PATH = os.path.join(MEDIA_PATH, 'mp3.png')
MP3_FOCUS_PATH = os.path.join(MEDIA_PATH, 'mp3s.png')
XXX_SITES_PATH = os.path.join(MEDIA_PATH, 'sites.png')
XXX_SITES_FOCUS_PATH = os.path.join(MEDIA_PATH, 'sitess.png')
XXX_CAMS_PATH = os.path.join(MEDIA_PATH, 'cama.png')
XXX_CAMS_FOCUS_PATH = os.path.join(MEDIA_PATH, 'camas.png')
XXX_MOVIES_PATH = os.path.join(MEDIA_PATH, 'amovie.png')
XXX_MOVIES_FOCUS_PATH = os.path.join(MEDIA_PATH, 'amovies.png')
