import requests
from bs4 import BeautifulSoup
import xbmcgui
import re
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://www.thumbzilla.com'
class Scraper:
    def __init__(self):
        self.Base = 'https://www.thumbzilla.com/'
        self.CatUrl = 'https://www.thumbzilla.com/'
        self.Search = ('?query=')
        self.content = []
        self.links = []
        self.cats = []
        
    def MainContent(self,url):
        if url == '': url = self.Base
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('a', class_={'js-thumb'})
        for i in data:
            try:
                name = i.find('span', class_={'title'}).text.replace('/n','')
                url = i['href']
                if not Base_Domain in url: url=Base_Domain+url
                icon = i.img['data-original']
                self.content.append({'name' : name, 'url': url, 'image' : icon})
            except: pass
        return self.content
        
    def ResolveLink(self,url):
        pattern = r'''videoUrl['"]:['"]([^'"]+m3u8.+?)['"].+?:['"](.*?)['"]'''
        link = requests.get(url,headers=headers).text
        videos = re.findall(pattern,link)
        for stream,qual in videos:
            stream = stream.replace('\\','')
            self.links.append({'name' : qual, 'url': stream+'|Referer=%s' % url})
        return self.links
        
    def GetCats(self):
        c = requests.get(self.CatUrl,headers=headers).text
        soup = BeautifulSoup(c,'html.parser')
        r = soup.find_all('div', class_={'checkHomepage'})
        for i in r:
            try:
                title = i.find('span', class_={'wrapper'}).text.strip()
                url = i.a['href']
                if not Base_Domain in url: url = Base_Domain+url
                self.cats.append({'name' : title, 'url': url+'?page=1'})
            except: pass
        return self.cats
        
    def GetNextPage(self,url):
        if url == '':
            url = 'https://www.thumbzilla.com/?page=2'
            return url
        else:
            if not '/categories/' in url:
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('https://www.thumbzilla.com/?page=%s' % NewNextPageUrl)
                return NextPageUrl
            else:
                NextPageUrl = url.split('page=')[-1]
                oldurl = url.rsplit('page=', 1)[0]
                NewNextPageUrl = int(NextPageUrl) + 1
                NextPageUrl = ('%spage=%s' % (oldurl,NewNextPageUrl))
                return NextPageUrl