from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
from six.moves.urllib.parse import parse_qs, quote_plus, urlparse, parse_qsl, urljoin
from six import PY2
from resources.lib.modules import lover
from resources.lib.modules import utils
from resources.lib.modules import helper
import log_utils
import kodi
import client
import dom_parser2, os,re
from bs4 import BeautifulSoup
dialog = xbmcgui.Dialog()
buildDirectory = utils.buildDir #CODE BY NEMZZY AND ECHO
translatePath = xbmc.translatePath if PY2 else xbmcvfs.translatePath
filename     = os.path.basename(__file__).split('.')[0]
base_domain  = 'http://collectionofbestporn.com'
base_name    = base_domain.replace('www.',''); base_name = re.findall('(?:\/\/|\.)([^.]+)\.',base_name)[0].title()
type         = 'video'
menu_mode    = 254
content_mode = 255
player_mode  = 801

search_tag   = 1
search_base  = urljoin(base_domain,'search/%s')

@utils.url_dispatcher.register('%s' % menu_mode)
def menu():
    
    lover.checkupdates()
    
    try:
        url = urljoin(base_domain, 'channels')
        c = client.request(url)
        r = dom_parser2.parse_dom(c, 'div', {'class': 'video-thumb'})
        r = [(dom_parser2.parse_dom(i, 'a', req='href'), \
             dom_parser2.parse_dom(i, 'img', req=['src','alt'])) \
            for i in r]
        r = [(i[0][0].attrs['href'], i[1][0].attrs['alt'], i[1][0].attrs['src']) for i in r if i]
        if ( not r ):
            log_utils.log('Scraping Error in %s:: Content of request: %s' % (base_name.title(),str(c)), log_utils.LOGERROR)
            kodi.notify(msg='Scraping Error: Info Added To Log File', duration=6000, sound=True)
            quit()
    except Exception as e:
        log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)
        kodi.notify(msg='Fatal Error', duration=4000, sound=True)
        quit()

    dirlst = []
    
    for i in r:
        try:
            if PY2: name = kodi.sortX(i[1].encode('utf-8'))
            else: name = kodi.sortX(i[1])
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': name, 'url': i[0], 'mode': content_mode, 'icon': i[2], 'fanart': fanarts, 'folder': True})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(),base_name.title(),str(e)), log_utils.LOGERROR)
    
    if dirlst: buildDirectory(dirlst)    
    else:
        kodi.notify(msg='No Menu Items Found')
        quit()
        
@utils.url_dispatcher.register('%s' % content_mode,['url'],['searched'])
def content(url,searched=False):

    try:
        url = url.replace('+','-')
        c = client.request(url)
        soup = BeautifulSoup(c,'html.parser')
        r = soup.find_all('div', class_={'video-thumb'})
        if ( not r ) and ( not searched ):
            log_utils.log('Scraping Error in %s:: Content of request: %s' % (base_name.title(),str(c)), log_utils.LOGERROR)
            kodi.notify(msg='Scraping Error: Info Added To Log File', duration=6000, sound=True)
    except Exception as e:
        if ( not searched ):
            log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)
            kodi.notify(msg='Fatal Error', duration=4000, sound=True)
            quit()    
        else: pass
    
    dirlst = []
        
    for i in r:
        try:
            name = i.img['title']
            content_url = i.a['href']
            icon = i.img['src']
            icon = icon+'|verifypeer=false'
            time = i.find('span', class_={'time'}).text
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': name + '[COLOR yellow] | ' + time + '[/COLOR]', 'url': content_url, 'mode': player_mode, 'icon': icon, 'fanart': fanarts, 'description': name, 'folder': False})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (name.title(),base_name.title(),str(e)), log_utils.LOGERROR)
    
    if dirlst: buildDirectory(dirlst, stopend=True, isVideo = True, isDownloadable = True)
    else:
        if (not searched):
            kodi.notify(msg='No Content Found')
            quit()
        
    if searched: return str(len(r))
    
    if not searched:
        try:
            search_pattern = '''<link rel="next" href="(.*?)"'''
            helper.scraper().get_next_page(content_mode,url,search_pattern,filename)
        except Exception as e: 
            log_utils.log('Error getting next page for %s :: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)