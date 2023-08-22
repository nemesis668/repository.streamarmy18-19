import requests
from bs4 import BeautifulSoup
import xbmcgui
import xbmc
import re
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://www.tubewolf.com'
SiteName = 'TubeWolf'
DefaultImage = 'https://raw.githubusercontent.com/nemesis668/repository.streamarmy18-19/917d31e44e35d06957f37e1e65bf89b2c549d36d/plugin.video.cwm/icon.png'
class Scraper:
    def __init__(self):
        self.Base = 'https://www.tubewolf.com/1/'
        self.CatUrl = 'https://www.tubewolf.com/categories/'
        self.Search = ('https://www.tubewolf.com/search/?q=%s')
        self.content = []
        self.links = []
        self.cats = []
    def SearchSite(self,term):
        try:
            self.content.append({'name' : '[COLOR magenta]Content From %s[/COLOR]' % SiteName ,'url': '', 'image' : DefaultImage})
            term = term.replace(' ','+')
            link = requests.get(self.Search % term,headers=headers).text
            soup = BeautifulSoup(link, 'html.parser')
            data = soup.find_all('div', class_={'thumb'})
            for i in data:
                title = i.a['title']
                url =i.a['href']
                icon = i.img['src']
                if not Base_Domain in url: url=Base_Domain+url
                self.content.append({'name' : title, 'url': url, 'image' : icon})
            if len(self.content) > 3: return self.content
            else: pass
        except Exception as e: xbmc.log('SCRAPER ERROR : %s ::: %s'% (SiteName,e),xbmc.LOGINFO)
    def MainContent(self,url):
        if url == '': url = self.Base
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('div', class_={'thumb'})
        for i in data:
            title = i.a['title']
            url =i.a['href']
            icon = i.img['src']
            if not Base_Domain in url: url=Base_Domain+url
            self.content.append({'name' : title, 'url': url, 'image' : icon})
        return self.content
    def ResolveLink(self,url):
        c = requests.get(url,headers=headers).text
        pattern = r'''<source\s+src=['"]([^'"]+)['"].+?title=['"](.*?)['"]'''
        r = re.findall(pattern,c,flags=re.DOTALL)
        for url,quality in sorted(r, reverse=True):
            if quality == '': quality = 'SD'
            self.links.append({'name' : quality, 'url': url})
        return self.links
    def GetCats(self):
        c = requests.get(self.CatUrl, headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        data = soup.find_all('div', class_={'thumb'})
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
            url = 'https://www.tubewolf.com/2/'
            return url
        else:
            if not '/categories/' in url:
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('https://www.tubewolf.com/%s/' %NewNextPageUrl)
                return NextPageUrl
            else:
                oldurl = url.rsplit('/', 2)[0]
                getcurrent = url.rsplit('/', 2)[1]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('%s/%s/' % (oldurl,NewNextPageUrl))
                return NextPageUrl
                