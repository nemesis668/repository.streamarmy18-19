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
dialog = xbmcgui.Dialog()
buildDirectory = utils.buildDir #CODE BY NEMZZY AND ECHO
translatePath = xbmc.translatePath if PY2 else xbmcvfs.translatePath
filename     = os.path.basename(__file__).split('.')[0]
base_domain  = 'https://www.vrsmash.com'
base_name    = base_domain.replace('www.',''); base_name = re.findall('(?:\/\/|\.)([^.]+)\.',base_name)[0].title()
type         = 'vr'
menu_mode    = 284
content_mode = 285
player_mode  = 801
headers = {'User-Agent' : 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'}
search_tag   = 0
search_base  = urljoin(base_domain,'video/search?query=%s').replace(' ','+')

@utils.url_dispatcher.register('%s' % menu_mode)
def menu():
    
    lover.checkupdates()

    try:
        url = urljoin(base_domain,'category/all')
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        r = soup.find_all('div', class_={'tile tile-category'})
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
            title = i.find('div', class_={'tile-title'}).a.text
            media_url = i.find('div', class_={'tile-title'}).a['href']
            if base_domain not in media_url: media_url = base_domain+media_url
            icon = i.img['data-src']
            if base_domain not in icon: icon = base_domain+icon
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': title, 'url': media_url, 'mode': content_mode, 'icon': icon, 'fanart': fanarts, 'folder': True})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(),base_name.title(),str(e)), log_utils.LOGERROR)
    
    if dirlst: buildDirectory(dirlst)    
    else:
        kodi.notify(msg='No Menu Items Found')
        quit()
        
@utils.url_dispatcher.register('%s' % content_mode,['url'],['searched'])
def content(url,searched=False):

    try:
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        r = soup.find_all('div', class_={'tile-thumbnail'})
        if ( not r ) and ( not searched ):
            log_utils.log('Scraping Error in %s:: Content of request: %s' % (base_name.title(),str(c)), log_utils.LOGERROR)
            kodi.notify(msg='Scraping Error: Info Added To Log File', duration=6000, sound=True)
            quit()
    except Exception as e:
        if ( not searched ):
            log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)
            kodi.notify(msg='Fatal Error', duration=4000, sound=True)
            quit()    
        else: pass
        
    dirlst = []
    
    for i in r:
        try:
            title = i.img['alt']
            media_url = i.a['href']
            icon = i.img['data-src']
            if base_domain not in media_url: media_url = base_domain+media_url
            if base_domain not in icon: icon = base_domain+icon
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': title, 'url': media_url, 'mode': player_mode, 'icon': icon, 'fanart': fanarts, 'description': 'No Desc', 'folder': False})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[0].title(),base_name.title(),str(e)), log_utils.LOGERROR)
    
    if dirlst: buildDirectory(dirlst, stopend=True, isVideo = True, isDownloadable = True)
    else:
        if (not searched):
            kodi.notify(msg='No Content Found')
            quit()
        
    if searched: return str(len(r))
    
    if not searched:
        search_pattern = '''<li\s*class=['"]next['"]><a\s*href=['"]([^'"]+)'''
        parse = base_domain
        
        helper.scraper().get_next_page(content_mode,url,search_pattern,filename,parse)