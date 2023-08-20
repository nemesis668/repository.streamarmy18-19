import requests
from bs4 import BeautifulSoup
import xbmcgui
import re
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://www.perfectgirls.xxx'
SiteName = 'Perfect Girls'
DefaultImage = 'https://raw.githubusercontent.com/nemesis668/repository.streamarmy18-19/917d31e44e35d06957f37e1e65bf89b2c549d36d/plugin.video.cwm/icon.png'
class Scraper:
    def __init__(self):
        self.Base = 'https://www.perfectgirls.xxx/1/'
        self.CatUrl = 'https://www.perfectgirls.xxx/tags/'
        self.Search = ('https://www.perfectgirls.xxx/search/%s/')
        self.content = []
        self.links = []
        self.cats = []
    def SearchSite(self,term):
        self.content.append({'name' : '[COLOR magenta]Content From %s[/COLOR]' % SiteName ,'url': '', 'image' : DefaultImage})
        term = term.replace(' ','-')
        link = requests.get(self.Search % term,headers=headers).text
        soup = BeautifulSoup(link,'html.parser')
        data = soup.find_all('div', class_={'thumb thumb-video'})
        for i in data:
            try:
                title = i.a['title']
                media = i.a['href']
                icon = i.img['data-original']
                #icon = icon+'|verifypeer=false'
                if not 'http' in icon: icon='https:'+icon
                if not Base_Domain in media: media = Base_Domain+media
                self.content.append({'name' : title, 'url': media, 'image' : icon})
            except: pass
        if len(self.content) > 3: return self.content
        else: pass
    def MainContent(self,url):
        if url == '': url = self.Base
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link,'html.parser')
        data = soup.find_all('div', class_={'thumb thumb-video'})
        for i in data:
            try:
                title = i.a['title']
                media = i.a['href']
                icon = i.img['data-original']
                icon = icon+'|verifypeer=false'
                if not 'http' in icon: icon='https:'+icon
                if not Base_Domain in media: media = Base_Domain+media
                self.content.append({'name' : title, 'url': media, 'image' : icon})
            except: pass
        return self.content
    def ResolveLink(self,url):
        link = requests.get(url, headers=headers).text
        soup = BeautifulSoup(link,'html.parser')
        r = soup.find_all('a', class_={'download-link'})
        for i in r:
            url = i['href']
            qual = i.span.text
            self.links.append({'name' : str(qual), 'url': url})
        return self.links
    def GetCats(self):
        c = requests.get(self.CatUrl,headers=headers).text
        soup = BeautifulSoup(c,'html.parser')
        r = soup.find_all('a', class_={'item'})
        for i in r:
            try:
                title = i.text.strip()
                url = i['href']
                if not Base_Domain in url: url = Base_Domain+url
                self.cats.append({'name' : title, 'url': url+'?page=1'})
            except: pass
        return self.cats
    def GetNextPage(self,url):
        if url == '':
            url = 'https://www.perfectgirls.xxx/2/'
            return url
        else:
            if not '/tags/' in url:
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('https://www.perfectgirls.xxx/%s/' % NewNextPageUrl)
                return NextPageUrl
            else:
                oldurl = url.rsplit('/', 2)[0]
                getcurrent = url.rsplit('/', 2)[1]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('%s/%s/' % (oldurl,NewNextPageUrl))
                return NextPageUrl