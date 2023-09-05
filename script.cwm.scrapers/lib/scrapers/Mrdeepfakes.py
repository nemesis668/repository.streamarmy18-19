import requests
from bs4 import BeautifulSoup
import xbmcgui
import re
import xbmc
from resources.libs.decoder.kvs import kvs_decode
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
Base_Domain = 'https://mrdeepfakes.com/'
SiteName = 'MrDeepFakes'
DefaultImage = 'https://raw.githubusercontent.com/nemesis668/repository.streamarmy18-19/917d31e44e35d06957f37e1e65bf89b2c549d36d/plugin.video.cwm/icon.png'
class Scraper:
    
    def __init__(self):
        self.Base = 'https://mrdeepfakes.com/'
        self.CatUrl = 'https://mrdeepfakes.com/categories'
        self.Search = ('https://mrdeepfakes.com/search/%s')
        self.content = []
        self.links = []
        self.cats = []
    def SearchSite(self,term):
        try:
            self.content.append({'name' : '[COLOR magenta]Content From %s[/COLOR]' % SiteName ,'url': '', 'image' : DefaultImage})
            term = term.replace(' ','-')
            link = requests.get(self.Search % term,headers=headers).text
            soup = BeautifulSoup(link, 'html.parser')
            data = soup.find_all('div', class_={'item'})
            for i in data:
                name = i.img['alt']
                media = i.a['href']
                if not Base_Domain in media: media=Base_Domain+media
                icon = i.img['data-original']
                self.content.append({'name' : name, 'url': media, 'image' : icon})
            if len(self.content) > 3: return self.content
            else: pass
        except Exception as e: xbmc.log('SCRAPER ERROR : %s ::: %s'% (SiteName,e),xbmc.LOGINFO)
    def MainContent(self,url):
        if url == '': url = self.Base
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('div', class_={'item'})
        for i in data:
            name = i.img['alt']
            media = i.a['href']
            if not Base_Domain in media: media=Base_Domain+media
            icon = i.img['data-original']
            self.content.append({'name' : name, 'url': media, 'image' : icon})
        return self.content
    def ResolveLink(self,url):
        try:
            c = requests.get(url,headers=headers).text
            patternlic = r'''license_code:.*?['"](.*?)['"]'''
            getlic = re.findall(patternlic,c,flags=re.DOTALL)[0]
            pattern = r'''url.*?(function[^'"]+mp4.*?)['"].*?_text:.*?['"](.*?)['"]'''
            r = re.findall(pattern,c,flags=re.DOTALL)
            for source,quality in r:
                final_url = kvs_decode(source, getlic)
                headers.update({'Referer': url})
                source2 = requests.get(final_url,headers=headers,stream=True)
                newsource = source2.url
                playurl = ('%s|Referer=https://mrdeepfakes.com/' % newsource)
                if not 'skip' in quality.lower(): self.links.append({'name' : quality, 'url': playurl})
            return self.links
        except Exception as e: xbmc.log('SCRAPER ERROR : %s ::: %s'% (SiteName,e),xbmc.LOGINFO)
    def GetCats(self):
        c = requests.get(self.CatUrl, headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        data = soup.find_all('a', class_={'item'})
        for i in data:
            try:
                name = i['title']
                url = i['href']
                if not Base_Domain in url: url = Base_Domain+url
                self.cats.append({'name' : name, 'url': url+'?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=1'})
            except: pass
        return self.cats
    def GetNextPage(self,url):
        if url == '':
            url = 'https://mrdeepfakes.com/?mode=async&function=get_block&block_id=list_videos_most_recent_videos&sort_by=post_date&from=2'
            return url
        else:
            oldurl = url.rsplit('from=', 2)[0]
            getcurrent = url.rsplit('from=', 1)[-1]
            NewNextPageUrl = int(getcurrent) + 1
            NextPageUrl = ('%sfrom=%s' % (oldurl,NewNextPageUrl))
            return NextPageUrl
                