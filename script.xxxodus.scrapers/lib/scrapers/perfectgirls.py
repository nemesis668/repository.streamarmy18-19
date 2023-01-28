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
base_domain  = 'http://www.perfectgirls.net'
base_name    = base_domain.replace('www.',''); base_name = re.findall('(?:\/\/|\.)([^.]+)\.',base_name)[0].title()
type         = 'video'
menu_mode    = 216
content_mode = 217
player_mode  = 801

search_tag   = 0
search_base  = urljoin(base_domain,'search/?q=%s')

@utils.url_dispatcher.register('%s' % menu_mode)
def menu():
    
    lover.checkupdates()
    
    try:
        url = base_domain
        c = client.request(url)
        r = dom_parser2.parse_dom(c, 'li', {'class': 'header-submenu__item'})
        r = dom_parser2.parse_dom(r, 'a', req='href')
        r = [(i.attrs['href'], \
            i.content)for i in r if i]
        r = [(urljoin(base_domain,i[0]),i[1]) for i in r if i]
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
            if PY2: name = kodi.sortX(i[1].encode('utf-8')).title()
            else: name = kodi.sortX(i[1]).title()
            icon = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/icon.png' % filename))
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': name, 'url': i[0], 'mode': content_mode, 'icon': icon, 'fanart': fanarts, 'folder': True})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(),base_name.title(),str(e)), log_utils.LOGERROR)
    
    if dirlst: buildDirectory(dirlst)    
    else:
        kodi.notify(msg='No Menu Items Found')
        quit()
        
@utils.url_dispatcher.register('%s' % content_mode,['url'],['searched'])
def content(url,searched=False):

    try:
        headers = {'User-Agent' : 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'}
        c = requests.get(url,headers=headers).text
        soup = BeautifulSoup(c,'html.parser')
        r = soup.find_all('div', class_={'list__item'})
        #dialog.ok("R",str(r))
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
            name = i.a['title']
            media_url = i.a['href']
            icon = i.img['data-original']
            icon = icon+'|verifypeer=false'
            if searched: description = 'Result provided by %s' % base_name.title()
            else: description = name
            if not 'http' in icon: icon='http:'+icon
            if not base_domain in media_url: media_url =  base_domain + media_url
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': name, 'url': media_url, 'mode': player_mode, 'icon': icon, 'fanart': fanarts, 'description': description, 'folder': False})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(),base_name.title(),str(e)), log_utils.LOGERROR)
    if dirlst: buildDirectory(dirlst, stopend=False, isVideo = True, isDownloadable = True)
    else:
        if (not searched):
            kodi.notify(msg='No Content Found')
            quit()
        
    if searched: return str(len(r))

    if not searched:
        
        try:
            pattern = r'''((?:http|https)(?:\:\/\/)(?:www)(?:\/\/|\.)(perfectgirls.net)\/(category\/)([0-9+]\/)(.+?\/))([0-9]+)'''
            r = re.search(pattern,url)
            base = r.group(1)
            search_pattern = '''<a\s*class=['"]btn_wrapper__btn['"]\s*href=['"]([^'"]+)['"]>Next'''
            parse = base         
            helper.scraper().get_next_page(content_mode,url,search_pattern,filename,parse)
        except Exception as e: 
            log_utils.log('Error getting next page for %s :: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)