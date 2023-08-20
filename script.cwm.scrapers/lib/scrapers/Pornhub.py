import requests
from bs4 import BeautifulSoup
import xbmcgui
import re
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://www.pornhub.com'
cookies = {'Cookie': 'accessAgeDisclaimerPH=1; accessAgeDisclaimerUK=1'}
SiteName = 'PornHub'
DefaultImage = 'https://raw.githubusercontent.com/nemesis668/repository.streamarmy18-19/917d31e44e35d06957f37e1e65bf89b2c549d36d/plugin.video.cwm/icon.png'
class Scraper:
    def __init__(self):
        self.Base = 'https://www.pornhub.com'
        self.CatUrl = 'https://www.pornhub.com/categories'
        self.Search = ('https://www.pornhub.com/video/search?search=%s')
        self.content = []
        self.links = []
        self.cats = []
    def SearchSite(self,term):
        self.content.append({'name' : '[COLOR magenta]Content From %s[/COLOR]' % SiteName ,'url': '', 'image' : DefaultImage})
        term = term.replace(' ','+')
        link = requests.get(self.Search % term,headers=headers, cookies=cookies).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('div', class_={'phimage'})
        for i in data:
            try:
                name = i.a['title']
                icon = i.img['src']
                url = i.a['href']
                if not Base_Domain in url: url=Base_Domain+url
                self.content.append({'name' : name, 'url': url, 'image' : icon})
            except: pass
        if len(self.content) > 3: return self.content
        else: pass
    def MainContent(self,url):
        if url == '': url = self.Base
        if 'video?c=' in url:
            link = requests.get(url,headers=headers, cookies=cookies).text
            soup = BeautifulSoup(link, 'html.parser')
            content = soup.find('ul', id={'videoCategory'})
            for i in content.find_all('div', class_={'phimage'}):
                try:
                    name = i.a['title']
                    icon = i.img['src']
                    url = i.a['href']
                    if not Base_Domain in url: url=Base_Domain+url
                    self.content.append({'name' : name, 'url': url, 'image' : icon})
                except: pass
            return self.content
        else:
            link = requests.get(url,headers=headers, cookies=cookies).text
            soup = BeautifulSoup(link, 'html.parser')
            data = soup.find_all('div', class_={'phimage'})
            for i in data:
                try:
                    name = i.a['title']
                    icon = i.img['src']
                    url = i.a['href']
                    if not Base_Domain in url: url=Base_Domain+url
                    self.content.append({'name' : name, 'url': url, 'image' : icon})
                except: pass
            return self.content
        
    def ResolveLink(self,url):
        # Credit to gujal for this resolver code!!
        link = requests.get(url,headers=headers, cookies=cookies).text
        sections = re.findall(r'(var\sra[a-z0-9]+=.+?);flash', link)
        for section in sections:
            pvars = re.findall(r'var\s(ra[a-z0-9]+)=([^;]+)', section)
            link = re.findall(r'var\smedia_\d+=([^;]+)', section)[0]
            link = re.sub(r"/\*.+?\*/", '', link)
            for key, value in pvars:
                link = re.sub(key, value, link)
            link = link.replace('"', '').split('+')
            link = [i.strip() for i in link]
            link = ''.join(link)
            if 'urlset' not in link:
                r = re.findall(r'(\d+p)', link, re.I)
                if r: self.links.append({'name' : r[0], 'url': link })
        return self.links
        
    def GetCats(self):
        c = requests.get(self.CatUrl,headers=headers, cookies=cookies).text
        soup = BeautifulSoup(c,'html.parser')
        r = soup.find_all('div', class_={'category-wrapper'})
        for i in r:
            try:
                title = i.a['data-mxptext']
                url = i.a['href']
                if not Base_Domain in url: url = Base_Domain+url
                self.cats.append({'name' : title, 'url': url+'&page=1'})
            except: pass
        return self.cats
    def GetNextPage(self,url):
        if url == '':
            url = 'https://www.pornhub.com/video?page=2'
            return url
        else:
            if not 'video?c=' in url:
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('https://www.pornhub.com/video?page=%s' % NewNextPageUrl)
                return NextPageUrl
            else:
                NextPageUrl = url.split('page=')[-1]
                oldurl = url.rsplit('page=', 1)[0]
                NewNextPageUrl = int(NextPageUrl) + 1
                NextPageUrl = ('%spage=%s' % (oldurl,NewNextPageUrl))
                return NextPageUrl