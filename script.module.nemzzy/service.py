import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
import  re, os, time
import requests 
translatePath = xbmcvfs.translatePath
dialog = xbmcgui.Dialog()
addon_id = 'script.module.nemzzy'
icon = xbmcvfs.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
addon = xbmcaddon.Addon()
dialog.notification("Nemzzy Service","RUNNING",icon,5000)
githubxml = 'https://raw.githubusercontent.com/nemesis668/repository.streamarmy18-19/main/addons.xml'
serviceapi = 'http://streamarmy.co.uk/service.php?system=%s&addons=%s'
pattern = r'''<addon\sid=['"](plugin.*?)['"]'''


releasedaddons = []

class Run:
    def platform():
        if xbmc.getCondVisibility('system.platform.android'):
            return 'Android'
        elif xbmc.getCondVisibility('system.platform.linux'):
            return 'Linux'
        elif xbmc.getCondVisibility('system.platform.tvos'):
            return 'TV OS'
        elif xbmc.getCondVisibility('system.platform.windows'):
            return 'Windows'
        elif xbmc.getCondVisibility('system.platform.osx'):
            return 'OSX'
        elif xbmc.getCondVisibility('system.platform.atv2'):
            return 'AppleTv'
        elif xbmc.getCondVisibility('system.platform.xbox'):
            return 'Xbox'
        elif xbmc.getCondVisibility('system.platform.ios'):
            return 'IOS'
        elif xbmc.getCondVisibility('system.platform.darwin'):
            return 'IOS'
        else:
            return 'Unknown Device'
    def Start():
        Version = Run.platform()
        installed = 0
        try:
            getcurrent = requests.get(githubxml).text
            findaddons = re.findall(pattern,getcurrent)
            for addonn in findaddons:
                releasedaddons.append(addonn)
        except:
            pass
        for checkadd in releasedaddons:
            addonpath = xbmcvfs.translatePath(os.path.join('special://home/addons/%s' % checkadd, 'addon.xml'))
            if os.path.exists(addonpath):
                installed += 1
                with open(addonpath, 'r') as reader:
                    patternv = r'''<addon\sid=['"]%s['"].*?version=['"](.*?)['"]''' % checkadd
                    getver = re.findall(patternv,reader.read(),flags=re.DOTALL)[0]
                    newpat = (r'''<addon\sid=['"]%s['"].*?version=['"]%s['"]''' % (checkadd,getver))
                    try:
                        checkver = re.findall(newpat,getcurrent,flags=re.DOTALL)[0]
                    except IndexError:
                        if 'nemesisaio' in checkadd: addonicon = xbmcvfs.translatePath(os.path.join('special://home/addons/%s' % checkadd, 'icon.gif'))
                        else: addonicon = xbmcvfs.translatePath(os.path.join('special://home/addons/%s' % checkadd, 'icon.png'))
                        xbmc.log(msg='ADDON OUT OF DATE ::: %s' % checkadd, level=xbmc.LOGINFO)
                        dialog.notification("Nemzzy Service","Addon %s Needs Updating" %checkadd.replace('plugin.video.','').title(),addonicon,5000)
                        xbmc.sleep(5000)
                reader.close()
            else:
                pass
        pingapi = requests.get(serviceapi % (Version,installed)).text
        dialog.notification("Nemzzy Service finished","Checked %s installed addons" % installed,icon,10000)
if __name__ == '__main__':
    Run.Start()
