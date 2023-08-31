import requests
from bs4 import BeautifulSoup
import xbmcgui
import re
import xbmc
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://www.cliphunter.com'
SiteName = 'Cliphunter'
DefaultImage = 'https://raw.githubusercontent.com/nemesis668/repository.streamarmy18-19/917d31e44e35d06957f37e1e65bf89b2c549d36d/plugin.video.cwm/icon.png'
class Scraper:
    def __init__(self):
        self.Base = 'https://www.cliphunter.com/popular/ratings/today/1'
        self.CatUrl = 'https://www.cliphunter.com/categories/'
        self.Search = ('https://www.cliphunter.com/search/%s')
        self.content = []
        self.links = []
        self.cats = []
    def SearchSite(self,term):
        try:
            self.content.append({'name' : '[COLOR magenta]Content From %s[/COLOR]' % SiteName ,'url': '', 'image' : DefaultImage})
            term = term.replace(' ','%20')
            link = requests.get(self.Search % term,headers=headers).text
            soup = BeautifulSoup(link, 'html.parser')
            data = soup.find_all('a', class_={'t pop-execute'})
            for i in data:
                name = i['href'].split('/')[-1].replace('_',' ').strip()
                media = i['href']
                if not Base_Domain in media: media=Base_Domain+media
                icon = i.img['src']
                if not Base_Domain in media: media = Base_Domain+media
                self.content.append({'name' : name, 'url': media, 'image' : icon})
            if len(self.content) > 3: return self.content
            else: pass
        except Exception as e: xbmc.log('SCRAPER ERROR : %s ::: %s'% (SiteName,e),xbmc.LOGINFO)
    def MainContent(self,url):
        if url == '': url = self.Base
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('a', class_={'t pop-execute'})
        for i in data:
            name = i['href'].split('/')[-1].replace('_',' ').strip()
            media = i['href']
            if not Base_Domain in media: media=Base_Domain+media
            icon = i.img['src']
            if not Base_Domain in media: media = Base_Domain+media
            self.content.append({'name' : name, 'url': media, 'image' : icon})
        return self.content
    def ResolveLink(self,url):
        r = requests.get(url,headers=headers).text
        pattern = r"""["']h['"]:(.*?),.*?url['"]:['"]([^'"]+mp4.*?)['"]"""
        urls = re.findall(pattern,r)
        for qual,links in urls:
            links = links.replace('\\','')
            links = ('%s|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82&Referer=https://www.cliphunter.com/' % links)
            self.links.append({'name' : qual, 'url': links})
        return self.links
    def GetCats(self):
        c = requests.get(self.CatUrl, headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        data = soup.find('div', class_={'paper paperSpacings xs-fullscreen photoGrid'})
        for i in data.find_all('a'):
            try:
                name = i['title']
                url = i['href']
                if not Base_Domain in url: url = Base_Domain+url
                self.cats.append({'name' : name, 'url': url+'/1/'})
            except: pass
        return self.cats
    def GetNextPage(self,url):
        if url == '':
            url = 'https://www.cliphunter.com/popular/ratings/today/2'
            return url
        else:
            if not '/categories/' in url:
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('https://www.cliphunter.com/popular/ratings/today/%s' %NewNextPageUrl)
                return NextPageUrl
            else:
                oldurl = url.rsplit('/', 2)[0]
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('%s/%s/' % (oldurl,NewNextPageUrl))
                return NextPageUrl
                