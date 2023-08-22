import requests
from bs4 import BeautifulSoup
import xbmcgui
import re
import base64
import urllib.parse
import json
import xbmc
dialog = xbmcgui.Dialog()
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82',
		   'Referer' : 'https://www.pornerbros.com/',
		   'Origin' : 'https://www.pornerbros.com'}
Base_Domain = 'https://www.pornerbros.com'
SiteName = 'Pornerbros'
DefaultImage = 'https://raw.githubusercontent.com/nemesis668/repository.streamarmy18-19/917d31e44e35d06957f37e1e65bf89b2c549d36d/plugin.video.cwm/icon.png'
class Scraper:
    def __init__(self):
        self.Base = 'https://www.pornerbros.com/videos?p=1'
        self.CatUrl = 'https://www.pornerbros.com/tags'
        self.Search = ('https://www.pornerbros.com/search?q=%s')
        self.content = []
        self.links = []
        self.cats = []
    def SearchSite(self,term):
        try:
            self.content.append({'name' : '[COLOR magenta]Content From %s[/COLOR]' % SiteName ,'url': '', 'image' : DefaultImage})
            term = term.replace(' ','%20')
            link = requests.get(self.Search % term,headers=headers).text
            pattern = r'''window.INITIALSTATE.*?['"](.*?)['"]'''
            data = re.findall(pattern,link)[0]
            data = base64.b64decode(data)
            data = data.decode('utf-8')
            getbase = urllib.parse.unquote(data)
            data = json.loads(getbase)
            data = data['page']['videos']['_embedded']['items']
            for i in data:
                try:
                    title = i['title']
                    icon = i['thumbnailsList'][0]
                    url1 = i['slug']
                    url2 = i['uuid']
                    finalurl = ('https://www.pornerbros.com/videos/%s_%s' % (url1,url2))
                    self.content.append({'name' : title, 'url': finalurl, 'image' : icon})
                except: pass
            if len(self.content) > 3: return self.content
            else: pass
        except Exception as e: xbmc.log('SCRAPER ERROR : %s ::: %s'% (SiteName,e),xbmc.LOGINFO)
    def MainContent(self,url):
        if url == '': url = self.Base
        link = requests.get(url,headers=headers).text
        pattern = r'''window.INITIALSTATE.*?['"](.*?)['"]'''
        data = re.findall(pattern,link)[0]
        data = base64.b64decode(data)
        data = data.decode('utf-8')
        getbase = urllib.parse.unquote(data)
        data = json.loads(getbase)
        if '/tags/' in url: data = data['page']['embedded']['videos']['_embedded']['items']
        else: data = data['page']['videos']['_embedded']['items']
        for i in data:
            try:
                title = i['title']
                icon = i['thumbnailsList'][0]
                url1 = i['slug']
                url2 = i['uuid']
                finalurl = ('https://www.pornerbros.com/videos/%s_%s' % (url1,url2))
                self.content.append({'name' : title, 'url': finalurl, 'image' : icon})
            except: pass
        return self.content
        
    def ResolveLink(self,url):
        link = requests.get(url,headers=headers).text
        pattern = r'''window.INITIALSTATE.*?['"](.*?)['"]'''
        qualpattern = r'''"videoQuality": "(.*?)"'''
        qualtype = re.findall(qualpattern,link)[0]
        data = re.findall(pattern,link)[0]
        data = base64.b64decode(data)
        data = data.decode('utf-8')
        convert = urllib.parse.unquote(data)
        patern2 = r'''['"]mediaId['"]:(.*?),'''
        mediaid = re.findall(patern2, convert)[0]
        if qualtype == 'SD': posturl = 'https://token.pornerbros.com/%s/desktop/480+360+240' % mediaid
        else: posturl = 'https://token.pornerbros.com/%s/desktop/720+480+360+240' % mediaid
        getsources = requests.post(posturl,headers=headers).json()
        availablequal = []
        for source in getsources:
            availablequal.append(source)
        for each in availablequal:
            media = getsources[each]
            qual = each
            url = media['token']
            self.links.append({'name' : qual, 'url': url+'|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'})
        return self.links
        
    def GetCats(self):
        c = requests.get(self.CatUrl,headers=headers).text
        soup = BeautifulSoup(c,'html.parser')
        r = soup.find_all('div', class_={'category-item'})
        for i in r:
            try:
                title = i.a['title']
                url = i.a['href']
                if not Base_Domain in url: url = Base_Domain+url
                self.cats.append({'name' : title, 'url': url+'?p=1'})
            except: pass
        return self.cats
        
    def GetNextPage(self,url):
        if url == '':
            url = 'https://www.pornerbros.com/videos?p=2'
            return url
        else:
            if not '/tags/' in url:
                getcurrent = re.findall(r'\d+',url)[0]
                NewNextPageUrl = int(getcurrent) + 1
                NextPageUrl = ('https://www.pornerbros.com/videos?p=%s' % NewNextPageUrl)
                return NextPageUrl
            else:
                NextPageUrl = url.split('p=')[-1]
                oldurl = url.rsplit('p=', 1)[0]
                NewNextPageUrl = int(NextPageUrl) + 1
                NextPageUrl = ('%sp=%s' % (oldurl,NewNextPageUrl))
                return NextPageUrl