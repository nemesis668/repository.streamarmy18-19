# -*- coding: utf-8 -*-
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
from six.moves.urllib.parse import parse_qs, quote_plus, urlparse, parse_qsl, urljoin
from six import PY2
import re,json,base64,os

import client
import cache
import workers
import jsunpack
import utils
import kodi
import log_utils
import resolveurl
import requests
from bs4 import BeautifulSoup
dialog	= xbmcgui.Dialog()

def CLEANUP(text):

	text = str(text)
	text = text.replace('\\r','')
	text = text.replace('\\n','')
	text = text.replace('\\t','')
	text = text.replace('\\','')
	text = text.replace('<br />','\n')
	text = text.replace('<hr />','')
	text = text.replace('&#039;',"'")
	text = text.replace('&#39;',"'")
	text = text.replace('&quot;','"')
	text = text.replace('&rsquo;',"'")
	text = text.replace('&amp;',"&")
	text = text.replace('&#8211;',"&")
	text = text.replace('u0026',"&")
	text = text.replace('&#8217;',"'")
	text = text.replace('&#038;',"&")
	text = text.lstrip(' ')
	text = text.lstrip('	')

	return text
class streamer:

    def resolve(self, url, pattern=None):
        if pattern: 

            u = self.generic(url, pattern)
            
        else:
        
            if 'eporner.com' in url: u = self.eporner(url)
            
            elif 'girlfriendvideos.com' in url: u = self.girlfriendvideos(url)
            
            elif 'redtube.com' in url: u = self.redtube(url)
            
            elif 'xnxx.com' in url: u = self.xnxx(url)
            
            elif 'siska.video' in url: u = self.siska(url)
            
            elif 'ghettotube.com' in url: u = self.ghettotube(url)
            
            elif 'daftporn.com' in url: u = self.daftporn(url)
            
            elif 'collectionofbestporn.com' in url: u = self.collectionofbestporn(url)
            
            elif 'pornrox.com' in url: u = self.pornrox(url)

            elif 'porn00' in url: u = self.porn00(url)
            
            elif 'fapality.com' in url: u = self.fapality(url)
            
            elif 'justporno.tv' in url: u = self.justporno(url)

            elif '4tube.com' in url: u = self.fourtube(url)
            
            elif 'chaturbate.com' in url: u = self.chaturbate(url)

            elif 'perfectgirls.xxx' in url: u = self.perfectgirls(url)

            elif 'pornhub.com' in url: u = self.pornhub(url)
            
            elif 'zzcartoon.com' in url: u = self.zzcartoon(url)
            
            elif 'pornheel.com' in url: u = self.pornheel(url)
            
            elif 'porn.com' in url: u = self.generic(url)
            
            elif 'pandamovie.info' in url: u = self.pandamovie(url)

            elif 'winporn.com' in url: u = self.winporn(url)

            elif 'yuvutu.com' in url: u = self.yuvutu(url)

            elif 'huge6.com' in url: u = self.hugesix(url)

            elif 'boobsandtits.co.uk' in url: u = self.boobntit(url)
            
            elif 'sexmax.co' in url: u = self.sexmax(url)
            elif 'freeomovie.info' in url: u = self.freeomovie(url)

            elif 'drtube' in url: u = self.drtube(url)
            
            elif 'porndig.com' in url: u = self.porndig(url)
            
            elif 'nuvid' in url: u = self.nuvid(url)
            
            elif 'xxxdan' in url: u = self.xxxdan(url)
            
            elif 'solopornoitaliani' in url: u = self.solopornoitaliani(url)
            
            elif 'spreadporn.org' in url: u = self.spreadporn(url)

            elif 'befuck.com' in url: u = self.befuck(url)
            
            elif 'megasesso' in url: u = self.megasesso(url)
            
            elif 'freeones' in url: u = self.freeones(url)
            
            elif 'fuqer.com' in url: u = self.fuqer(url)
            
            elif 'satan18av' in url: u = self.satan18av(url)

            elif 'overthumbs' in url: u = self.overthumbs(url)

            elif 'streamate.com' in url: u = self.streamate(url)

            elif 'mixhdporn.com' in url: u = self.mixhd(url)      
            
            elif 'xtheatre.net' in url: u = self.xtheatre(url)                                            

            #elif 'chaturbate.com' in url: u = self.chaturbate(url)                      

            elif 'nxgx.com' in url: u = self.nxgx(url)

            elif 'hqporner.com' in url: u = self.hqporner(url)

            
            
            elif 'hclips.com' in url: u = self.hclips(url)
            
            elif 'watchxxxfree.tv' in url: u = self.watchxxxfree(url)
            
            elif 'youngpornvideos.com' in url: u = self.youngpornvideos(url)
            
            elif 'javhihi.com' in url: u = self.javhihi(url)
            
            elif 'txxx.com' in url: u = self.txxx(url)
            
            elif 'vrsumo.com' in url: u = self.vrsumo(url)
            
            elif 'anysex.com' in url: u = self.anysex(url)
            
            elif '123pandamovie.me' in url: u = self.pandamovie(url)
            
            elif 'pornxs.com' in url: u = self.pornxs(url)
            
            elif 'streamingporn.xyz' in url: u = self.streamingporn(url)
            
            elif '3movs.com' in url: u = self.threemovs(url)
            
            elif 'watchmygf.me' in url: u = self.watchmygf(url)
            
            elif 'vrsmash.com' in url: u = self.vrsmash(url)
            
            elif 'spankbang.com' in url: u = self.spankbang(url)
            
            elif 'teenpornsite.net' in url: u = self.teenpornsite(url)
            
            elif 'watchpornfree.info' in url: u = self.watchpornfree(url)
            
            elif 'pornhd.com' in url: u = self.pornhd(url)
            
            elif 'motherless.com' in url: u = self.motherless(url)
            
            elif 'xvideos.com' in url: u = self.xvideos(url)
            
            elif 'youjizz.com' in url: u = self.youjizz(url)
            
            elif 'adult-tv-channels.com' in url: u = self.adult_tv(url)
            


            else: u = self.generic(url, pattern=None)

        return u

    def generic(self, url, pattern=None):

        if 'youporn.com' in url: u = self.youporn(url)
        try:
            r = client.request(url)
            if pattern: s=re.findall(r'%s' % pattern, r)
            else:
                patterns = [
                            r'''\s*=\s*[\'\"](http.+?)[\'\"]''', \
                            r'''\s*=\s*['"](http.+?)['"]''', \
                            r'''['"][0-9_'"]+:\s[\'\"]([^'"]+)''', \
                            r'''\(\w+\([\'\"]([^\'\"]*)''', \
                            r'''[\'\"]\w+[\'\"]:['"]([^'"]*)''', \
                            r'''\s*=\s*[\'\"](http.+?)[\'\"]''', \
                            r'''\s*:\s*[\'\"](//.+?)[\'\"]''', \
                            r'''\:[\'\"](\.+?)[\'\"]''', \
                            r'''\s*\(\s*[\'\"](http.+?)[\'\"]''', \
                            r'''\s*=\s*[\'\"](//.+?)[\'\"]''', \
                            r'''\w*:\s*[\'\"](http.+?)[\'\"]''', \
                            r'''\w*=[\'\"]([^\'\"]*)''', \
                            r'''\w*\s*=\s*[\'\"]([^\'\"]*)''', \
                            r'''(?s)<file>([^<]*)''', \
                            ]
                
                s = []
                for pattern in patterns: 
                    l = re.findall(pattern, r)
                    s += [i for i in l if (urlparse.urlparse(i).path).strip('/').split('/')[-1].split('.')[-1] in ['mp4', 'flv', 'm3u8']]

                if s: s = [i for i in s if (urlparse.urlparse(i).path).strip('/').split('/')[-1].split('.')[-1] in ['mp4', 'flv', 'm3u8']]
                else: s = client.parseDOM(r, 'source', ret='src', attrs = {'type': 'video.+?'})
                
                if not s: 
                    log_utils.log('Error resolving %s :: Error: %s' % (url,str(e)), log_utils.LOGERROR)
                    return
                    
                s = ['http:' + i if i.startswith('//') else i for i in s]
                s = [urlparse.urljoin(url, i) if not i.startswith('http') else i for i in s]
                s = [x for y,x in enumerate(s) if x not in s[:y]]

            self.u = []
            def request(i):
                try:
                    i = i.replace(' ','%20')
                    c = client.request(i, output='headers', referer=url)
                    checks = ['video','mpegurl','html']
                    if any(f for f in checks if f in c['Content-Type']): self.u.append((i, int(c['Content-Length'])))
                except:
                    pass
            threads = []
            for i in s: threads.append(workers.Thread(request, i))
            [i.start() for i in threads] ; [i.join() for i in threads]

            u = sorted(self.u, key=lambda x: x[1])[::-1]
            
            mobile_mode = kodi.get_setting('mobile_mode')
            if mobile_mode == 'true': u = client.request(u[-1][0], output='geturl', referer=url)
            else: u = client.request(u[0][0], output='geturl', referer=url)
            log_utils.log('Returning %s from XXX-O-DUS Resolver' % str(u), log_utils.LOGNOTICE)
            return u
        except Exception as e:
            log_utils.log('Error resolving %s :: Error: %s' % (url,str(e)), log_utils.LOGERROR)

    # needed to generate hash for eporner
    def encode_base_n(self, num, n, table=None):
        FULL_TABLE = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if not table:
            table = FULL_TABLE[:n]

        if n > len(table):
            raise ValueError('base %d exceeds table length %d' % (n, len(table)))

        if num == 0:
            return table[0]

        ret = ''
        while num:
            ret = table[num % n] + ret
            num = num // n
        return ret

    def girlfriendvideos(self, url):
        
        try:
            r = client.request(url)
            r = r.replace('\\','')
            pattern = r"""<video src="([^"]+)"""
            link = re.findall(pattern,r)[0]
            u = 'http://www.girlfriendvideos.com' + link
            return u
        except: return 

    def eporner(self, url):
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
        headers = {'User-Agent': ua}
        names = []
        srcs  = []
        c = requests.get(url,headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        r = soup.find('div', class_={'dloaddivcol'})
        for links in r.find_all('a'):
            link = links['href']
            title = links.text
            title = title.replace('Download','')
            url = ('https://www.eporner.com%s' %link)
            names.append(kodi.giveColor(title,'white',True))
            srcs.append(url)
        selected = kodi.dialog.select('Select a link.',names)
        if selected < 0:
            kodi.notify(msg='No option selected.')
            kodi.idle()
            quit()
        else:
            u = srcs[selected]
            return u
            # dialog.ok("EPORNER","HERE")
        #try:
            # r = client.request(url)
            # pattern = r"""{\s*vid:\s*'([^']+)',\s*hash\s*:\s*["\']([\da-f]{32})"""
            # id,hash = re.findall(pattern,r)[0]
            # hash_code = ''.join((self.encode_base_n(int(hash[lb:lb + 8], 16), 36) for lb in range(0, 32, 8)))
            # load_url = 'https://www.eporner.com/xhr/video/%s?hash=%s&device=generic&domain=www.eporner.com&fallback=false&embed=false&supportedFormats=mp4' % (id,hash_code)
            # r = client.request(load_url).replace("\/", "/")
            # r = json.loads(r).get("sources", {}).get('mp4', {})
            # r = [(i, r[i].get("src")) for i in r]
            # u = sorted(r, key=lambda x: int(re.search('(\d+)', x[0]).group(1)), reverse=True)
            # return u
        #except: return 

    def watchxxxfree(self, url):
        
        try:
            r = client.request(url)
            pattern = r"""<iframe.+?src=['"]([^'"]+)"""
            e = re.findall(pattern,r)
            for links in e:
                return links
        except: return

    def porn00(self, url):
        
        try:
            r = client.request(url)
            pattern = r'''<ul>.+?iframe.+?\?v=([\d]+)'''
            id=re.findall(pattern,r,re.DOTALL)[0]
            url = 'http://www.porn00.org/plays/?v=%s' % id
            cookie = client.request(url, output='cookie')
            r = client.request(url, cookie=cookie)
            pattern = r'''(?:)file\:\s*[\'\"]([^\'\"]+)[\'\"]\,\s*\w+\:\s*[\'\"]([^\'\"]+)'''
            r=re.findall(pattern,r)
            r = [(i[1],i[0]) for i in r if i]
            u = sorted(r, key=lambda x: int(re.search('(\d+)', x[0]).group(1)), reverse=True)
            return u
        except: return

    def justporno(self, url):
        try:        
            r = client.request(url)
            s = re.findall('''source\s*src=['"]+([^'"]+)''', r)[0]
            ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
            headers = {'User-Agent': ua}
            response = requests.get(s, headers=headers, stream=True)
            play = response.url
            xbmc.Player().play(play)
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
        except:
            return

    def freeomovie(self, url):
        
        #dialog.ok("HERE",str(url))
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
        headers = {'User-Agent': ua}
        c = requests.get(url, headers=headers).text
        soup = BeautifulSoup(c, 'html5lib')
        r = soup.find('div', id={'pettabs'})
        names = []
        srcs  = []
        found = 0
        for links in r.find_all('a'):
            sources = links['href']
            if 'drivevideo' in sources: sources = sources.split('?link=')[1]
            titles = links.text
            if resolveurl.HostedMediaFile(sources).valid_url():
                names.append(kodi.giveColor(titles,'white',True))
                srcs.append(sources)
        selected = kodi.dialog.select('Select a link.',names)
        if selected < 0:
            kodi.notify(msg='No option selected.')
            kodi.idle()
            quit()
        else:
            url2 = srcs[selected]
            try:
                u = resolveurl.HostedMediaFile(url2).resolve()
                xbmc.Player().play(u)
            except : dialog.notification('XXX-O-DUS', '[COLOR yellow]Resolver Couldn\'t Resolve Link, Try Another[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
    def fourtube(self, url):
        dialog.ok("URL",str(url))
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
        headers = {'User-Agent': ua}
        link = requests.get(url, headers=headers).text
        soup = BeautifulSoup(link, 'html5lib')
        content = soup.find('div', class_={'links-list'})
        names = []
        srcs  = []
        for i in content.find_all('button'):
            IDS = i['data-id']
            quality = i['data-quality']
            names.append(quality)
            srcs.append(IDS)
        selected = kodi.dialog.select('Select a link.',names)
        if selected < 0:
            kodi.notify(msg='No option selected.')
            kodi.idle()
            quit()
        else:
            token = srcs[selected]
            qual = names[selected]
            apiurl = ('https://token.4tube.com/%s/desktop/%s' % (token,qual))
            ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
            headers = {'User-Agent': ua,
                        'Referer' : url,
                        'Origin' : 'https://www.4tube.com'}
            link = requests.post(apiurl, headers=headers).text
            data = json.loads(link)
            play = data[qual]['token']
            xbmc.Player().play(play)
            xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
            
    def spankbang(self, url):
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
        headers = {'User-Agent': ua}
        link = requests.get(url, headers=headers).text
        soup = BeautifulSoup(link, 'html5lib')
        content = soup.find('div', id={'video'})['data-streamkey']
        dialog.ok("CONTENT",str(content))
        apiurl = 'https://spankbang.com/api/videos/stream'
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
        headers = {'User-Agent': ua,
                    'Referer' : url,
                    'X-Requested-With': 'XMLHttpRequest'}
        post_data = {'id': content}
        link = requests.post(apiurl, data=post_data, headers=headers).text
        pattern = r'''['"](http.*?)['"]'''
        getlinks = re.findall(pattern,link,flags=re.DOTALL)
        names = [] ; srcs  = []
        for links in getlinks:
            if '2160p' in links: title = '4K'
            elif '1080p' in links: title = '1080'
            elif '720p' in links: title = '720'
            elif '480p' in links: title = '480'
            else: title = 'SD'
            names.append(title)
            srcs.append(links)
        selected = kodi.dialog.select('Select a link.',names)
        if selected < 0:
            kodi.notify(msg='No option selected.')
            kodi.idle()
            quit()
        else:
            play = srcs[selected]
            xbmc.Player().play(play)
            xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
            xbmc.executebuiltin('Dialog.Close(busydialog)')
    def freeones(self, url):
        try:        
            u = client.request(url)
            e = re.findall('_script"\ssrc="([^"]*)', u)[0]
            return self.generic(e)
        except:
            return
            
    def fuqer(self, url):
        try:        
            u = client.request(url)
            e = re.findall('config:\'([^\']*)', u)[0]
            return self.generic(e)
        except:
            return

    def perfectgirls(self, url):
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
                   'X-Requested-With' : 'XMLHttpRequest'}
        try:
            link = requests.get(url,headers=headers).content
            soup = BeautifulSoup(str(link),'html.parser')
            r = soup.find('video', class_={'video-js'})
            names = []
            srcs  = []
            for vids in r.find_all('source'):
                qual = vids['title']
                source = vids['src']
                names.append(kodi.giveColor(qual,'white',True))
                srcs.append(source)
            selected = kodi.dialog.select('Select a link.',names)
            if selected < 0:
                kodi.notify(msg='No option selected.')
                kodi.idle()
                quit()
            else:
                url2 = srcs[selected]
                return url2
        except: return


    def pornhub(self, url):
        try:
            r = client.request(url)
            vars = re.findall('var\s+(.+?)\s*=\s*(.+?);', r)
            link = re.findall('quality_\d+p\s*=\s*(.+?);', r)[0]
            link = [i.strip() for i in link.split('+')]
            link = [i for i in link if i.startswith('*/')]
            link = [re.sub('^\*/', '', i) for i in link]
            link = [(i, [x[1] for x in vars if x[0] == i]) for i in link]
            link = [i[1][0] if i[1] else i[0] for i in link]
            link = ''.join(link)
            link = re.sub('\s|\+|\'|\"', '', link)
            return link
        except:
            return 
    #pornheel gets url and provider name list
    def pornheel(self, url):
        try:
            u = client.request(url)
            e = re.findall('<a\shref="([^"]*)".+?">Streaming\s([^<]*)', u)
            e = [(client.request(i[0], output='geturl'), i[1]) for i in e if i]
            return e
        except:
            return 

    # def pandamovie(self, url):
        # try:
            # u = client.request(url)
            # e = re.findall('<li>.+?on ([^"]*).+?f="([^"]*)', u)
            # e = [(i[0],i[1]) for i in e if 'pandamovie' not in i[1]]
            # return e
        # except:
            # return


    def winporn(self, url):
        try:
            r = client.request(url)
            link = re.findall('var video_id = "(.+?)"', r)[0]
            r = 'http://nl.winporn.com/player_config_json/?vid=' + link + '&aid=0&domain_id=0&embed=0&ref=&check_speed=0'
            return self.generic(r)
        except:
            return


    def yuvutu(self, url):
        try:
            r = client.request(url)
            r = client.parseDOM(r, 'iframe', ret='src')
            r = [i for i in r if 'embed' in i][0]
            r = urlparse.urljoin(url, r)
            return self.generic(r)
        except:
            return
            
                        
    def hugesix(self, url):
        try:
            main = client.request(url)
            links = re.findall('config=(.+?)",', main)[0] 
            link = links
            link = client.request(link)
            express1 = '<filehd>(.+?)</filehd>'
            express2 = '<file>(.+?)</file>'
            play = re.compile(express1, re.MULTILINE|re.DOTALL).findall(link)
            if not play: play = re.compile(express2, re.MULTILINE|re.DOTALL).findall(link)
            play = play[0]
            return play
        except:
            return

    def boobntit(self, url):
        try:
            main = client.request(url)
            link = client.parseDOM(main, 'div', attrs = {'id': 'player'})
            link = client.parseDOM(link, 'iframe', ret='src')
            link = link[0]
            return self.generic(link)
        except:
            return self.generic(url)
            
    def sexmax(self, url):
        try:        
            url = client.request(url)
            express = '<div id="player-embed">.+?<iframe src="(.+?)"'
            link = re.compile(express, re.MULTILINE|re.DOTALL).findall(url)[0]
            dir = client.request(link)
            dir = dir.replace('\/', '/')
            express = '"src":"(.+?)"'
            link = re.compile(express, re.MULTILINE|re.DOTALL).findall(dir)[0]
            return link
        except:
            return

    def drtube(self, url):
        try:        
            url = client.request(url)
            express = 'vid:(.+?),'
            link = re.compile(express, re.MULTILINE|re.DOTALL).findall(url)[0]
            link = 'http://www.drtuber.com/player_config_json/?vid=' + link + '&aid=0&domain_id=0&embed=0&ref=&check_speed=0'
            return self.generic(link)
        except:
            return
            
    def nuvid(self, url):
        try:        
            url = client.request(url)
            express = 'vid:(.+?),'
            link = re.compile(express, re.MULTILINE|re.DOTALL).findall(url)[0]
            link = 'http://www.nuvid.com/player_config_json/?vid=' + link + '&aid=0&domain_id=0&embed=0&ref=&check_speed=0'
            html = client.request(link)
            html = html.replace('\/', '/')
            express2 = '"hq":"(.+?)"'
            express3 = '"lq":"(.+?)"'
            play = re.compile(express2, re.MULTILINE|re.DOTALL).findall(html)
            if not play: play = re.compile(express3, re.MULTILINE|re.DOTALL).findall(html)
            play = play[0]
            return play
        except:
            return
            
    def solopornoitaliani(self, url):
        try:        
            url = client.request(url)
            express = '\'videoid\',\'(.+?)\''
            link = re.compile(express, re.MULTILINE|re.DOTALL).findall(url)[0]
            link = 'http://www.solopornoitaliani.xxx/vdata/' + link + '.flv'
            return link
        except:
            return
            
    def megasesso(self, url):
        try:        
            u = client.request(url)
            u = client.parseDOM(u, 'div', attrs = {'class': 'player-iframe'})
            u = [(client.parseDOM(i, 'iframe', ret='src')) for i in u]
            u = [(client.replaceHTMLCodes(i[0]).encode('utf-8')) for i in u]
            u = 'http://www.megasesso.com' + u[0]
            return self.generic(u)
        except:
            return

           

    def overthumbs(self, url):
        try:
            u = client.request(url)
            e = re.findall('(?s)id="play".+?src="([^"]*)', u)[0]
            e = ('http://overthumbs.com' + e)
            r = client.request(e)
            unpack = jsunpack.unpack(r)
            try:
                source = re.findall('file.+?"([^"]*)',unpack)[0]
            except IndexError: source = re.findall('src.+?"([^"]*)',unpack)[0]
            xbmc.Player().play(source)
        except:
            return

    def streamate(self, url):
        try:
            u = client.request(url)
            e = re.findall('iframe\.src = \'([^\']*)', u)
            e = 'https://www.streamate.com' + e[0]
            r = client.request(e)
            r = re.findall('data-manifesturl="([^"]*)', r)[0]
            return self.generic(r)
        except:
            return

    #spreadporn gets link and provider name and provider logo
    def spreadporn(self, url):
        try:
            u = client.request(url)
            e = re.findall('(?s)<li class.+?"stream".+?k="([^"]*).+?c="([^"]*)"\salt="([^"]*)', u)
            return e
        except:
            return
            
    def satan18av(self, url):
        try:
            u = client.request(url)
            e = re.findall('<iframe src="([^"]*)', u)[0]
            return e
        except:
            return

    def befuck(self, url):
        try:
            u = client.request(url)
            e = re.findall('<source src="([^"]*)', u)[0]
            return e
        except:
            return      
    #mixhd gets link and provider  
    def mixhd(self, url):
        try:
            u = client.request(url)
            u = re.findall('<iframe src="([^"]*)', u)
            u = [(i,i.split('//')[-1].split('.')[0]) for i in u]
            return u
        except:
            return
    #xtheatre gets link and provider   
    def xtheatre(self, url):
        try:
            u = client.request(url)
            u = re.findall('<iframe src="([^"]*)', u)
            u = [(i,i.split('//')[-1].split('.')[0]) for i in u]
            return u
        except:
            return

    def youporn(self, url):
        try:        
            headers = {'User-Agent' : 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'}
            link = requests.get(url,headers=headers).text
            soup = BeautifulSoup(link, 'html.parser')
            r = soup.find('div', class_={'feature videoLike'})['data-videoid']
            apiurl = ('https://www.youporn.com/api/video/media_definitions/%s' % r)
            link = requests.get(apiurl,headers=headers).json()
            names = []
            srcs  = []
            for i in link:
                quality = i['quality']
                mediia = i['videoUrl']
                names.append(kodi.giveColor(quality,'white',True))
                srcs.append(mediia)
            selected = kodi.dialog.select('Select a link.',names)
            if selected < 0:
                kodi.notify(msg='No option selected.')
                kodi.idle()
                quit()
            else:
                url2 = srcs[selected]
                xbmc.Player().play(url2)
        except: pass
    def pornrox(self,url):
        c = client.request(url)
        pattern = r'''video_url:\s+['"](.*?)['"]'''
        r = re.findall(pattern,c,flags=re.DOTALL)[0]
        xbmc.Player().play(r)
    def chaturbate(self, url):
        import random
        from inputstreamhelper import Helper
        api_url = 'https://chaturbate.com/get_edge_hls_url_ajax/'
        user_agent_list = [
            ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
             "Chrome/77.0.3865.90 Safari/537.36"),
            ("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
             "Chrome/79.0.3945.130 Safari/537.36"),
        ]

        def get_headers():
            headers = {
                "Connection": "keep-alive",
                "Cache-Control": "max-age=0",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": random.choice(user_agent_list),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
                "Sec-Ch-Ua" : "Microsoft Edge;v=131, Chromium;v=131, Not_A Brand;v=24",
                "Referer" : "https://chaturbate.com/",
                "x-requested-with": "XMLHttpRequest"
            }
            return headers
            
            

        dialog.notification('XXX-O-DUS', '[COLOR yellow]Getting Cam Now[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
        #try:
        room_slug = url.split('.com/')[1].replace('/','')
        Headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36' }
        #pattern = r'''hls_source.+(http.*?m3u8)'''
        link = requests.get(url,headers=get_headers())
        csrf_token = link.cookies.get_dict()['csrftoken']
        data = {'room_slug': room_slug,
                'bandwidth' : 'high',
                'current_edge': '',
                'exclude_edge': '',
                'csrfmiddlewaretoken': csrf_token}
        source = requests.post(api_url, headers=get_headers(),data=data).json()
        #dialog.ok("SOURCE",str(source))
        cam = source['url']
        cam = cam.replace('live-hls','live-c-fhls').replace('playlist.m3u8','playlist_sfm4s.m3u8').replace('-ams','-rtm')
        #cam = cam+'|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36&Keep-Alive=true&Referer=https://chaturbate.com&Origin=https://chaturbate.com'
        #source = re.findall(pattern,link,flags=re.DOTALL)[0]
        #if PY2: source = source.replace('\u002D','-')
        #else: source = source.replace('u002D','-').replace('\-','-')
        #xbmc.log("%s" % source, xbmc.LOGINFO)
        is_helper = Helper("hls")
        if is_helper.check_inputstream():
            play_item = xbmcgui.ListItem(path=cam)
            play_item.setProperty('inputstreamaddon', is_helper.inputstream_addon)
            play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            play_item.setProperty('inputstream', 'inputstream.adaptive')
            play_item.setProperty('inputstream.adaptive.common_headers', 'headername=encoded_value&User-Agent=%s&Origin=https://chaturbate.com' % random.choice(user_agent_list))
            xbmc.Player ().play(cam, play_item, False)
        #xbmc.Player ().play(cam)
        #except: dialog.notification('XXX-O-DUS', '[COLOR yellow]Performer Is Offline[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
            
    def nxgx(self, url):
        try:        
            r = client.request(url)
            pattern = r"""iframe\s*src=['"]([^'"]+)"""
            u = re.findall(pattern,r)[0]
            u = resolveurl.HostedMediaFile(u).resolve()
            return u
        except: 
            return

    def hqporner(self, url):
        # Thank you to Cummination for letting me use their resolver code for HQPorner
        #try:
            r = client.request(url)
            pattern = r"""iframe\s*width=['"]\d+['"]\s*height=['"]\d+['"]\s*src=['"]([^'"]+)"""
            url = re.findall(pattern,r)[0]
            url = url if url.startswith('http') else 'https:' + url
            names = []
            srcs  = []
            videopage = requests.get(url).text
            vdiv = re.search(r'function do_pl\(\)\s*{(.*)};', videopage)
            if vdiv:
                vdiv = vdiv.group(1)
                s = re.search(r'replaceAll\("([^"]+)",\s*([^)]+)', vdiv)
                if s:
                    var = s.group(1)
                    params = s.group(2).split('+')
                    repl = ''
                    for param in params:
                        if param.startswith('"'):
                            repl += param[1:-1]
                        else:
                            repl += re.findall(r'{0}="([^"]+)'.format(param), vdiv)[0]
                    vdiv = vdiv.replace(var, repl)
                videopage = vdiv
            videos = re.compile(r'source\s*src=\\"([^\\]+).+?\\"([^\\\s]+)', re.DOTALL | re.IGNORECASE).findall(videopage)
            if not videos:
                videos = re.compile(r'file:\s*"([^"]+mp4)",\s*label:\s*"\d+', re.DOTALL | re.IGNORECASE).findall(videopage)
            for links,qual in videos:
                if not 'http' in links: links='http:'+links
                names.append(kodi.giveColor(qual,'white',True))
                srcs.append(links)
            selected = kodi.dialog.select('Select a link.',names)
            if selected < 0:
                kodi.notify(msg='No option selected.')
                kodi.idle()
                quit()
            else:
                url2 = srcs[selected]
                xbmc.Player().play(url2)
        #except: pass
    def hclips(self, url):
        try:
            r = client.request(url)
            pattern = r'''<iframe width=['"]\d+['"]\s*height=['"]\d+['"]\s* src="(.*?)"'''
            url = re.findall(pattern,r)[0]
            r = client.request(url)
            pattern = r'''var\s*video_url="(.+?)"'''
            url2 = re.findall(pattern,r)[0]
            url2 = url2 + '|referer=' + url
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            xbmc.Player().play(url2)
        except:
            return
            
    def youngpornvideos(self,url):
            r = client.request(url)
            pattern = r'''file:\s+['"]([^'"]+m3u8.+)['"]'''
            r = re.findall(pattern,r)[0]
            xbmc.Player().play(r)
    def porndig(self,url):
        r = client.request(url)
        soup = BeautifulSoup(r,'html.parser')
        iframe = soup.find('div', class_={'video_wrapper'}).iframe['src']
        r = client.request(iframe)
        soup = BeautifulSoup(r,'html.parser')
        pattern = r'''['"]url['"]:.*?['"](.*?)['"].*?['"]label['"]:.*?['"](.*?)['"]'''
        c = re.findall(pattern,r,flags=re.DOTALL)
        names = []
        srcs  = []
        for url,quality in sorted(c, reverse=False):
            url = url.replace('\\','') + '|Referer='+iframe
            names.append(kodi.giveColor(quality,'white',True))
            srcs.append(url)
        selected = kodi.dialog.select('Select a link.',names)
        if selected < 0:
            kodi.notify(msg='No option selected.')
            kodi.idle()
            quit()
        else:
            url2 = srcs[selected]
            xbmc.Player().play(url2)
    def pornhd(self,url):
            r = client.request(url)
            pattern = r'''<source\s+src=['"]([^'"]+).*?label=['"](.*?)['"]'''
            r = re.findall(pattern,r)
            names = []
            srcs  = []
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            for url2,quality in sorted(r, reverse=False):
                names.append(kodi.giveColor(quality,'white',True))
                srcs.append(url2)
            selected = kodi.dialog.select('Select a link.',names)
            if selected < 0:
                kodi.notify(msg='No option selected.')
                kodi.idle()
                quit()
            else:
                url2 = srcs[selected]
                r = client.request(url2)
                dialog.ok("R",str(r))
                #url2 ='https://cdn-ht.pornhd.com/video_720p/283/ZtuTBZBgy2/video_720p.mp4?validfrom=1581689202&validto=1581862002&burst=4096k&rate=384k&hash=EWPwvXFHEnz09e8669aO92SiPQQ%3D'
                xbmc.Player().play(url2)
    def javhihi(self,url):
            r = client.request(url)
            pattern = r'''<source\s+src=['"]([^'"]+)['"]\s.+?data-res=['"]([^'"]+)'''
            r = re.findall(pattern,r)
            names = []
            srcs  = []
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            for url,quality in sorted(r, reverse=True):
                names.append(kodi.giveColor(quality,'white',True))
                srcs.append(url)
            selected = kodi.dialog.select('Select a link.',names)
            if selected < 0:
                kodi.notify(msg='No option selected.')
                kodi.idle()
                quit()
            else:
                url2 = srcs[selected]
                xbmc.Player().play(url2)
    def anysex(self,url):
        r = client.request(url)
        pattern = r'''<source\s+id=['"]video_source.+?src=['"]([^'"]+)['"].+?title=['"](.*?)['"]'''
        r = re.findall(pattern,r,flags=re.DOTALL)
        names = []
        srcs  = []
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        for url,quality in sorted(r, reverse=True):
            names.append(kodi.giveColor(quality,'white',True))
            srcs.append(url)
        selected = kodi.dialog.select('Select a link.',names)
        if selected < 0:
            kodi.notify(msg='No option selected.')
            kodi.idle()
            quit()
        else:
            url2 = srcs[selected]
            xbmc.Player().play(url2)

    def pandamovie(self,url):
        headers = {'User-Agent' : 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'}
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find_all('li', class_={'hosts-buttons-wpx'})
        names = []
        srcs  = []
        found = 0
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        dialog.notification('XXX-O-DUS', '[COLOR yellow]Checking For Links Now, Be Patient[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
        for i in data:
            url = i.a['href']
            if 'drivevideo' in url: url = url.split('?link=')[1]
            title = i.a['title']
            if resolveurl.HostedMediaFile(url).valid_url():
                names.append(kodi.giveColor(title,'white',True))
                srcs.append(url)
        selected = kodi.dialog.select('Select a link.',names)
        if selected < 0:
            kodi.notify(msg='No option selected.')
            kodi.idle()
            quit()
        else:
            url2 = srcs[selected]
            try:
                u = resolveurl.HostedMediaFile(url2).resolve()
                xbmc.Player().play(u)
            except : dialog.notification('XXX-O-DUS', '[COLOR yellow]Resolver Couldn\'t Resolve Link, Try Another[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
    #else: dialog.notification('XXX-O-DUS', '[COLOR yellow]No Working Links Found Sorry[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
        
    def txxx(self, url):
        try:
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            r = client.request(url)
            pattern = r'''<div class="download__link".+?<a href="(.*?)"'''
            url = re.findall(pattern,r)[0]
            url = CLEANUP(url)
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            xbmc.Player().play(url)
        except:
            return
            
    def vrsumo(self, url):
        try:
            r = client.request(url)
            pattern = r'''iframe\s+src=['"]([^'"]+)['"]'''
            url = re.findall(pattern,r)[1]
            r = client.request(url)
            pattern = r'''url:\s+['"]([^'"]+)['"]'''
            url = re.findall(pattern,r)[0]
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            xbmc.Player().play(url)
        except:
            return
            
    def streamingporn(self,url):
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        r = requests.get(url,headers=headers).text
        r = re.findall('<div class="entry-content">(.*?)</div>',r, flags=re.DOTALL)[0]
        pattern = r'''<a\s+href=['"]([^'"]+)['"].+?.>(.*?)<'''
        r = re.findall(pattern,r)
        names = []
        srcs  = []
        found = 0
        #xbmc.executebuiltin("Dialog.Close(busydialog)")
        for url,name in r:
            if not 'image' in url:
                if not 'severeporn' in name:
                    if resolveurl.HostedMediaFile(url).valid_url():
                        #dialog.notification('XXX-O-DUS', '[COLOR yellow]Checking For Links Now, Be Patient[/COLOR]', xbmcgui.NOTIFICATION_INFO, 13000)
                        try:
                            found +=1
                            #u = resolveurl.HostedMediaFile(url, include_popups=False).resolve()
                            name = name.replace('Download','').strip()
                            names.append(kodi.giveColor(name,'white',True))
                            srcs.append(url)
                        except: pass
        if found >= 1:
            selected = kodi.dialog.select('Select a link.',names)
            if selected < 0:
                kodi.notify(msg='No option selected.')
                kodi.idle()
                quit()
            else:
                url2 = srcs[selected]
                dialog.notification('XXX-O-DUS', '[COLOR yellow]Getting Links Now[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
                u = resolveurl.HostedMediaFile(url2, include_popups=False).resolve()
                xbmc.Player().play(u)
        else: dialog.notification('XXX-O-DUS', '[COLOR yellow]No Working Links Found Sorry[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
                
    def threemovs(self,url):
        link = client.request(url)
        play = re.findall('<div class="dropabble">.+?href="(.*?)"',link,flags=re.DOTALL)[0]
        xbmc.Player().play(play)
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
        
    def watchmygf(self,url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        link = client.request(url)
        play = re.findall('''video_url.+?['"](.*?)['"]''',link,flags=re.DOTALL)[0]
        rnd = re.findall(r'''rnd:\s+['"](.*?)['"]''',link,flags=re.DOTALL)[0]
        licence = re.findall(r'''license_code:\s+['"](.*?)['"]''',link,flags=re.DOTALL)[0]
        from resources.lib.modules import fundec
        decrypt = fundec.decryptHash(play, licence, 16)
        follow = ('%s?rnd=%s' % (decrypt,rnd))
        link2 = requests.get(follow,headers=headers,stream=True)
        play2 = link2.url
        xbmc.Player().play(play2)
        
    def vrsmash(self,url):
        link = client.request(url)
        play = re.findall('''"contentUrl":\s+"(.*?)"''',link,flags=re.DOTALL)[0]
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        xbmc.Player().play(play)

    def teenpornsite(self, url):
        dialog.notification('XXX-O-DUS', '[COLOR yellow]Getting Links Now[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
        r = client.request(url)
        pattern = r'''file['"]:['"]([^'"]+)['"].*?label['"]:['"](.*?)['"]'''
        r = re.findall(pattern,r,flags=re.DOTALL)
        names = []
        srcs  = []
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        for url,name in r:
            names.append(kodi.giveColor(name,'white',True))
            srcs.append(url)
        selected = kodi.dialog.select('Select a Quality.',names)
        if selected < 0:
            kodi.notify(msg='No option selected.')
            kodi.idle()
            quit()
        else:
            url2 = srcs[selected]
            xbmc.Player().play(url2)
    def collectionofbestporn(self, url):
        dialog.notification('XXX-O-DUS', '[COLOR yellow]Getting Links Now[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
        c = client.request(url)
        soup = BeautifulSoup(c,'html.parser')
        r = soup.find_all('source')
        names = []
        srcs  = []
        for i in r:
            quality = i['res']
            url = i['src']
            url = url+'|verifypeer=false'
            names.append(kodi.giveColor(quality,'white',True))
            srcs.append(url)
        selected = kodi.dialog.select('Select a Quality.',names)
        if selected < 0:
            kodi.notify(msg='No option selected.')
            kodi.idle()
            quit()
        else:
            url2 = srcs[selected]
            xbmc.Player().play(url2)
    def ghettotube(self, url):
        c = client.request(url)
        pattern = r'''video_url:\s+['"](.*?)['"]'''
        r = re.findall(pattern,c,flags=re.DOTALL)[0]
        xbmc.Player().play(r)
    def siska(self, url):
            c = client.request(url)
            
            pattern = r'''<iframe src=['"](.*?)['"]'''
            r = re.findall(pattern,c,flags=re.DOTALL)
            names = []
            srcs  = []
            found = 0
            for url in r:
                if not 'hqq.tv' in url:
                    if resolveurl.HostedMediaFile(url).valid_url():
                        found += 1
                        stream = ('Link %s' % found)
                        names.append(kodi.giveColor(stream,'white',True))
                        srcs.append(url)
            selected = kodi.dialog.select('Select a Quality.',names)
            if selected < 0:
                kodi.notify(msg='No option selected.')
                kodi.idle()
                quit()
            else:
                url2 = srcs[selected]
                u = resolveurl.HostedMediaFile(url2).resolve()
                xbmc.Player().play(u)
            
    def zzcartoon(self, url):
        headers = {'User-Agent' : 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'}
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        data = soup.find('div', class_={'player'})
        media_url = re.findall('''video_url:\s+['"](.*?)['"]''',str(data),flags=re.DOTALL)[0]
        xbmc.Player().play(media_url)
    def daftporn(self, url):
        headers = {'User-Agent' : 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'}
        link = requests.get(url,headers=headers).text
        soup = BeautifulSoup(link, 'html.parser')
        #dialog.ok("SOUP",str(soup))
        data = soup.find('div', class_={'newplayercontainer'})
        #dialog.ok("DATA",str(data))
        
    def fapality(self, url):
        c = client.request(url)
        soup = BeautifulSoup(c,'html.parser')
        r = soup.find_all('source', id=re.compile("video_source_[0-9]"))
        names = []
        srcs  = []
        for i in r:
            name = i['title']
            names.append(kodi.giveColor(name,'white',True))
            src = i['src']
            srcs.append(src)
        selected = kodi.dialog.select('Select a Quality.',names)
        if selected < 0:
            kodi.notify(msg='No option selected.')
            kodi.idle()
            quit()
        else:
            url2 = srcs[selected]
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'Referer' : url}
            link = requests.get(url2,headers=headers, stream=True)
            xbmc.Player().play(link.url)
    def watchpornfree(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'Referer' : url}
        #dialog.notification('XXX-O-DUS', '[COLOR yellow]Getting Links Now[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
        r = requests.get(url, headers=headers).text
        soup = BeautifulSoup(r,'html.parser')
        r = soup.find('div', id={'pettabs'})
        #r = re.findall('<div id="pettabs">(.*?)</div>',r, flags=re.DOTALL)[0]
        pattern = r'''href=['"]([^'"]+)['"].+?>(.*?)<'''
        r = re.findall(pattern,str(r))
        names = []
        srcs  = []
        found = 0
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        for url,name in r:
            if 'drivevideo' in url: url = url.split('?link=')[1]
            if resolveurl.HostedMediaFile(url).valid_url():
                found += 1
                name = ("Link %s" % found)
                names.append(kodi.giveColor(name,'white',True))
                srcs.append(url)
        selected = kodi.dialog.select('Select a link.',names)
        if selected < 0:
            kodi.notify(msg='No option selected.')
            kodi.idle()
            quit()
        else:
            url2 = srcs[selected]
            try:
                u = resolveurl.HostedMediaFile(url2).resolve()
                xbmc.Player().play(u)
            except : dialog.notification('XXX-O-DUS', '[COLOR yellow]Resolver Couldn\'t Resolve Link, Try Another[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
    def xxxdan(self, url):
        try:
            Headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36' }
            pattern = r'''sources.+?src:['"]([^'"]+)['"]'''
            link = requests.get(url,headers=Headers).text
            source = re.findall(pattern,link,flags=re.DOTALL)[0]
            xbmc.Player ().play(source)
        except: dialog.notification('XXX-O-DUS', '[COLOR yellow]Performer Is Offline[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
    def xvideos(self, url):
        try:
            Headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36' }
            pattern = r'''['"]([^'"]+m3u8)['"]'''
            link = requests.get(url,headers=Headers).text
            source = re.findall(pattern,link,flags=re.DOTALL)[0]
            xbmc.Player ().play(source)
        except: dialog.notification('XXX-O-DUS', '[COLOR yellow]Couldn\'t resolve Link[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
    
    def motherless(self, url):
        try:
            Headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36' }
            pattern = r'''__fileurl = ['"]([^'"]+)['"]'''
            link = requests.get(url,headers=Headers).text
            source = re.findall(pattern,link,flags=re.DOTALL)[0]
            source = source+'|verifypeer=false'
            xbmc.Player ().play(source)
        except: dialog.notification('XXX-O-DUS', '[COLOR yellow]Performer Is Offline[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
    def xnxx(self, url):
        try:
            Headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36' }
            pattern = r'''setVideoHLS.*?['"](.*?.m3u8)['"]'''
            link = requests.get(url,headers=Headers).text
            source = re.findall(pattern,link,flags=re.DOTALL)[0]
            xbmc.Player ().play(source)
        except: dialog.notification('XXX-O-DUS', '[COLOR yellow]Video Is Offline[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
    
    def adult_tv(self, url):
        try:
            headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36' }
            pattern = r'''file:['"](.*?)['"]'''
            base_domain = 'https://adult-tv-channels.com'
            link = requests.get(url,headers=headers).text
            soup = BeautifulSoup(link,'html.parser')
            iframe = soup.find('iframe')['src']
            if not base_domain in iframe: iframe = base_domain+iframe
            headers2 = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
                       'Referer' : url}
            link2 = requests.get(iframe,headers=headers2).text
            source = re.findall(pattern,link2,flags=re.DOTALL)[0]
            xbmc.Player ().play(source)
        except: dialog.notification('XXX-O-DUS', '[COLOR yellow]Video Is Offline[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
    
    def redtube(self, url):
        try:
            Headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36' }
            pattern = r'''videoUrl['"]:['"]([^"]+)['"]'''
            link = requests.get(url,headers=Headers).text
            source = re.findall(pattern,link,flags=re.DOTALL)[0].replace('\\','')
            source = 'https://www.redtube.com'+source
            link = requests.get(source,headers=Headers).json()
            names = []
            srcs  = []
            for i in link:
                qual = i['quality']
                url = i['videoUrl']
                names.append(kodi.giveColor(qual,'white',True))
                srcs.append(url)
            selected = kodi.dialog.select('Select a link.',names)
            if selected < 0:
                kodi.notify(msg='No option selected.')
                kodi.idle()
                quit()
            else:
                url2 = srcs[selected]
                xbmc.Player().play(url2)
        except: dialog.notification('XXX-O-DUS', '[COLOR yellow]Resolver Couldn\'t Resolve Link, Try Another[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
        
    def youjizz(self, url):
        try:
            Headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36' }
            pattern = r'''quality['"]:['"](.*?)['"].*?name['"]:['"](.*?)['"]'''
            link = requests.get(url,headers=Headers).text
            soup = BeautifulSoup(link,'html.parser')
            r = soup.find('div', id={'content'})
            stuff = re.findall(pattern,str(r))
            names = []
            srcs  = []
            for qual,vid in stuff:
                names.append(kodi.giveColor(qual,'white',True))
                vid = vid.replace('\\','')
                if not 'http' in vid: vid = 'https:'+vid
                srcs.append(vid)
            selected = kodi.dialog.select('Select a link.',names)
            if selected < 0:
                kodi.notify(msg='No option selected.')
                kodi.idle()
                quit()
            else:
                url2 = srcs[selected]
                xbmc.Player().play(url2)
        except: dialog.notification('XXX-O-DUS', '[COLOR yellow]Resolver Couldn\'t Resolve Link, Try Another[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
