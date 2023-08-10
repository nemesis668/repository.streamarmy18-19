import requests
from bs4 import BeautifulSoup
import xbmcgui
import re
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://fapality.com/'
class Scraper:
    def __init__(self):
        self.Base = 'https://fapality.com/popular/1'
        self.CatUrl = 'https://fapality.com/categories/'
        self.Search = ('?query=')
        self.content = []
        self.links = []
        self.cats = []
    def MainContent(self,url):
        if url == '': url = self.Base
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('li', class_={'masonry-item'})
        for i in data:
            try:
                title = i.a['title']
                media = i.a['href']
                icon = i.img['src']
                if not Base_Domain in media: media = Base_Domain+media
                self.content.append({'name' : title, 'url': media, 'image' : icon})
            except: pass
        return self.content
    def ResolveLink(self,url):
        c = requests.get(url, headers=headers).text
        soup = BeautifulSoup(c,'html.parser')
        r = soup.find_all('source', id=re.compile("video_source_[0-9]"))
        names = []
        srcs  = []
        for i in r:
            title = i['title']
            url = i['src']
            self.links.append({'name' : title, 'url': url})
        return self.links
    def GetCats(self):
        c = requests.get(self.CatUrl,headers=headers).text
        soup = BeautifulSoup(c,'html.parser')
        r = soup.find_all('div', class_={'item'})
        for i in r:
            try:
                title = i.a['title']
                url = i.a['href']
                if not Base_Domain in url: url = Base_Domain+url
                self.cats.append({'name' : title, 'url': url+'1/'})
            except: pass
        return self.cats
    def GetNextPage(self,url):
        if url == '':
            url = 'https://fapality.com/popular/2/'
            return url
        else:
            if not '/categories/' in url:
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('https://fapality.com/popular/%s/' % NewNextPageUrl)
                return NextPageUrl
            else:
                oldurl = url.rsplit('/', 2)[0]
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('%s/%s/' % (oldurl,NewNextPageUrl))
                return NextPageUrl