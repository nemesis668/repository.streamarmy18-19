import re, requests, json
from kodi_six import xbmc, xbmcgui, xbmcaddon
from six import PY2
import random
dialog = xbmcgui.Dialog()
Notice = xbmc.LOGNOTICE if PY2 else xbmc.LOGINFO


class Scraper:
	def __init__(self):
		self.Base = 'https://eb2.srtaem.bar/embed/'
		self.Search = ('%s')
		self.links = []
	def Index(self,type,term,year,imdb):
		if type == 'MOVIE':
			try:
				import random
				ip = ".".join(map(str, (random.randint(0, 255) 
										for _ in range(4))))
				session = requests.Session()
				ref = ('https://eb2.srtaem.bar/embed/%s' % imdb)
				ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
				headers = {'User-Agent': ua,
				'Referer': ref,
				'X-Requested-With': 'XMLHttpRequest'}
				post_data = {'imdb': imdb,
				'ip': ip, 'hd' : 'false'}
				filmname = term.title()
				url = 'https://eb2.srtaem.bar/l1'
				link2 = session.post(url, data=post_data, headers=headers)
				data = json.loads(link2.text)
				#data = str(data)
				pattern = r'''src['"]:\su['"](.*?)['"].*?res.*?u['"](.*?)['"]'''
				sources = re.findall(pattern,data,flags=re.DOTALL)
				for url2,qual in sources:
					url3 = ('%s|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36&Origin=https://eb2.srtaem.bar' %url2)
					if '360' in qual:
						title = ('HDFUN | SD | DIRECT | %s' % filmname)
						sort = '4'
					elif '480' in qual:
						title = ('HDFUN | SD | DIRECT | %s' % filmname)
						sort = '4'
					elif '720' in qual:
						title = ('HDFUN | HD | DIRECT | %s' % filmname)
						sort = '3'
					elif '1080' in qual:
						title = ('HDFUN | FHD | DIRECT | %s' % filmname)
						sort = '2'
					else:
						title = ('HDFUN | Unkown | DIRECT | %s' % filmname)
						sort = '4'
					self.links.append({'title': title, 'url': url3, 'quality': sort, 'Debrid' : False, 'Direct' : True})
				if len(self.links) <= 1: xbmc.log("No Results From ::: HDFUN" , level=Notice) 
				else: return self.links
			except Exception as c:
				xbmc.log("SCRAPER ERROR HDFUN  ::: %s" %c , level=Notice)
		else: xbmc.log("SCRAPER HDFUN MOVIE ONLY  ::: %s" %term.title() , level=Notice)

