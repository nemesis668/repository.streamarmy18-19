import requests
from bs4 import BeautifulSoup
import xbmcgui
import xbmc
import re
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://xhamster.com'
SiteName = 'XHamster'
DefaultImage = 'https://raw.githubusercontent.com/nemesis668/repository.streamarmy18-19/917d31e44e35d06957f37e1e65bf89b2c549d36d/plugin.video.cwm/icon.png'
class Scraper:
    def __init__(self):
        self.Base = 'https://xhamster.com/best/weekly/1'
        self.CatUrl = 'https://xhamster.com/categories/'
        self.Search = ('https://xhamster.com/search/%s')
        self.content = []
        self.links = []
        self.cats = []
    def SearchSite(self,term):
        try:
            self.content.append({'name' : '[COLOR magenta]Content From %s[/COLOR]' % SiteName ,'url': '', 'image' : DefaultImage})
            term = term.replace(' ','+')
            link = requests.get(self.Search % term,headers=headers).text
            soup = BeautifulSoup(link, 'html.parser')
            data = soup.find_all('div', class_={'thumb-list__item video-thumb'})
            for i in data:
                title = i.img['alt']
                icon = i.img['src']
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
        data = soup.find_all('div', class_={'thumb-list__item video-thumb'})
        for i in data:
            title = i.img['alt']
            icon = i.img['src']
            media = i.a['href']
            if not Base_Domain in media: media = Base_Domain+media
            self.content.append({'name' : title, 'url': media, 'image' : icon})
        return self.content
    def ResolveLink(self,url):
        link = requests.get(url,headers=headers).text
        pattern = r'''['"]([^'"]\d+p)['"]:['"]([^'"]+mp4)['"]'''
        videos = re.findall(pattern,link)
        if not videos:
            pattern = r'''['"]([^'"]\d+p)['"]:['"]([^'"]+mp4.*?)['"]'''
            videos = re.findall(pattern,link)
        for qual,stream in videos:
            stream = stream.replace('\\','')
            self.links.append({'name' : qual, 'url': stream+'|Referer=%s' % url})
        return self.links
    def GetCats(self):
        c = requests.get(self.CatUrl, headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        content = soup.find_all('a', class_={'item-6b822 thumbItem-6b822'})
        for i in content:
            try:
                title = i.img['alt']
                url = i['href']
                if not Base_Domain in url: url = Base_Domain+url
                self.cats.append({'name' : title, 'url': url+'/1'})
            except: pass
        return self.cats
    def GetNextPage(self,url):
        if url == '':
            url = 'https://xhamster.com/best/weekly/2'
            return url
        else:
            if not '/categories/' in url:
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('https://xhamster.com/best/weekly/%s' % NewNextPageUrl)
                return NextPageUrl
            else:
                NextPageUrl = url.split('/')[-1]
                oldurl = url.rsplit('/', 1)[0]
                NewNextPageUrl = int(NextPageUrl) + 1
                NextPageUrl = ('%s/%s' % (oldurl,NewNextPageUrl))
                return NextPageUrl
                