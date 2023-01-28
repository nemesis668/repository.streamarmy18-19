from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
from six.moves.urllib.parse import parse_qs, quote_plus, urlparse, parse_qsl, urljoin

import os,re,time
from six import PY2
if PY2:
    import adultresolver
    import linkfinder
else:
    from resources.lib.modules import adultresolver
    from resources.lib.modules import linkfinder
adultresolver = adultresolver.streamer()
dialog = xbmcgui.Dialog()
def Blacklistcheck(url):
    dialog.notification('XXX-O-DUS', '[COLOR yellow]Checking For Links Now, Be Patient[/COLOR]', xbmcgui.NOTIFICATION_INFO, 2500)
    if 'hclips.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'chaturbate.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'zzcartoon.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'daftporn.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'watchxxxfreeinhd.com' in url:
        linkfinder.find(url)
        quit()
    elif 'youngpornvideos.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'freeomovie.info' in url:
        adultresolver.resolve(url)
        quit()
    elif 'javhihi.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'txxx.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'vrsumo.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'anysex.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'pandamovie.info' in url:
        adultresolver.resolve(url)
        quit()
    elif 'streamingporn.xyz' in url:
        adultresolver.resolve(url)
        quit()
    elif '3movs.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'watchmygf.me' in url:
        adultresolver.resolve(url)
        quit()
    elif 'vrsmash.com' in url:
        adultresolver.resolve(url)
        quit()
    elif '4tube.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'justporno.tv' in url:
        adultresolver.resolve(url)
        quit()
    elif 'spankbang.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'teenpornsite.net' in url:
        adultresolver.resolve(url)
        quit()
    elif 'watchpornfree.info' in url:
        adultresolver.resolve(url)
        quit()
    elif 'pornhd.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'hqporner.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'porn.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'porndig.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'youporn.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'pornrox.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'collectionofbestporn.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'ghettotube.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'siska.video' in url:
        adultresolver.resolve(url)
        quit()
    elif 'overthumbs.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'fapality.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'xxxdan.com' in url:
        adultresolver.resolve(url)
        quit()
    elif 'motherless.com' in url:
        adultresolver.resolve(url)
        quit()
    else:
        return url
		