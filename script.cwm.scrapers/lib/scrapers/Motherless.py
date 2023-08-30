import requests
from bs4 import BeautifulSoup
import xbmcgui
import xbmc
import re
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://www.motherless.com'
SiteName = 'Motherless'
DefaultImage = 'https://raw.githubusercontent.com/nemesis668/repository.streamarmy18-19/917d31e44e35d06957f37e1e65bf89b2c549d36d/plugin.video.cwm/icon.png'
class Scraper:
    def __init__(self):
        self.Base = 'https://motherless.com/videos/recent?page=1'
        self.CatUrl = 'https://www.motherless.com'
        self.Search = ('https://motherless.com/term/videos/%s?term=%s&type=all&range=0&size=0&sort=relevance')
        self.content = []
        self.links = []
        self.cats = []
    def SearchSite(self,term):
        try:
            self.content.append({'name' : '[COLOR magenta]Content From %s[/COLOR]' % SiteName ,'url': '', 'image' : DefaultImage})
            term = term.replace(' ','+')
            link = requests.get(self.Search % (term,term),headers=headers).text
            soup = BeautifulSoup(link, 'html.parser')
            data = soup.find_all('div', class_={'thumb-container video'})
            for i in data:
                title = i.find('img', class_={'static'})['alt'].title()
                time = i.find('span', class_={'size'}).text
                media = i.a['href']
                icon = i.find('img', class_={'static'})['src']
                icon = icon+'|verifypeer=false'
                #if not Base_Domain in media: media = Base_Domain+media
                self.content.append({'name' : '%s | Length :[COLOR yellow] %s[/COLOR]' % (title,time), 'url': media, 'image' : icon})
            if len(self.content) > 3: return self.content
            else: pass
        except Exception as e: xbmc.log('SCRAPER ERROR : %s ::: %s'% (SiteName,e),xbmc.LOGINFO)
    def MainContent(self,url):
        if url == '': url = self.Base
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('div', class_={'thumb-container video'})
        for i in data:
            title = i.find('img', class_={'static'})['alt'].title()
            time = i.find('span', class_={'size'}).text
            media = i.a['href']
            icon = i.find('img', class_={'static'})['src']
            icon = icon+'|verifypeer=false'
            #if not Base_Domain in media: media = Base_Domain+media
            self.content.append({'name' : '%s | Length :[COLOR yellow] %s[/COLOR]' % (title,time), 'url': media, 'image' : icon})
        return self.content
    def ResolveLink(self,url):
        link = requests.get(url, headers=headers).text
        pattern = r'''__fileurl = ['"]([^'"]+)['"]'''
        source = re.findall(pattern,link,flags=re.DOTALL)[0]
        source = source+'|verifypeer=false'
        self.links.append({'name' : 'Play Content', 'url': source})
        return self.links
    def GetCats(self):
        c = requests.get(self.CatUrl, headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        content = soup.find('div', class_={'menu-categories-tabs-container'})
        for i in content.find_all('a'):
            try:
                title = i.text.strip()
                url = i['href']
                if not Base_Domain in url: url = Base_Domain+url
                self.cats.append({'name' : title, 'url': url+'?page=1'})
            except: pass
        return self.cats
    def GetNextPage(self,url):
        if url == '':
            url = 'https://motherless.com/videos/recent?page=2'
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
                