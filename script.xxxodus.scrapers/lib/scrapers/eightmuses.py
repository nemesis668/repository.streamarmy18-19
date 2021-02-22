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
buildDirectory = utils.buildDir #CODE BY NEMZZY AND ECHO
translatePath = xbmc.translatePath if PY2 else xbmcvfs.translatePath
filename     = os.path.basename(__file__).split('.')[0]
base_domain  = 'https://www.8muses.com'
base_name    = base_domain.replace('www.',''); base_name = re.findall('(?:\/\/|\.)([^.]+)\.',base_name)[0].title()
type         = 'comics'

pic_men_mode = 756
comics_mode  = 757
pic_v_mode   = 805

@utils.url_dispatcher.register('%s' % pic_men_mode, ['url'])
def menu(url=None):
    
    try:
        if ( not url ): url = urljoin(base_domain,'comix/')
        c = client.request(url)
        r = dom_parser2.parse_dom(c, 'div', {'class': 'gallery'})
        r = dom_parser2.parse_dom(r, 'a', req='href')
        r = [i for i in r if 'login' not in i.attrs['href']]
        r = [(i.attrs['href'], \
              dom_parser2.parse_dom(i, 'img', req='data-src'), \
              dom_parser2.parse_dom(i, 'span', {'class': 'title-text'})) \
            for i in r if i]
        r = [(urljoin(base_domain,i[0]), i[2][0].content, i[1][0].attrs['data-src']) for i in r if i]
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
            else:name = kodi.sortX(i[1]).title()
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': name, 'url': i[0], 'mode': comics_mode, 'icon': i[2], 'fanart': fanarts, 'folder': True})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(),base_name.title(),str(e)), log_utils.LOGERROR)
    
    if dirlst:
        buildDirectory(dirlst, stopend=True, pictures=True)    
        search_pattern = '''<span\s*class=['"]next['"]>\s*<a\s*href=['"]([^'"]+)['"]>'''
        parse = base_domain
        helper.scraper().get_next_page(pic_men_mode,url,search_pattern,filename,parse,pictures=True)    
    else:
        kodi.notify(msg='No Menu Items Found')
        quit()
        
@utils.url_dispatcher.register('%s' % comics_mode, ['url'])
def comics(url=None):
    
    reload = False
    try:
        if ( not url ): url = urljoin(base_domain,'comix/')
        c = client.request(url)
        try:
            r = dom_parser2.parse_dom(c, 'div', {'class': 'gallery'})
            r = dom_parser2.parse_dom(r, 'a', req='href')
            r = [i for i in r if 'login' not in i.attrs['href']]
            r = [(i.attrs['href'], \
                  dom_parser2.parse_dom(i, 'img', req='data-src'), \
                  dom_parser2.parse_dom(i, 'span', {'class': 'title-text'})) \
                for i in r if i]
            r = [(urljoin(base_domain,i[0]), i[2][0].content, i[1][0].attrs['data-src']) for i in r if i]
            reload = True
        except:
            r = dom_parser2.parse_dom(c, 'div', {'class': 'gallery'})
            r = dom_parser2.parse_dom(r, 'a', req='href')
            r = [i for i in r if 'login' not in i.attrs['href']]
            r = [(i.attrs['href'], \
                  dom_parser2.parse_dom(i, 'img', req='data-src')) \
                for i in r if i]
            r = [(urljoin(base_domain,i[0]), i[1][0].attrs['data-src']) for i in r if i]
            reload = False
        if ( not r ):
            log_utils.log('Scraping Error in %s:: Content of request: %s' % (base_name.title(),str(c)), log_utils.LOGERROR)
            kodi.notify(msg='Scraping Error: Info Added To Log File', duration=6000, sound=True)
            quit()
    except Exception as e:
        log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)
        kodi.notify(msg='Fatal Error', duration=4000, sound=True)
        quit()
        
    dirlst = []
    
    if reload:
        for i in r:
            try:
                if PY2: name = kodi.sortX(i[1].encode('utf-8')).title()
                else: name = kodi.sortX(i[1]).title()
                fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
                dirlst.append({'name': name, 'url': i[0], 'mode': comics_mode, 'icon': i[2], 'fanart': fanarts, 'folder': True})
            except Exception as e:
                log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(),base_name.title(),str(e)), log_utils.LOGERROR)
    else:
        num = 1
        for i in r:
            try:
                name = 'Page %s'% str(num)
                fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
                dirlst.append({'name': name, 'url': i[0], 'mode': pic_v_mode, 'icon': i[1], 'fanart': fanarts, 'folder': False})
            except Exception as e:
                log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(),base_name.title(),str(e)), log_utils.LOGERROR)
            num += 1
            
    if dirlst:
        buildDirectory(dirlst, stopend=True, pictures=True)    
        search_pattern = '''<span\s*class=['"]next['"]>\s*<a\s*href=['"]([^'"]+)['"]>'''
        parse = base_domain
        helper.scraper().get_next_page(pic_men_mode,url,search_pattern,filename,parse,pictures=True)    
    else:
        kodi.notify(msg='No Menu Items Found')
        quit()
