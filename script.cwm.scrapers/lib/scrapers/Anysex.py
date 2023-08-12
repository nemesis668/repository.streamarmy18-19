import requests
from bs4 import BeautifulSoup
import xbmcgui
import re
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://anysex.com'
class Scraper:
    def __init__(self):
        self.Base = 'https://anysex.com/'
        self.CatUrl = 'https://anysex.com/categories/'
        self.Search = ('?query=')
        self.content = []
        self.links = []
        self.cats = []
    def MainContent(self,url):
        if url == '': url = self.Base
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('li', class_={'item'})
        for i in data:
            name = i.img['alt']
            media = i.a['href']
            if not Base_Domain in media: media=Base_Domain+media
            icon = i.img['src']
            if not Base_Domain in media: media = Base_Domain+media
            self.content.append({'name' : name, 'url': media, 'image' : icon})
        return self.content
    def ResolveLink(self,url):
        c = requests.get(url,headers=headers).text
        pattern = r'''<source\s+id=['"]video_source.+?src=['"]([^'"]+)['"].+?title=['"](.*?)['"]'''
        r = re.findall(pattern,c,flags=re.DOTALL)
        for url,quality in sorted(r, reverse=True):
            self.links.append({'name' : quality, 'url': url})
        return self.links
    def GetCats(self):
        c = requests.get(self.CatUrl, headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        data = soup.find_all('li', class_={'item'})
        for i in data:
            try:
                name = i.a['title']
                url = i.a['href']
                if not Base_Domain in url: url = Base_Domain+url
                self.cats.append({'name' : name, 'url': url+'1/'})
            except: pass
        return self.cats
    def GetNextPage(self,url):
        if url == '':
            url = 'https://anysex.com/new-movies/2/'
            return url
        else:
            if not '/categories/' in url:
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('https://anysex.com/new-movies/%s/' %NewNextPageUrl)
                return NextPageUrl
            else:
                oldurl = url.rsplit('/', 2)[0]
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('%s/%s/' % (oldurl,NewNextPageUrl))
                return NextPageUrl
                