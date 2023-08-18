import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs, os, requests, re, time
import sqlite3
_addon_id_	= 'plugin.video.cwm'
MainTextColour = 'gold'
AddonTitle = ('[COLOR %s][B]Cum With Me[/B][/COLOR]' % MainTextColour)
dialog = xbmcgui.Dialog()
_self_		= xbmcaddon.Addon(id=_addon_id_)
get_setting = _self_.getSetting
translatePath = xbmcvfs.translatePath
databases = translatePath(os.path.join('special://profile/addon_data/plugin.video.cwm', 'databases'))
cwmdb = translatePath(os.path.join(databases, 'cwm.db'))
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'}
AddonIcon		= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_, 'Icon.png'))
if ( not os.path.exists(databases)): os.makedirs(databases)
conn = sqlite3.connect(cwmdb)
c = conn.cursor()
try:
    c.executescript("CREATE TABLE IF NOT EXISTS chaturbate (name, url, image);")
except:
    pass
conn.close()

Checked = []
CheckMonitor = get_setting('Monitor')
i = 0
if CheckMonitor == 'false': quit()
while not xbmc.Monitor().abortRequested():
    if i <= 500:
        conn = sqlite3.connect(cwmdb)
        conn.text_factory = str
        c = conn.cursor()
        c.execute("SELECT * FROM chaturbate")
        e = [u for u in c.fetchall()]
        conn.close()
        if len(e) < 1:
            dialog.notification(AddonTitle, '[COLOR pink]No Performers Added To Favs, Monitor is on though![/COLOR]',AddonIcon, 2500)
            quit()
        else:
            for (name,url,image) in e:
                if name not in Checked:
                    pattern = r'''hls_source.+(http.*?m3u8)'''
                    link = requests.get(url,headers=headers).text
                    source = re.findall(pattern,link,flags=re.DOTALL)
                    if source:
                        dialog.notification(AddonTitle, '[COLOR pink]Performer %s is now Online[/COLOR]' % name, image, 2500)
                        Checked.append(name)
                        xbmc.sleep(5000)
                    else: pass
    if i >= 11:
        i = 0
        Checked = []
    i += 1
    time.sleep(300)