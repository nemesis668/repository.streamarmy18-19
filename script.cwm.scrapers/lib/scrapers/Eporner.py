import requests
from bs4 import BeautifulSoup
import xbmcgui
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://www.eporner.com'
class Scraper:
    def __init__(self):
        self.Base = 'https://www.eporner.com/most-viewed/'
        self.CatUrl = 'https://www.eporner.com/cats/'
        self.Search = ('https://www.eporner.com/search/%s/')
        self.content = []
        self.links = []
        self.cats = []
    def SearchSite(self,term):
        term = term.replace(' ','-')
        link = requests.get(self.Search % term,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('div', class_={'mb hdy'})
        for i in data:
            title = i.img['alt']
            try: icon = i.img['data-src']
            except: icon = i.img['src']
            media = i.a['href']
            if not Base_Domain in media: media = Base_Domain+media
            self.content.append({'name' : title, 'url': media, 'image' : icon})
        return self.content
    def MainContent(self,url):
        if url == '': url = self.Base
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('div', class_={'mb hdy'})
        for i in data:
            title = i.img['alt']
            try: icon = i.img['data-src']
            except: icon = i.img['src']
            media = i.a['href']
            if not Base_Domain in media: media = Base_Domain+media
            self.content.append({'name' : title, 'url': media, 'image' : icon})
        return self.content
    def ResolveLink(self,url):
        c = requests.get(url,headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        r = soup.find('div', class_={'dloaddivcol'})
        for links in r.find_all('a'):
            link = links['href']
            title = links.text
            title = title.replace('Download','')
            url = ('https://www.eporner.com%s' %link)
            self.links.append({'name' : title, 'url': url})
        return self.links
    def GetCats(self):
        c = requests.get(self.CatUrl, headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        content = soup.find_all('div', class_={'ctbinner'})
        for i in content:
            try:
                title = i.a['title']
                url = i.a['href']
                if not Base_Domain in url: url = Base_Domain+url
                self.cats.append({'name' : title, 'url': url+'1'})
            except: pass
        return self.cats
    def GetNextPage(self,url):
        if url == '':
            url = 'https://www.eporner.com/2/most-viewed/'
            return url
        else:
            if not '/cat/' in url:
                NextPageUrl = url.split('/')[3]
                NewNextPageUrl = int(NextPageUrl) + 1
                NextPageUrl = ('https://www.eporner.com/%s/most-viewed/' %NewNextPageUrl)
                return NextPageUrl
            else:
                NextPageUrl = url.split('/')[-1]
                oldurl = url.rsplit('/', 1)[0]
                NewNextPageUrl = int(NextPageUrl) + 1
                NextPageUrl = ('%s/%s' % (oldurl,NewNextPageUrl))
                return NextPageUrl
                