from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
from six.moves.urllib.parse import parse_qs, quote_plus, urlparse, parse_qsl, urljoin
from six import PY2
from resources.lib.modules import lover
from resources.lib.modules import utils
from resources.lib.modules import helper
import log_utils
import kodi
import client
import time
import dom_parser2, os,re,requests
from resources.lib.modules import cfscrape
cloudflare = cfscrape.create_scraper()
buildDirectory = utils.buildDir #CODE BY NEMZZY AND ECHO
from bs4 import BeautifulSoup
dialog	= xbmcgui.Dialog()
translatePath = xbmc.translatePath if PY2 else xbmcvfs.translatePath
filename     = os.path.basename(__file__).split('.')[0]
base_domain  = 'https://spankbang.com'
base_name    = base_domain.replace('www.',''); base_name = re.findall('(?:\/\/|\.)([^.]+)\.',base_name)[0].title()
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.59"
headers = {'User-Agent': ua}
type         = 'video'
menu_mode    = 230
content_mode = 231
player_mode  = 801

search_tag   = 1
search_base  = urljoin(base_domain,'/s/%s/').replace(' ','%20')
@utils.url_dispatcher.register('%s' % menu_mode)

def menu():
    
    lover.checkupdates()

    try:
        url = urljoin(base_domain,'categories')
        c = cloudflare.get(url,headers=headers)
        soup = BeautifulSoup(c.text, 'html.parser')
        content = soup.find('ul', class_={'list'})
        if ( not content ):
            log_utils.log('Scraping Error in %s:: Content of request: %s' % (base_name.title(),str(c)), log_utils.LOGERROR)
            kodi.notify(msg='Scraping Error: Info Added To Log File', duration=6000, sound=True)
            quit()
    except Exception as e:
        log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)
        kodi.notify(msg='Fatal Error', duration=4000, sound=True)
        quit()
        
    dirlst = []

    for a in content.find_all('li'):
        try:
            title = a.text
            url2 = a.find('a', class_={'keyword'})['href']
            if not base_domain in url2: url2 = base_domain+url2
            icon = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/icon.png' % filename))
            #if not base_domain in icon: icon = base_domain+icon
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': title, 'url': url2, 'mode': content_mode, 'icon': icon, 'fanart': fanarts, 'folder': True})
        except Exception as e:
            log_utils.log('Error: %s' % str(e), log_utils.LOGERROR)

    if dirlst: buildDirectory(dirlst)    
    else:
        kodi.notify(msg='No Menu Items Found')
        quit()
        
@utils.url_dispatcher.register('%s' % content_mode,['url'],['searched'])
def content(url,searched=False):

    try:
        c = cloudflare.get(url,headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        content = soup.find('div', class_={'results results_search'})
        if ( not content ) and ( not searched ):
            log_utils.log('Scraping Error in %s:: Content of request: %s' % (base_name.title(),str(c)), log_utils.LOGERROR)
            kodi.notify(msg='Scraping Error: Info Added To Log File', duration=6000, sound=True)
    except Exception as e:
        if ( not searched ):
            log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)
            kodi.notify(msg='Fatal Error', duration=4000, sound=True)
            quit()    
        else: pass
        
    dirlst = []
        
    for a in content.find_all('a', class_={'thumb'}):
        try:
            title = a.img['alt'].title()
            url2 = a['href']
            if not base_domain in url2: url2=base_domain+url2
            icon = a.img['data-src']
            if not 'http' in icon: icon = 'https:'+icon
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': title, 'url': url2, 'mode': player_mode, 'icon': icon, 'fanart': fanarts, 'description': title, 'folder': False})
        except Exception as e:
            dialog.ok("E",str(e))
            log_utils.log('Error: %s' % str(e), log_utils.LOGERROR)

    if dirlst: buildDirectory(dirlst, stopend=True, isVideo = True, isDownloadable = True)
    else:
        if (not searched):
            kodi.notify(msg='No Content Found')
            quit()
        
    if searched: return str(len(r))

    if not searched:
        
        try:
            search_pattern = '''<li\s*class\=['"]next['"]\>\<a\s*href\=['"]([^'"]+)'''
            parse = base_domain        
            helper.scraper().get_next_page(content_mode,url,search_pattern,filename,parse)
        except Exception as e: 
            log_utils.log('Error getting next page for %s :: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)