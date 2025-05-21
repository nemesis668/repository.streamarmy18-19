from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
from six.moves.urllib.parse import parse_qs, quote_plus, urlparse, parse_qsl, urljoin
from six import PY2
from resources.lib.modules import lover
from resources.lib.modules import utils
from resources.lib.modules import helper
import log_utils
import kodi
import client
import dom_parser2, os,re,requests
from bs4 import BeautifulSoup
translatePath = xbmc.translatePath if PY2 else xbmcvfs.translatePath
buildDirectory = utils.buildDir #CODE BY NEMZZY AND ECHO
dialog = xbmcgui.Dialog()
filename     = os.path.basename(__file__).split('.')[0]
base_domain  = 'https://www.youporn.com'
base_name    = base_domain.replace('www.',''); base_name = re.findall('(?:\/\/|\.)([^.]+)\.',base_name)[0].title()
type         = 'video'
menu_mode    = 240
content_mode = 241
player_mode  = 801

search_tag   = 1
search_base  = urljoin(base_domain,'search/?query=%s')

@utils.url_dispatcher.register('%s' % menu_mode)
def menu():

    lover.checkupdates()

    try:
        url = urljoin(base_domain,'categories')
        c = client.request(url)
        soup = BeautifulSoup(c,'html.parser')
        r = soup.find('div', class_={'categoriesList tm_categoriesList'})
        if ( not r ):
            log_utils.log('Scraping Error in %s:: Content of request: %s' % (base_name.title(),str(c)), log_utils.LOGERROR)
            kodi.notify(msg='Scraping Error: Info Added To Log File', duration=6000, sound=True)
            quit()
    except Exception as e:
        log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)
        kodi.notify(msg='Fatal Error', duration=4000, sound=True)
        quit()

    dirlst = []

    for a in r.find_all('a'):
        try:
            url2 = a['href']
            if not base_domain in url2: url2 = base_domain+url2
            icon = a.img['data-src']
            title = url2.split('category/')[1].replace('/','').title()
            if not base_domain in url2: url2 = base_domain + url2
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': title, 'url': url2, 'mode': content_mode, 'icon': icon, 'fanart': fanarts, 'folder': True})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(),base_name.title(),str(e)), log_utils.LOGERROR)

    if dirlst: buildDirectory(dirlst)    
    else:
        kodi.notify(msg='No Menu Items Found')
        quit()

@utils.url_dispatcher.register('%s' % content_mode,['url'],['searched'])
def content(url,searched=False):
    #dialog.ok("URL",str(url))
    try:
        c = client.request(url)
        soup = BeautifulSoup(c, 'html5lib')
        r = soup.find_all('div', class_={'video-box pc js_video-box thumbnail-card js-pop'})
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
            name = i.img['alt']
            url2 = i.a['href']
            if not base_domain in url2: url2 = base_domain+url2
            icon = i.img['data-src']
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': name, 'url': url2, 'mode': player_mode, 'icon': icon, 'fanart': fanarts, 'description': name, 'folder': False})
        except Exception as e:
            pass
            #log_utils.log('Error: %s' % str(e), log_utils.LOGERROR)
    if dirlst: buildDirectory(dirlst, stopend=True, isVideo = True, isDownloadable = True)
    else:
        if (not searched):
            kodi.notify(msg='No Content Found')
            quit()
        
    if searched: return str(len(r))

    if not searched:
        
        try:
            search_pattern = '''\<link\s*rel\=['"]next['"]\s*href\=['"]([^'"]+)'''
            parse = base_domain        
            helper.scraper().get_next_page(content_mode,url,search_pattern,filename)
        except Exception as e: 
            log_utils.log('Error getting next page for %s :: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)