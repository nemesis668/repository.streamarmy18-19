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
dialog = xbmcgui.Dialog()
filename     = os.path.basename(__file__).split('.')[0]
base_domain  = 'https://www.porndig.com'
base_name    = base_domain.replace('www.',''); base_name = re.findall('(?:\/\/|\.)([^.]+)\.',base_name)[0].title()
type         = 'video'
menu_mode    = 246
content_mode = 247
player_mode  = 801
cookies = {'ctrcheck=':'1',
           'ctrenable=' : '1',
           'ctrcatenable=' : '1',
           'ctrgalenable=' : '1',
           'chtcnted=' : '1',
           'chtcnt=' : '1',
           'discl=' : '1'}
search_tag   = 0
search_base  = urljoin(base_domain,'/amateur/search/%s')
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
@utils.url_dispatcher.register('%s' % menu_mode)
def menu():
    
	lover.checkupdates()

	try:
		url = urljoin(base_domain,'video')
		c = requests.get(url,headers=headers,cookies=cookies).text
		r = dom_parser2.parse_dom(c, 'a', {'class': 'sidebar_section_item'})
		r = [i for i in r if 'channels' in i.attrs['href']]        
		r = [(urljoin(base_domain,i.attrs['href']), i.content + ' - [ Professional ]') for i in r]
		url = urljoin(base_domain,'amateur/videos/')
		c = client.request(url)
		e = dom_parser2.parse_dom(c, 'a', {'class': 'sidebar_section_item'})
		e = [i for i in e if 'channels' in i.attrs['href']]
		r += [(urljoin(base_domain,i.attrs['href']), i.content + ' - [ Amateur ]') for i in e]        
		r = sorted(r, key=lambda x: x[1])
		if ( not r ):
			log_utils.log('Scraping Error in %s:: Content of request: %s' % (base_name.title(),str(c)), log_utils.LOGERROR)
			kodi.notify(msg='Scraping Error: Info Added To Log File', duration=6000, sound=True)
			quit()
	except Exception as e:
		log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)
		kodi.notify(msg='Fatal Error', duration=4000, sound=True)
		quit()

	dirlst = []
	urls = []
	for i in r:
		try:
			name = i[1]
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
    #dialog.ok("URL",str(url))
    try:
        c = requests.get(url,headers=headers,cookies=cookies).text
        r = re.findall('data-post_id=(.*?)</section>',c,flags=re.DOTALL)
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
    #dialog.ok("R",str(r))
    for i in r:
        #dialog.ok("I",str(i))
        #quit()
        try:
            name = re.findall('alt="(.*?)"',i)[1]
            url = re.findall('href="(.*?)"',i)[0]
            if not base_domain in url: url = base_domain + url
            icon = re.findall('<img data-src="(.*?)"',i)[0]
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': name, 'url': url, 'mode': player_mode, 'icon': icon, 'fanart': fanarts, 'folder': False})
        except Exception as e:
            log_utils.log('Error adding menu item %s in %s:: Error: %s' % (i[1].title(),base_name.title(),str(e)), log_utils.LOGERROR)

    if dirlst: buildDirectory(dirlst, stopend=False, isVideo = True, isDownloadable = True)
    else:
        if (not searched):
            kodi.notify(msg='No Content Found')
            quit()
        
    if searched: return str(len(r))