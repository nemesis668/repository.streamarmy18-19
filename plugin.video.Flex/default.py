#############################################################
#################### START ADDON IMPORTS ####################
import xbmc
import xbmcgui
import xbmcplugin
import time
import os
import Login
import sys

#import pyxbmct.addonwindow as pyxbmct
from addon.common.addon import Addon

dp = xbmcgui.DialogProgress()
dialog = xbmcgui.Dialog()
_addon_id_ = 'plugin.video.Flex'
UsersXml		= xbmc.translatePath(os.path.join('special://home/userdata/addon_data/' + _addon_id_, 'users.xml'))
MoviesXml		= xbmc.translatePath(os.path.join('special://home/userdata/addon_data/' + _addon_id_, 'movies.xml'))
ShowsXml		= xbmc.translatePath(os.path.join('special://home/userdata/addon_data/' + _addon_id_, 'shows.xml'))
addontemp		= xbmc.translatePath(os.path.join('special://home/userdata/addon_data/' + _addon_id_))
#IntroVideo		= xbmc.translatePath(os.path.join('special://home/addons/' + _addon_id_, 'FlexIntro.mp4'))
if not os.path.exists(addontemp):
	os.makedirs(addontemp)
if not os.path.exists(UsersXml):
	open(UsersXml, 'a').close()


#############################################################
#################### SET ADDON ID ###########################
#_self_  = xbmcaddon.Addon(id=_addon_id_)
#addon   = Addon(_addon_id_, sys.argv)

#xbmc.Player ().play(IntroVideo)
#time.sleep(10)
#xbmc.Player().stop()
Login.MainWindow()

quit()





