import requests
from bs4 import BeautifulSoup
import xbmcgui
import re
import xbmc
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://hqporner.com'
SiteName = 'HQPorner'
DefaultImage = 'https://raw.githubusercontent.com/nemesis668/repository.streamarmy18-19/917d31e44e35d06957f37e1e65bf89b2c549d36d/plugin.video.cwm/icon.png'
class Scraper:
    def __init__(self):
        self.Base = 'https://hqporner.com/hdporn/1'
        self.CatUrl = 'https://hqporner.com/categories'
        self.Search = ('https://hqporner.com/?q=%s')
        self.content = []
        self.links = []
        self.cats = []
    def SearchSite(self,term):
        try:
            self.content.append({'name' : '[COLOR magenta]Content From %s[/COLOR]' % SiteName ,'url': '', 'image' : DefaultImage})
            term = term.replace(' ','+')
            link = requests.get(self.Search % term,headers=headers).text
            soup = BeautifulSoup(link, 'html.parser')
            data = soup.find_all('section', class_={'box feature'})
            for i in data:
                try:
                    name = i.img['alt'].title()
                    url2 = i.a['href']
                    icon = i.img['src']
                    icon =icon+'|verifypeer=false'
                    if not 'https:' in url2: url2 = 'https://hqporner.com' + url2
                    if not 'https:' in icon: icon = 'https:' + icon
                    self.content.append({'name' : name, 'url': url2, 'image' : icon})
                except: pass
            if len(self.content) > 3: return self.content
            else: pass
        except Exception as e: xbmc.log('SCRAPER ERROR : %s ::: %s'% (SiteName,e),xbmc.LOGINFO)
    def MainContent(self,url):
        if url == '': url = self.Base
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('section', class_={'box feature'})
        for i in data:
            try:
                name = i.img['alt'].title()
                url2 = i.a['href']
                icon = i.img['src']
                icon =icon+'|verifypeer=false'
                if not 'https:' in url2: url2 = 'https://hqporner.com' + url2
                if not 'https:' in icon: icon = 'https:' + icon
                self.content.append({'name' : name, 'url': url2, 'image' : icon})
            except: pass
        return self.content
        
    def ResolveLink(self,url):
        c = requests.get(url, headers=headers).text
        pattern = r"""iframe\s*width=['"]\d+['"]\s*height=['"]\d+['"]\s*src=['"]([^'"]+)"""
        url = re.findall(pattern,c)[0]
        url = url if url.startswith('http') else 'https:' + url
        r = requests.get(url,headers=headers).text
        pattern = r"""a\s+href=['"]([^'"]+mp4)['"].*?>(.*?)<"""
        urls = re.findall(pattern,r)
        for links,qual in urls:
            if not 'http' in links: links='http:'+links
            self.links.append({'name' : qual, 'url': links})
        return self.links
        
    def GetCats(self):
        c = requests.get(self.CatUrl,headers=headers).text
        soup = BeautifulSoup(c,'html.parser')
        r = soup.find_all('section', class_={'box feature'})
        for i in r:
            try:
                title = i.img['alt'].title()
                url = i.a['href']
                if not Base_Domain in url: url = Base_Domain+url
                self.cats.append({'name' : title, 'url': url+'/1'})
            except: pass
        return self.cats
        
    def GetNextPage(self,url):
        if url == '':
            url = 'https://hqporner.com/hdporn/2'
            return url
        else:
            if not '/category/' in url:
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('https://hqporner.com/hdporn/%s' % NewNextPageUrl)
                return NextPageUrl
            else:
                NextPageUrl = url.split('/')[-1]
                oldurl = url.rsplit('/', 1)[0]
                NewNextPageUrl = int(NextPageUrl) + 1
                NextPageUrl = ('%s/%s' % (oldurl,NewNextPageUrl))
                return NextPageUrl