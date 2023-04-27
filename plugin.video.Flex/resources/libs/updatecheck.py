import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import sys

import os
import re
import requests
from common_addon import Addon
dialog = xbmcgui.Dialog()
AddonTitle = '[COLOR red][B]E[COLOR yellow]nterTain Me[/B][/COLOR]'
addon_id            = 'plugin.video.EntertainMe'
addon               = Addon(addon_id, sys.argv)
selfAddon           = xbmcaddon.Addon(id=addon_id)
def checkupdates():
	curentpin = selfAddon.getSetting('pin')
	if 'Expired' in curentpin:
		dialog.ok(AddonTitle,"[B][COLOR white]Pairing is Required For This Addon, We Don't Have Any Annoying Pop Up Ads, So Please Visit [COLOR yellow]http://aiopin.world[COLOR white] To Get A Pin Code,[COLOR yellow] Your Pin Will Be Valid For 24 Hours[COLOR white] Click Ok To Enter Pin[/B][/COLOR]")
		string =''
		keyboard = xbmc.Keyboard(string, '[B][COLOR yellow]Please Enter Pin Generated From Website[/B][/COLOR]')
		keyboard.doModal()
		if keyboard.isConfirmed():
			string = keyboard.getText()
			if len(string)>1:
				term = string.title()
				selfAddon.setSetting(id='pin', value=term)
			else: quit()
		else: quit()
	curentpin = selfAddon.getSetting('pin')
	pinurlcheck = ('http://aiopin.world/service.php?code=%s&plugin=NemesisAio' % curentpin)
	link = requests.get(pinurlcheck).content
	if len(link) > 5:
		pass
	else:
		selfAddon.setSetting(id='pin', value='Expired')
		checkupdates()