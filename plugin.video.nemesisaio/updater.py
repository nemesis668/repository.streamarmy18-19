import requests
import hashlib
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
from six import PY2
import time
import os
translatePath = xbmc.translatePath if PY2 else xbmcvfs.translatePath
addon_id            = 'plugin.video.nemesisaio'
AddonTitle          = '[COLOR yellow][B]NemesisAio[/B][/COLOR]'
Addonicon           = translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.gif'))
dialog              = xbmcgui.Dialog()
def ScraperCheck(check):
	file1 = translatePath(os.path.join('special://home/addons/plugin.video.nemesisaio', 'resources/scrapers/%s' % check.lower()))
	file1check = open(file1).read()
	file2 = requests.get('https://raw.githubusercontent.com/nemesis668/repository.streamarmy/master/plugin.video.nemesisaio/resources/scrapers/%s' % check).content
	check1 = hashlib.md5(file1check).hexdigest()
	check2 = hashlib.md5(file2).hexdigest()
	if check1 == check2:
		pass
	else:
		with open (file1, 'w') as F:
			F.write(file2)
			dialog.notification(AddonTitle, '[COLOR yellow]Updated %s Scraper[/COLOR]' %check, Addonicon, 2500)
			time.sleep(1)
			