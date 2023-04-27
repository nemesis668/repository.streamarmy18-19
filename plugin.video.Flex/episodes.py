#############################################################
#################### START ADDON IMPORTS ####################
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import os
import re
import sys
import requests
import json
import base64
import viewer
import time
import resolveurl
from datetime import datetime
import pyxbmct

dialog = xbmcgui.Dialog()
dp = xbmcgui.DialogProgress()
#############################################################
#################### SET ADDON ID ###########################
_addon_id_  = 'plugin.video.Flex'
_self_  = xbmcaddon.Addon(id=_addon_id_)
AddonTitle = '[B][COLOR white]FLE[COLOR blue]X[/B][/COLOR]'
Addonicon  = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_, 'icon.png'))
icon  = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_, 'icon.png'))
fanarts = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_, 'fanart.jpg'))
#############################################################
#################### SET ADDON THEME DIRECTORY ##############
_theme_ = _self_.getSetting('Theme')
_images_    = '/resources/' + _theme_	
#############################################################
#################### SET ADDON THEME IMAGES #################
Listbg = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'listbg.png'))
Addon_Image = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ ,'icon.png'))
Background_Image    = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'searchblack.png'))
TMDBAPI = _self_.getSetting('tmdb')
if TMDBAPI == '': TMDBAPI	=	'5135334daa33251bc407e5f24cb1c6a5'
########## Function To Call That Starts The Window ##########
def listwindow(ShowName,SeasonsTitle,epiurl):
	global data
	global List
	global Season
	global ShowsName
	ShowsName = ShowName
	Season = SeasonsTitle
	data = epiurl
	window = list_window('flex')
	window.doModal()
	del window
def passed(self, title):
    constructurl = title.split('/season/')[0]
    newurl = ('%s?api_key=%s&append_to_response=external_ids'  % (constructurl,TMDBAPI))
    #dialog.ok("NEW",str(newurl))
    grabimdb = requests.get(newurl).json()
    #xbmc.log('TMDBURL :::'+str(newurl),level = xbmc.LOGINFO)
    imdb = grabimdb['external_ids']['imdb_id']
    global Item_Title
    global Item_Link
    global Item_Desc
    global Item_Icon
    global Item_Icon2
    global Poster
    global AddPoster
    global desc
    global AddTitle
    url = title
    Item_Title =  []
    Item_Link  =  []
    Item_Desc  =  []
    Item_Icon  =  []
    Item_Icon2  =  []
    #title = title.title()
    Item_Title.append('[B][COLOR deepskyblue]'+ Season+'[/B][/COLOR]')
    Item_Link.append('')
    Item_Desc.append('[B][COLOR deepskyblue]'+ Season+'[/B][/COLOR]')
    Item_Icon.append(Addon_Image)
    Item_Icon2.append(fanarts)
    self.List.addItem('[B][COLOR deepskyblue]'+ Season+'[/B][/COLOR]')
    self.textbox.setText('[B][COLOR deepskyblue]'+ Season+'[/B][/COLOR]')
    self.Show_Logo.setImage(Addon_Image)
    link = requests.get(url).json()
    data = link['episodes']
    #IMDBNO = link['imdb_id']
    #dialog.ok("IMDB",str(IMDBNO))
    imgpath = 'https://image.tmdb.org/t/p/original'
    g = datetime.now()
    for i in data:
        name = i['name']
        try: airdate = i['air_date']
        except KeyError: airdate = ''
        date = time.strptime(airdate, "%Y-%m-%d")
        currentdate = ("%s-%s-%s" % (g.year, g.month, g.day) )
        currentdate = time.strptime(currentdate, "%Y-%m-%d")
        seasonno = i['season_number']
        if len (str(seasonno)) == 1: seasonno = '0'+str(seasonno)
        seasonno = str(seasonno)
        epino = i['episode_number']
        if len (str(epino)) == 1: epino = '0'+str(epino)
        epino = str(epino)
        poster = i['still_path']
        try: airdate = i['air_date']
        except: airdate = 'TBC'
        airdate = ('First Aired : %s\n\n' %airdate)
        Poster= poster
        if not poster: icon = Addonicon
        else: icon = imgpath + poster
        AddPoster = str(icon)
        desc = i ['overview']
        if desc == '': desc = 'No Synophsis Available'
        desc =  airdate+desc
        if (currentdate < date): title = ('[COLOR deepskyblue][B]S%s E%s | %s[/B][/COLOR]' % (seasonno,epino,name))
        else: title = ('S%s E%s | %s' % (seasonno,epino,name))
        link = ('%s|%s||%s|||%s' % (ShowsName,seasonno,epino,imdb))
        desc = ('[B]%s[/B]' % desc)
        AddTitle = title
        Item_Title.append(title)
        Item_Desc.append(desc)
        Item_Icon.append(icon)
        Item_Icon2.append(fanarts)
        Item_Link.append(link)
        self.List.addItem(title)
def FindSources(self,name,year,IMDBNO,desc,imdb):
    self.List2.setVisible(True)
    self.List.setVisible(False)
    global Item_Title
    global Item_Link2
    global Item_Icon
    Item_Title =  []
    Item_Link2  =  []
    Item_Icon  =  []
    Media_Link =  []
    Media_Link2 =  []
    Item_Title.append('[B][COLOR deepskyblue]SOURCES FOR % s[/B][/COLOR]' % name)
    self.List2.addItem('[B][COLOR deepskyblue]SOURCES FOR % s[/B][/COLOR]' % name)
    Item_Link2.append('')
    sourceurl = ('https://torrentio.strem.fun/yts,eztv,rarbg,1337x,kickasstorrents,torrentgalaxy,magnetdl,horriblesubs,nyaasi,nyaapantsu/stream/series/%s:%s:%s.json' % (imdb,year,IMDBNO))
    #xbmc.log('sourceurl :::'+str(sourceurl),level = xbmc.LOGINFO)
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    headers = {'User-Agent': ua}
    link = requests.get(sourceurl,headers=headers).json()
    for data in link['streams']:
        quality = data['name'].replace('Torrentio','').strip()
        title = data['title'].strip().replace('\n','')
        new_title = title.encode("ascii", "ignore")
        updated_title = new_title.decode()
        hashfile = data['infoHash']
        self.List2.addItem('[B][COLOR deepskyblue]%s | %s[/B][/COLOR]' % (quality,updated_title))
        playconstruct = ('magnet:?xt=urn:btih:%s' % hashfile)
        Item_Link2.append(playconstruct)
    self.setFocus(self.List2)

def List_Selected(self,Media_Link):
    title = Media_Link.split('|')[0]
    season = Media_Link.split('|')[1]
    episode = Media_Link.split('||')[1]
    imdb = Media_Link.split('|||')[1]
    FindSources(self,title,season,episode,desc,imdb)
def List_Selected2(self,Media_Link2):
	Player(AddTitle, str(Media_Link2), AddPoster,desc)
def Player(name,url,iconimage,desc):
    try:
        dialog.notification(AddonTitle, '[COLOR yellow]Sourcing Your Media[/COLOR]', Addonicon, 2500)
        if resolveurl.HostedMediaFile(url).valid_url(): 
            stream_url = resolveurl.HostedMediaFile(url).resolve()
            liz = xbmcgui.ListItem(str(name))
            liz.setArt({"thumb": str(iconimage)})
            liz.setInfo('video', {'Plot': str(desc)})
            liz.setPath(stream_url)
            xbmc.Player ().play(stream_url, liz, False)
            quit()
    except Exception as c:
            dialog.notification(AddonTitle,"[B][COLOR yellow]ERROR %s[/B][/COLOR]" % c,Addonicon,5000)
#############################################################
######### Class Containing the GUi Code / Controls ##########
class list_window(pyxbmct.AddonFullWindow):
	xbmc.executebuiltin("Dialog.Close(busydialog)")
	def __init__(self, title='Flex'):
		super(list_window, self).__init__(title)
		self.setGeometry(1280, 720, 100, 50)
		Background  = pyxbmct.Image(Background_Image)
		self.placeControl(Background, -10, -1, 123, 52)
		self.set_info_controls()
		self.set_active_controls()
		self.set_navigation()
		self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
		self.connect(self.List, lambda:List_Selected(self,Media_Link))
		self.connect(self.List2, lambda:List_Selected2(self,Media_Link2))
		passed(self, data)
		self.setFocus(self.List)
	def set_info_controls(self):
		self.Hello = pyxbmct.Label('', textColor='0xFF00f72c', font='font60', alignment=pyxbmct.ALIGN_CENTER)
		self.placeControl(self.Hello, -4, 1, 1, 50)
		self.textbox = pyxbmct.TextBox(textColor='0xFFFFFFFF')
		self.placeControl(self.textbox, 60, 0, 45, 25)
		self.Show_Logo = pyxbmct.Image('')
		self.placeControl(self.Show_Logo, 14, 1, 40, 8)
		self.Show_Logo2 = pyxbmct.Image('')
		self.placeControl(self.Show_Logo2, 14, 12, 40, 19)
	def set_active_controls(self):
		self.List =	pyxbmct.List(buttonFocusTexture=Listbg,_space=12,_itemTextYOffset=-7,_itemTextXOffset=-1,textColor='0xFFFFFFFF')
		self.placeControl(self.List, 12, 33, 105, 16)
		self.List2 =	pyxbmct.List(buttonFocusTexture=Listbg,_space=12,_itemTextYOffset=-7,_itemTextXOffset=-1,textColor='0xFFFFFFFF')
		self.placeControl(self.List2, 12, 33, 105, 16)
		self.List2.setVisible(False)
		self.connectEventList(
			[pyxbmct.ACTION_MOVE_DOWN,
			 pyxbmct.ACTION_MOVE_UP,
			 pyxbmct.ACTION_MOUSE_WHEEL_DOWN,
			 pyxbmct.ACTION_MOUSE_WHEEL_UP,
			 pyxbmct.ACTION_MOUSE_MOVE],
			self.List_update)
	def set_navigation(self):
		pass
	def List_update(self):
		global Media_Title
		global Media_Link
		global Media_Link2
		global Media_Desc
		global Media_Icon
		global Media_Icon2
		try:
			if self.getFocus() == self.List:
				position = self.List.getSelectedPosition()
				Media_Title = Item_Title[position]
				Media_Link  = Item_Link[position]
				Media_Desc = Item_Desc[position]
				self.textbox.setText(Media_Desc)
				self.textbox.autoScroll(1000, 1000, 1000)
				if Item_Icon[position] is not None:
					Media_Icon = Item_Icon[position]
					self.Show_Logo.setImage(Media_Icon)
				else:
					Media_Icon = 'http://via.placeholder.com/300x220/13b7ff/FFFFFF?text=' + Media_Title
					self.Show_Logo.setImage(Media_Icon)
				if Item_Icon2[position] is not None:
					Media_Icon2 = Item_Icon2[position]
					self.Show_Logo2.setImage(Media_Icon2)
				else:
					Media_Icon = 'http://via.placeholder.com/300x220/13b7ff/FFFFFF?text=' + Media_Title
					self.Show_Logo2.setImage(Media_Icon)
		except (RuntimeError, SystemError):
			pass
		try:
			if self.getFocus() == self.List2:
				position = self.List2.getSelectedPosition()
				Media_Link2  = Item_Link2[position]
		except (RuntimeError, SystemError):
			pass