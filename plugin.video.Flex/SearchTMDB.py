#############################################################
#################### START ADDON IMPORTS ####################
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import os
import re
import sys
import requests
import xbmcvfs
import json
import base64
import viewer
import pyxbmct

dialog = xbmcgui.Dialog()
#############################################################
#################### SET ADDON ID ###########################
_addon_id_  = 'plugin.video.Flex'
_self_  = xbmcaddon.Addon(id=_addon_id_)
icon  = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_, 'icon.png'))
fanarts = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_, 'fanart.jpg'))
#############################################################
#################### SET ADDON THEME DIRECTORY ##############
_theme_ = _self_.getSetting('Theme')
_images_    = '/resources/' + _theme_	
#############################################################
#################### SET ADDON THEME IMAGES #################
Listbg = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'listbg.png'))
Addon_Image = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'icon.png'))
Background_Image    = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'searchblack.png'))
########## Function To Call That Starts The Window ##########
def listwindow(Search,user):
	global data
	global List
	global User
	User = user
	data = Search
	window = list_window('flex')
	window.doModal()
	del window
def passed(self, title):
	url = title.split('|')[1]
	source = title.split('|')[0]
	global Item_Title
	global Item_Link
	global Item_Desc
	global Item_Icon
	global Item_Icon2
	Item_Title =  []
	Item_Link  =  []
	Item_Desc  =  []
	Item_Icon  =  []
	Item_Icon2  =  []
	title = title.title()
	Item_Title.append('Search Results Provided By TMDB')
	Item_Link.append('')
	Item_Desc.append('Search Results Provided By TMDB')
	Item_Icon.append(Addon_Image)
	Item_Icon2.append(Addon_Image)
	self.List.addItem('Search Results Provided By TMDB')
	self.textbox.setText('Search Results Provided By TMDB')
	self.Show_Logo.setImage(Addon_Image)
	data = requests.get(url).json()
	if 'MOVIE' in source:
		try:
			movies = data['results']
		except:
			dialog.notification(AddonTitle, '[COLOR red]End Of Results, Or TMDB Not Responding[/COLOR]', Addon_Image, 5000)
			quit()
		for info in movies:
				imgpath = 'https://image.tmdb.org/t/p/original'
				try: title = info['title']#.encode('utf-8')
				except KeyError: title = info['name']#.encode('utf-8')
				icon = info['poster_path']
				movieid = info['id']
				if not icon: icon = Addon_Image
				else: icon = imgpath + icon
				fanart = info['backdrop_path']
				if not fanart: fanart = fanarts
				else: fanart = imgpath + fanart
				text = info['overview']#.encode('utf-8')
				try: date = info['release_date'] ; date = date.split('-')[0]
				except KeyError: date =''
				movieid = str(movieid)
				if not text == '':
					text = ('[B]%s[/B]' % text)
					Item_Title.append(title)
					Item_Desc.append(text)
					Item_Icon.append(icon)
					Item_Icon2.append(fanart)
					Item_Link.append('Movie|'+movieid)
					self.List.addItem(title)
	else:
		try:
			movies = data['results']
		except:
			dialog.notification(AddonTitle, '[COLOR red]End Of Results, Or TMDB Not Responding[/COLOR]', Addon_Image, 5000)
			quit()
		for info in movies:
				imgpath = 'https://image.tmdb.org/t/p/original'
				try: title = info['title']#.encode('utf-8')
				except KeyError: title = info['name']#.encode('utf-8')
				icon = info['poster_path']
				movieid = info['id']
				if not icon: icon = Addon_Image
				else: icon = imgpath + icon
				fanart = info['backdrop_path']
				if not fanart: fanart = fanarts
				else: fanart = imgpath + fanart
				text = info['overview']#.encode('utf-8')
				try: date = info['release_date'] ; date = date.split('-')[0]
				except KeyError: date =''
				movieid = str(movieid)
				if not text == '':
					text = ('[B]%s[/B]' % text)
					Item_Title.append(title)
					Item_Desc.append(text)
					Item_Icon.append(icon)
					Item_Icon2.append(fanart)
					Item_Link.append('TV|'+movieid)
					self.List.addItem(title)
def List_Selected(self):
	#pass
	global Media_Link
	viewer.MainWindow(self,Media_Link,User)
	self.close()
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
		self.connect(self.List, lambda:List_Selected(self))
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