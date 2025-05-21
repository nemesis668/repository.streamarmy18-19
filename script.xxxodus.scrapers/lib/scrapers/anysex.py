from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
from six.moves.urllib.parse import parse_qs, quote_plus, urlparse, parse_qsl, urljoin
from six import PY2
from resources.lib.modules import lover
from resources.lib.modules import utils
from resources.lib.modules import helper

import os,re
import client
import kodi
import dom_parser2
import log_utils
from bs4 import BeautifulSoup
translatePath = xbmc.translatePath if PY2 else xbmcvfs.translatePath
buildDirectory = utils.buildDir #CODE BY NEMZZY AND ECHO
dialog = xbmcgui.Dialog()
filename     = os.path.basename(__file__).split('.')[0]
base_domain  = 'https://anysex.com'
base_name    = base_domain.replace('www.',''); base_name = re.findall('(?:\/\/|\.)([^.]+)\.',base_name)[0].title()
type         = 'video'
menu_mode    = 404
content_mode = 405
player_mode  = 801

search_tag   = 0
search_base  = urljoin(base_domain,'search/?q=%s')

@utils.url_dispatcher.register('%s' % menu_mode)
def menu():

    lover.checkupdates()

    try:
        url = urljoin(base_domain,'/categories/')
        c = client.request(url)
        soup = BeautifulSoup(c, "html.parser")
        r = soup.find_all('div', class_={'item'})
    except Exception as e:
        log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)
        kodi.notify(msg='Fatal Error', duration=4000, sound=True)
        quit()
        
    dirlst = []

    for i in r:
        try:
            name = i.a['title']
            icon = i.img['src']
            url = i.a['href']
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % base_name))
            dirlst.append({'name': name, 'url': url,'mode': content_mode, 'icon': icon, 'fanart': fanarts, 'folder': True})
        except Exception as e:
            log_utils.log('Error adding menu item. %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)

    if dirlst: buildDirectory(dirlst)    
    else:
        kodi.notify(msg='No Menu Items Found')
        quit()

@utils.url_dispatcher.register('%s' % content_mode,['url'],['searched'])
def content(url,searched=False):

    try:
        c = client.request(url)
        soup = BeautifulSoup(c,'html.parser')
        r = soup.find_all('div', class_={'item'})
    except Exception as e:
        if ( not searched ):
            log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)
            kodi.notify(msg='Fatal Error', duration=4000, sound=True)
            quit()    
        else: pass
    dirlst = []
    for i in r:
        try:
            name = i.img['alt']
            url2 = i.a['href']
            if not base_domain in url2: url2 = base_domain + url2
            icon = i.img['data-jpg']
            try:
                time = i.find('span', class_={'time'}).text
            except:
                time = '?'
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': name + '[COLOR yellow] | ' + time + '[/COLOR]', 'url': url2, 'mode': player_mode, 'icon': icon, 'fanart': fanarts, 'folder': False})
        except Exception as e:
            log_utils.log('Error adding menu item. %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)
    if dirlst: buildDirectory(dirlst, stopend=True, isVideo = True, isDownloadable = True)
    else:
        if (not searched):
            kodi.notify(msg='No Content Found')
            quit()
        
    if searched: return str(len(r))

    if not searched:
        #dirlst = []
        try:
            currentp = re.findall(r'''/([0-9]+)/''',url)[0]
            np = int(currentp) + 1
            nextp = url.replace(currentp,str(np))
        except: nextp = url+'2/'
        npicon = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/main/next.png'))
        dirlst.append({'name': kodi.giveColor('Next Page -->','white'), 'url': nextp, 'mode': content_mode, 'icon': npicon, 'fanart': fanarts, 'description': 'Load More......', 'folder': True})
        if dirlst: buildDirectory(dirlst, stopend=True, isVideo = True, isDownloadable = True)
    xbmcplugin.endOfDirectory(kodi.syshandle, cacheToDisc=True)
