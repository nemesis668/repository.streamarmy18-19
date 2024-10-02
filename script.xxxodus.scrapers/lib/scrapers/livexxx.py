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
buildDirectory = utils.buildDir #CODE BY NEMZZY AND ECHO
translatePath = xbmc.translatePath if PY2 else xbmcvfs.translatePath
dialog = xbmcgui.Dialog()
filename     = os.path.basename(__file__).split('.')[0]
base_domain  = 'https://adult-tv-channels.com/?0'
base_name    = 'Live XXX Channels'#base_domain.replace('www.',''); base_name = re.findall('(?:\/\/|\.)([^.]+)\.',base_name)[0].title()
type         = 'livexxx'
menu_mode    = 330 
content_mode = 331
player_mode  = 801

search_tag   = 0
search_base  = urljoin(base_domain,'video/search?search=%s')

@utils.url_dispatcher.register('%s' % menu_mode)
def menu():
    lover.checkupdates()
    content(base_domain)
    # try:
        # url = base_domain
        # c = client.request(url)
        # soup = BeautifulSoup(c,'html.parser')
        # r = soup.find_all('figure', class_={'entry-item-thumb'})
        # if ( not r ):
            # log_utils.log('Scraping Error in %s:: Content of request: %s' % (base_name.title(),str(c)), log_utils.LOGERROR)
            # kodi.notify(msg='Scraping Error: Info Added To Log File', duration=6000, sound=True)
            # quit()
    # except Exception as e:
        # log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)
        # kodi.notify(msg='Fatal Error', duration=4000, sound=True)
        # quit()

    # dirlst = []

    # for i in r:
        # try:
            # chan_name = i.img['alt'].replace('official logo','').replace('channel logo','').replace('logo','').title()
            # chan_link = i.a['href']
            # chan_logo = i.img['src']
            # fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            # dirlst.append({'name': chan_name, 'url': chan_link, 'mode': content_mode, 'icon': chan_logo, 'fanart': fanarts, 'folder': True})
        # except Exception as e:
            # log_utils.log('Error adding menu item %s in %s:: Error: %s' % (name.title(),base_name.title(),str(e)), log_utils.LOGERROR)

    # if dirlst: buildDirectory(dirlst)    
    # else:
        # kodi.notify(msg='No Menu Items Found')
        # quit()
		
@utils.url_dispatcher.register('%s' % content_mode,['url'],['searched'])
def content(url,searched=False):
	
    try:
        c = client.request(url)
        soup = BeautifulSoup(c,'html.parser')
        r = soup.find_all('figure', class_={'entry-item-thumb'})
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
            chan_name = i.img['alt'].replace('official logo','').replace('channel logo','').replace('logo','').title()
            chan_link = i.a['href']
            chan_logo = i.img['src']
            if searched: description = 'Result provided by %s' % base_name.title()
            else: description = chan_name
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': chan_name, 'url': chan_link, 'mode': player_mode, 'icon': chan_logo, 'fanart': fanarts, 'description': description, 'folder': False})
        except Exception as e:
            log_utils.log('Error adding menu item PornHub:: Error: %s' % str(e), log_utils.LOGERROR)

    if dirlst: buildDirectory(dirlst, stopend=True, isVideo = True, isDownloadable = True)
    else:
        if (not searched):
            kodi.notify(msg='No Content Found')
            quit()
        
    if searched: return str(len(r))

    if not searched:
        
        try:
            search_pattern = '''['"]next page-numbers['"]\s*href\=['"]([^'"]+)'''
            parse = base_domain        
            helper.scraper().get_next_page(content_mode,url,search_pattern,filename)
        except Exception as e: 
            log_utils.log('Error getting next page for %s :: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)