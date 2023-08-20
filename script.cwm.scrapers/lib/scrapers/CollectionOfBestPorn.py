import requests
from bs4 import BeautifulSoup
import xbmcgui
import re
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://collectionofbestporn.com'
SiteName = 'Collection Of Best Porn'
DefaultImage = 'https://raw.githubusercontent.com/nemesis668/repository.streamarmy18-19/917d31e44e35d06957f37e1e65bf89b2c549d36d/plugin.video.cwm/icon.png'
class Scraper:
    def __init__(self):
        self.Base = 'https://collectionofbestporn.com'
        self.CatUrl = 'https://collectionofbestporn.com/channels/'
        self.Search = ('https://collectionofbestporn.com/search/%s')
        self.content = []
        self.links = []
        self.cats = []
    def SearchSite(self,term):
        self.content.append({'name' : '[COLOR magenta]Content From %s[/COLOR]' % SiteName ,'url': '', 'image' : DefaultImage})
        term = term.replace(' ','-')
        link = requests.get(self.Search % term,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('div', class_={'video-thumb'})
        for i in data:
            try:
                name = i.img['title']
                media = i.a['href']
                icon = i.img['src']
                icon = icon+'|verifypeer=false'
                self.content.append({'name' : name, 'url': media, 'image' : icon})
            except: pass
        if len(self.content) > 3: return self.content
        else: pass
    def MainContent(self,url):
        if url == '': url = self.Base
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('div', class_={'video-thumb'})
        for i in data:
            try:
                name = i.img['title']
                media = i.a['href']
                icon = i.img['src']
                icon = icon+'|verifypeer=false'
                self.content.append({'name' : name, 'url': media, 'image' : icon})
            except: pass
        return self.content
    def ResolveLink(self,url):
        c = requests.get(url,headers=headers).text
        soup = BeautifulSoup(c,'html.parser')
        r = soup.find_all('source')
        for i in r:
            quality = i['res']
            url = i['src']
            url = url+'|verifypeer=false'
            self.links.append({'name' : quality, 'url': url})
        return self.links
    def GetCats(self):
        c = requests.get(self.CatUrl, headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        data = soup.find_all('div', class_={'video-desc'})
        for i in data:
            try:
                name = i.a.text
                url = i.a['href']
                self.cats.append({'name' : name, 'url': url+'/page/1'})
            except: pass
        return self.cats
    def GetNextPage(self,url):
        if url == '':
            url = 'https://collectionofbestporn.com/most-recent/page/2'
            return url
        else:
            if not '/category/' in url:
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('https://collectionofbestporn.com/most-recent/page/%s' %NewNextPageUrl)
                return NextPageUrl
            else:
                oldurl = url.rsplit('/', 1)[0]
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('%s/%s' % (oldurl,NewNextPageUrl))
                return NextPageUrl
                