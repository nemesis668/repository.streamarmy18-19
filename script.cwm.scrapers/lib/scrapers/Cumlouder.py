import requests
from bs4 import BeautifulSoup
import xbmcgui
import re
import xbmc
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://www.cumlouder.com'
SiteName = 'CumLouder'
DefaultImage = 'https://raw.githubusercontent.com/nemesis668/repository.streamarmy18-19/917d31e44e35d06957f37e1e65bf89b2c549d36d/plugin.video.cwm/icon.png'
class Scraper:
    def __init__(self):
        self.Base = 'https://www.cumlouder.com/series/newest/1/'
        self.CatUrl = 'https://www.cumlouder.com/categories/'
        self.Search = ('https://www.cumlouder.com/search/?q=%s')
        self.content = []
        self.links = []
        self.cats = []
    def SearchSite(self,term):
        try:
            self.content.append({'name' : '[COLOR magenta]Content From %s[/COLOR]' % SiteName ,'url': '', 'image' : DefaultImage})
            term = term.replace(' ','%20')
            link = requests.get(self.Search % term,headers=headers).text
            soup = BeautifulSoup(link, 'html.parser')
            data = soup.find_all('a', class_={'muestra-escena'})
            for i in data:
                name = i.img['alt']
                media = i['href']
                if not Base_Domain in media: media=Base_Domain+media
                icon = i.img['data-src']
                if not 'http' in icon: icon='https:'+icon
                if not Base_Domain in media: media = Base_Domain+media
                self.content.append({'name' : name, 'url': media, 'image' : icon})
            if len(self.content) > 3: return self.content
            else: pass
        except Exception as e: xbmc.log('SCRAPER ERROR : %s ::: %s'% (SiteName,e),xbmc.LOGINFO)
    def MainContent(self,url):
        if url == '': url = self.Base
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('a', class_={'muestra-escena'})
        for i in data:
            name = i.img['alt']
            media = i['href']
            if not Base_Domain in media: media=Base_Domain+media
            icon = i.img['data-src']
            if not 'http' in icon: icon='https:'+icon
            if not Base_Domain in media: media = Base_Domain+media
            if '/porn-video/' in media: self.content.append({'name' : name, 'url': media, 'image' : icon})
        return self.content
    def ResolveLink(self,url):
        c = requests.get(url,headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        r = soup.find_all('video', id={'cum_player'})
        for links in r:
            url = links.source['src']
            title = links.source['label']
            self.links.append({'name' : title, 'url': url})
        return self.links
    def GetCats(self):
        c = requests.get(self.CatUrl, headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        data = soup.find_all('a', class_={'muestra-escena muestra-categoria show-tag'})
        for i in data:
            try:
                name = i.img['alt']
                url = i['href']
                url = url.replace('?show=cumlouder','')
                if not Base_Domain in url: url = Base_Domain+url
                self.cats.append({'name' : name, 'url': url+'1/'})
            except: pass
        return self.cats
    def GetNextPage(self,url):
        dialog.ok("URL",str(url))
        if url == '':
            url = 'https://www.cumlouder.com/series/newest/2/'
            return url
        else:
            if '/series/' in url:
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('https://www.cumlouder.com/series/newest/%s/' %NewNextPageUrl)
                return NextPageUrl
            else:
                oldurl = url.rsplit('/', 2)[0]
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('%s/%s/' % (oldurl,NewNextPageUrl))
                return NextPageUrl
                