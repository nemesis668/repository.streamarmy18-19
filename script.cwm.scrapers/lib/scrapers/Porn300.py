import requests
from bs4 import BeautifulSoup
import xbmcgui
import xbmc
import re
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://www.porn300.com/'
SiteName = 'Porn300'
DefaultImage = 'https://raw.githubusercontent.com/nemesis668/repository.streamarmy18-19/917d31e44e35d06957f37e1e65bf89b2c549d36d/plugin.video.cwm/icon.png'
class Scraper:
    def __init__(self):
        self.Base = 'https://www.porn300.com/?page=1'
        self.CatUrl = 'https://www.porn300.com/categories/'
        self.Search = ('https://www.porn300.com/search/?q=%s')
        self.content = []
        self.links = []
        self.cats = []
    def SearchSite(self,term):
        try:
            self.content.append({'name' : '[COLOR magenta]Content From %s[/COLOR]' % SiteName ,'url': '', 'image' : DefaultImage})
            term = term.replace(' ','+')
            link = requests.get(self.Search % term,headers=headers).text
            soup = BeautifulSoup(link, 'html.parser')
            data = soup.find_all('li', class_={'grid__item grid__item--16-9 grid__item--video-thumb'})
            for i in data:
                title = i.img['alt']
                icon = i.img['data-src']
                media = i.a['href']
                if not Base_Domain in media: media = Base_Domain+media
                self.content.append({'name' : title, 'url': media, 'image' : icon})
            if len(self.content) > 3: return self.content
            else: pass
        except Exception as e: xbmc.log('SCRAPER ERROR : %s ::: %s'% (SiteName,e),xbmc.LOGINFO)
    def MainContent(self,url):
        if url == '': url = self.Base
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('li', class_={'grid__item grid__item--16-9 grid__item--video-thumb'})
        for i in data:
            title = i.img['alt']
            icon = i.img['data-src']
            media = i.a['href']
            if not Base_Domain in media: media = Base_Domain+media
            self.content.append({'name' : title, 'url': media, 'image' : icon})
        return self.content
    def ResolveLink(self,url):
        link = requests.get(url, headers=headers).text
        soup = BeautifulSoup(link,'html.parser')
        data = soup.find('video', id={'video-js'})
        source = data.source['src']
        self.links.append({'name' : 'Play Content', 'url': source})
        return self.links
    def GetCats(self):
        c = requests.get(self.CatUrl, headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        content = soup.find_all('li', class_={'grid__item grid__item--category'})
        for i in content:
            try:
                title = i.a['data-category-gtmname']
                url = i.a['href']
                if not Base_Domain in url: url = Base_Domain+url
                self.cats.append({'name' : title, 'url': url+'?page=1'})
            except: pass
        return self.cats
    def GetNextPage(self,url):
        if url == '':
            url = 'https://www.porn300.com/?page=2'
            return url
        else:
            if not '/categories/' in url:
                NextPageUrl = url.split('page=')[-1]
                oldurl = url.rsplit('page=', 1)[0]
                NewNextPageUrl = int(NextPageUrl) + 1
                NextPageUrl = ('%spage=%s' % (oldurl,NewNextPageUrl))
                return NextPageUrl
            else:
                oldurl = url.rsplit('page=', 1)[0]
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('%spage=%s' % (oldurl,NewNextPageUrl))
                return NextPageUrl
                