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
Headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36' }
buildDirectory = utils.buildDir #CODE BY NEMZZY AND ECHO
dialog = xbmcgui.Dialog()
filename     = os.path.basename(__file__).split('.')[0]
base_domain  = 'https://watchpornfree.watch'
base_name    = base_domain.replace('www.',''); base_name = re.findall('(?:\/\/|\.)([^.]+)\.',base_name)[0].title()
type         = 'movies'
menu_mode    = 324
content_mode = 325
player_mode  = 801

search_tag   = 1
search_base  = urljoin(base_domain,'search/%s').replace(' ','+')

@utils.url_dispatcher.register('%s' % menu_mode)
def menu():
	url = 'https://watchpornfree.watch/'
	lover.checkupdates()
	content(url)
	# try:
		# url = base_domain
		# c = client.request(url)
		# r = re.findall('<header class="entry-header">(.*?)</h3>',c, flags=re.DOTALL)
	# except Exception as e:
		# log_utils.log('Fatal Error in %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)
		# kodi.notify(msg='Fatal Error', duration=4000, sound=True)
		# quit()
		
	# dirlst = []

	# for i in r:
		# try:
			# name = re.findall('rel="bookmark">(.*?)</a>',i,flags=re.DOTALL)[0]
			# url2 = re.findall('<a href="(.*?)"',i,flags=re.DOTALL)[0]
			# icon = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/icon.png' % base_name))
			# fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % base_name))
			# dirlst.append({'name': name, 'url': url2,'mode': content_mode, 'icon': icon, 'fanart': fanarts, 'folder': True})
		# except Exception as e:
			# log_utils.log('Error adding menu item. %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)

	# if dirlst: buildDirectory(dirlst)    
	# else:
		# kodi.notify(msg='No Menu Items Found')
		# quit()
	
        
@utils.url_dispatcher.register('%s' % content_mode,['url'],['searched'])
def content(url,searched=False):

    try:
        link = requests.get(url,headers=Headers).text
        soup = BeautifulSoup(link, 'html5lib')
        r = soup.find_all('div', class_={'product mb-4'})
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
            title = title.replace('Porn Movie Online Free','')
            url2 = i.a['href']
            if not base_domain in url2: url2 = base_domain+url2
            icon = i.img['src']
            fanarts = translatePath(os.path.join('special://home/addons/script.xxxodus.artwork', 'resources/art/%s/fanart.jpg' % filename))
            dirlst.append({'name': title, 'url': url2, 'mode': player_mode, 'icon': icon, 'fanart': fanarts, 'folder': False})
        except Exception as e:
            log_utils.log('Error adding menu item. %s:: Error: %s' % (base_name.title(),str(e)), log_utils.LOGERROR)
    if dirlst: buildDirectory(dirlst, stopend=True, isVideo = True, isDownloadable = True)
    else:
        if (not searched):
            kodi.notify(msg='No Content Found')
            quit()
        
    if searched: return str(len(r))

    if not searched:
        search_pattern = '''<a\s+class="next page-numbers".*?href=['"]([^'"]+)['"]'''
        parse = base_domain
        helper.scraper().get_next_page(content_mode,url,search_pattern,filename,parse)