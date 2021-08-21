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
buildDirectory = utils.buildDir #CODE BY NEMZZY AND ECHO
translatePath = xbmc.translatePath if PY2 else xbmcvfs.translatePath
filename     = os.path.basename(__file__).split('.')[0]
base_domain  = 'https://www.sexvr.com'
base_name    = base_domain.replace('www.',''); base_name = re.findall('(?:\/\/|\.)([^.]+)\.',base_name)[0].title()
type         = 'vr'
menu_mode    = 288
content_mode = 289
player_mode  = 801

search_tag   = 1
search_base  = urljoin(base_domain,'search/videos/%s/')

@utils.url_dispatcher.register('%s' % menu_mode)
def menu():
    
    lover.checkupdates()

    try:
        url = urljoin(base_domain,'channels/')
        c = client.request(url)
        r = dom_parser2.parse_dom(c, 'div', {'class': ['item-col','item--channel','col']})
        r = [(dom_parser2.parse_dom(i, 'a', req=['href','title']), \
              dom_parser2.parse_dom(i, 'img', req='src')) \
              for i in r if i]
        r = [(i[0][0].attrs['href'], i[0][0].attrs['title'], i[1][0].attrs['src'] \
            if i[1] else urljoin(base_domain,'core/images/catdefault.jpg')) for i in r[8:]]
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
        c = client.request(url)
        r = dom_parser2.parse_dom(c, 'div', {'class': ['item-col','col','popup','video-box','thumb-resize']})
        r = [(dom_parser2.parse_dom(i, 'a', req='href'), \
              dom_parser2.parse_dom(i, 'span', {'class': ['time','vr-yellow']}), \
              dom_parser2.parse_dom(i, 'img', req=['src','alt'])) \
              for i in r if i]
        r = [(i[0][0].attrs['href'], i[2][0].attrs['alt'], i[1][0].content, \
              i[2][0].attrs['src']) for i in r if i]
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
            if PY2:
                name = kodi.sortX(i[1].encode('utf-8'))
                name = name.title() + ' - [ %s ]' % kodi.sortX(i[2].encode('utf-8'))
            else:
                name = kodi.sortX(i[1])
                name = name.title() + ' - [ %s ]' % kodi.sortX(i[2])
            if searched: description = 'Result provided by %s' % base_name.title()
            else: description = name
            content_url = i[0] + '|SPLIT|%s' % base_name
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': name, 'url': content_url, 'mode': player_mode, 'icon': i[3], 'fanart': fanarts, 'description': description, 'folder': False})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[0].title(),base_name.title(),str(e)), log_utils.LOGERROR)
    
    if dirlst: buildDirectory(dirlst, stopend=True, isVideo = True, isDownloadable = True)
    else:
        if (not searched):
            kodi.notify(msg='No Content Found')
            quit()
        
    if searched: return str(len(r))
    
    if not searched:
        try: parse = re.findall('''<link\s*rel=['"]canonical['"]\s*href=['"]([^'"]+)''',r)[0]
        except: parse = base_domain
        search_pattern = '''<link\s*rel=['"]next['"]\s*href=['"]([^'"]+)'''        
        helper.scraper().get_next_page(content_mode,url,search_pattern,filename,parse)