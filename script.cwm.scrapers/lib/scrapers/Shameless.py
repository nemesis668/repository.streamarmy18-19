import requests
from bs4 import BeautifulSoup
import xbmcgui
import re
import xbmc
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://www.shameless.com/'
SiteName = 'Shameless'
DefaultImage = 'https://raw.githubusercontent.com/nemesis668/repository.streamarmy18-19/917d31e44e35d06957f37e1e65bf89b2c549d36d/plugin.video.cwm/icon.png'
class Scraper:
    def __init__(self):
        self.Base = 'https://www.shameless.com/'
        self.CatUrl = 'https://www.shameless.com/categories/'
        self.Search = ('https://www.shameless.com/search/?q=%s')
        self.content = []
        self.links = []
        self.cats = []
    def SearchSite(self,term):
        try:
            self.content.append({'name' : '[COLOR magenta]Content From %s[/COLOR]' % SiteName ,'url': '', 'image' : DefaultImage})
            term = term.replace(' ','+')
            link = requests.get(self.Search % term,headers=headers).text
            soup = BeautifulSoup(link, 'html.parser')
            data = soup.find_all('div', class_={'icnt'})
            for i in data:
                name = i.img['alt']
                media = i.a['href']
                if not Base_Domain in media: media=Base_Domain+media
                icon = i.img['data-src']
                icon = icon+'|Referer=https://www.shameless.com/'
                if not Base_Domain in media: media = Base_Domain+media
                self.content.append({'name' : name, 'url': media, 'image' : icon})
            if len(self.content) > 3: return self.content
            else: pass
        except Exception as e: xbmc.log('SCRAPER ERROR : %s ::: %s'% (SiteName,e),xbmc.LOGINFO)
    def MainContent(self,url):
        dialog.ok("URL",str(url))
        if url == '': url = self.Base
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('div', class_={'icnt'})
        for i in data:
            name = i.img['alt']
            media = i.a['href']
            if not Base_Domain in media: media=Base_Domain+media
            icon = i.img['data-src']
            icon = icon+'|Referer=https://www.shameless.com/'
            if not Base_Domain in media: media = Base_Domain+media
            self.content.append({'name' : name, 'url': media, 'image' : icon})
        return self.content
    def ResolveLink(self,url):
        c = requests.get(url,headers=headers).text
        pattern = r'''url:.*?(http[^'"]+mp4.*?)['"].*?_text:.*?['"](.*?)['"]'''
        r = re.findall(pattern,c,flags=re.DOTALL)
        for source,quality in r:
            headers.update({'Referer': url})
            source2 = requests.get(source,headers=headers,stream=True)
            newsource = source2.url
            playurl = ('%s|Referer=https://www.shameless.com/' % newsource)
            self.links.append({'name' : quality, 'url': playurl})
        return self.links
    def GetCats(self):
        c = requests.get(self.CatUrl, headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        data = soup.find_all('div', class_={'item'})
        for i in data:
            try:
                name = i.img['alt']
                url = i.a['href']
                if not Base_Domain in url: url = Base_Domain+url
                self.cats.append({'name' : name, 'url': url+'1/'})
            except: pass
        return self.cats
    def GetNextPage(self,url):
        if url == '':
            url = 'https://www.shameless.com/videos/2/'
            return url
        else:
            if not '/categories/' in url:
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('https://www.shameless.com/videos/%s/' %NewNextPageUrl)
                return NextPageUrl
            else:
                oldurl = url.rsplit('/', 2)[0]
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('%s/%s/' % (oldurl,NewNextPageUrl))
                return NextPageUrl
                