#############################################################
#################### START ADDON IMPORTS ####################
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import os
import re
import requests
import sys
import base64
import json
import time
import datetime
import viewer
import Movies
import SearchTMDB
import pyxbmct

dialog = xbmcgui.Dialog()
#############################################################
#################### SET ADDON ID ###########################
_addon_id_ = 'plugin.video.Flex'
_self_ = xbmcaddon.Addon(id=_addon_id_)
AddonTitle = '[B][COLOR white]FLE[COLOR blue]X[/B][/COLOR]'
dp = xbmcgui.DialogProgress()
icon  = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_, 'icon.png'))
MoviesXml		= xbmcvfs.translatePath(os.path.join('special://home/userdata/addon_data/' + _addon_id_, '%smovies.xml'))
ShowsXml		= xbmcvfs.translatePath(os.path.join('special://home/userdata/addon_data/' + _addon_id_, '%sshows.xml'))
TMDBAPI = _self_.getSetting('tmdb')
if TMDBAPI == '': TMDBAPI	=	'5135334daa33251bc407e5f24cb1c6a5'
# if not os.path.exists(MoviesXml):
	# open(MoviesXml, 'a').close()
# if not os.path.exists(ShowsXml):
	# open(ShowsXml, 'a').close()
#############################################################
#################### SET ADDON THEME DIRECTORY ##############
_theme_			= _self_.getSetting('Theme')
_images_		= '/resources/' + _theme_	
#############################################################
#################### SET ADDON THEME IMAGES #################
Background_Image	= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'background.png'))
Movies_Button		= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'MoviesB.png'))
Movies_ButtonS		= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'MoviesBS.png'))
TvShows_Button		= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'TvShowsB.png'))
TvShows_ButtonS		= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'TvShowsBS.png'))
AddMovie_Button		= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'AddMovieB.png'))
AddMovie_ButtonS	= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'AddMovieBS.png'))
AddShow_Button		= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'AddShowB.png'))
AddShow_ButtonS		= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'AddShowBS.png'))
Settings_Button		= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'SettingsB.png'))
Settings_ButtonS	= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'SettingsBS.png'))
Quit_Button		= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'QuitB.png'))
Quit_ButtonS	= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'QuitBS.png'))
NoMedia = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'NoVideo.png'))
### FRAMES
Frame1				= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'Frame.png'))
Frame1S				= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'FrameS.png'))
global MovieID
global Movie1
global Movie2
global Movie3
global Movie4
global Movie5
global Movie6
global Movie7
global Movie8
global Movie9
global Movie10
global Movie11
global Movie12
def PopMovies(self):
	logos = []
	movietitles = []
	movieids = []
	global Poster1
	global Poster2
	global Poster3
	global Poster4
	global Poster5
	global Poster6
	global Poster7
	global Poster8
	global Poster9
	global Poster10
	global Poster11
	global Poster12
	global Poster13
	global Poster14
	global Poster15
	global UserTitle
	global ID1
	global ID2
	global ID3
	global ID4
	global ID5
	global ID6
	global ID7
	global ID8
	global ID9
	global ID10
	global ID11
	global ID12
	global ID13
	global ID14
	global ID15
	with open(ShowsXml % User) as F:
		for cnt, line in enumerate(F):
				try:
					title = line.split('|')[0]
					movietitles.append(title)
					Poster = line.split('|')[1]
					logos.append(Poster)
					MovieID = line.split('|')[2]
					movieids.append(MovieID)
				except: pass
	try: Poster1 = logos[0]
	except: Poster1 = NoMedia
	try: Poster2 = logos[1]
	except: Poster2 = NoMedia
	try: ID1 = movieids[0]
	except: pass
	try: ID2 = movieids[1]
	except: pass
	try: Poster3 = logos[2]
	except: Poster3 = NoMedia
	try: ID3 = movieids[2]
	except: pass
	try: Poster4 = logos[3]
	except: Poster4 = NoMedia
	try: ID4 = movieids[3]
	except: pass
	try: Poster5 = logos[4]
	except: Poster5 = NoMedia
	try: ID5 = movieids[4]
	except: pass
	try: Poster6 = logos[5]
	except: Poster6 = NoMedia
	try: ID6 = movieids[5]
	except: pass
	try: Poster7 = logos[6]
	except: Poster7 = NoMedia
	try: ID7 = movieids[6]
	except: pass
	try: Poster8 = logos[7]
	except: Poster8 = NoMedia
	try: ID8 = movieids[7]
	except: pass
	try: Poster9 = logos[8]
	except: Poster9 = NoMedia
	try: ID9 = movieids[8]
	except: pass
	try: Poster10 = logos[9]
	except: Poster10 = NoMedia
	try: ID10 = movieids[9]
	except: pass
	try: Poster11 = logos[10]
	except: Poster11 = NoMedia
	try: ID11 = movieids[10]
	except: pass
	try: Poster12 = logos[11]
	except: Poster12 = NoMedia
	try: ID12 = movieids[11]
	except: pass
	try: Poster13 = logos[12]
	except: Poster13 = NoMedia
	try: ID13 = movieids[12]
	except: pass
	try: Poster14 = logos[13]
	except: Poster14 = NoMedia
	try: ID14 = movieids[13]
	except: pass
	try: Poster15 = logos[14]
	except: Poster15 = NoMedia
	try: ID15 = movieids[14]
	except: pass
	UserTitle = pyxbmct.Label(User + '\'S SHOWS ',textColor='0xFF02bcf5',font='font60',alignment=pyxbmct.ALIGN_CENTER)
#############################################################
########## Function To Call That Starts The Window ##########
def MainWindow(user):
	global User
	User = user
	window = Main('Flex')
	window.doModal()
	del window
def tick(self):
	Date = time.strftime("[B]%A\n%d/%m/%y - %H:%M[/B]")
	self.DATE.setLabel(str(Date))
def killaddon(self):
	self.close()
	xbmc.executebuiltin("Container.Update(path,replace)")
	xbmc.executebuiltin("ActivateWindow(Home)")
def openviewer(self,MovieID,User):
	viewer.MainWindow(self,'TV|'+MovieID,User)
	self.close()
def MoviesWin(self,User):
	Movies.MainWindow(User)
	self.close()
def SearchMovie(self,User):
	section=['[COLOR red][B]Search Movie[/B][/COLOR]','[COLOR white][B]Top Movies[/B][/COLOR]','[COLOR white][B]Cinema Movies[/B][/COLOR]','[COLOR white][B]People Watching[/B][/COLOR]']
	links=['SEARCH','TOP','CINEMA','WATCHING']
	select = dialog.select('[B][COLOR red]W[COLOR white]hat Would You Like To Do?[/COLOR][/B]',section)
	if select < 0:quit()
	url = links[select]
	if 'SEARCH' in url:
		string =''
		keyboard = xbmc.Keyboard(string, '[COLOR white][B]Search Which Movie?[/B][/COLOR]')
		keyboard.doModal()
		if keyboard.isConfirmed():
			string = keyboard.getText()
			if len(string)>1:
				term = string.lower()
		else: quit ()
		url = 'https://api.themoviedb.org/3/search/movie?api_key=' + TMDBAPI + '&query=' + term
		SearchTMDB.listwindow('MOVIE|'+url,User)
		self.close()
	elif 'TOP' in url:
		url = 'https://api.themoviedb.org/3/movie/popular?api_key=' + TMDBAPI + '&language=en-US&page=1'
		SearchTMDB.listwindow('MOVIE|'+url,User)
		self.close()
	elif 'CINEMA' in url:
		url = 'https://api.themoviedb.org/3/discover/movie?api_key=' + TMDBAPI + '&with_release_type=2|3&region=US'
		SearchTMDB.listwindow('MOVIE|'+url,User)
		self.close()
	elif 'WATCHING' in url:
		url = 'https://api.themoviedb.org/3/movie/now_playing?api_key=' + TMDBAPI + '&language=en-US&page=1'
		SearchTMDB.listwindow('MOVIE|'+url,User)
		self.close()
def SearchTV(self,User):
	section=['[COLOR red][B]Search Tv Show[/B][/COLOR]','[COLOR white][B]Top Tv Shows[/B][/COLOR]','[COLOR white][B]Shows Airing Today[/B][/COLOR]']
	links=['SEARCH','TVTOP','AIRING']
	select = dialog.select('[B][COLOR red]W[COLOR white]hat Would You Like To Do?[/COLOR][/B]',section)
	if select < 0:quit()
	url = links[select]
	if 'SEARCH' in url:
		string =''
		keyboard = xbmc.Keyboard(string, '[COLOR white][B]Search Which Tv Show?[/B][/COLOR]')
		keyboard.doModal()
		if keyboard.isConfirmed():
			string = keyboard.getText()
			if len(string)>1:
				term = string.lower()
		else: quit ()
		url = 'https://api.themoviedb.org/3/search/tv?api_key=' + TMDBAPI + '&query=' + term
		SearchTMDB.listwindow('TV|'+url,User)
		self.close()
	elif 'TVTOP' in url:
		url = 'https://api.themoviedb.org/3/tv/popular?api_key=' + TMDBAPI + '&language=en-US&page=1'
		SearchTMDB.listwindow('TV|'+url,User)
		self.close()
	elif 'AIRING' in url:
		url = 'https://api.themoviedb.org/3/tv/airing_today?api_key=' + TMDBAPI + '&language=en-US&page=1'
		SearchTMDB.listwindow('TV|'+url,User)
		self.close()
#############################################################
######### Class Containing the GUi Code / Controls ##########
class Main(pyxbmct.AddonFullWindow):
	xbmc.executebuiltin("Dialog.Close(busydialog)")
	def __init__(self, title='Flex'):
		super(Main, self).__init__(title)
		self.setGeometry(1280, 720, 100, 50)
		Background  = pyxbmct.Image(Background_Image)
		PopMovies(self)
		# T , L , H , W
		Movie1 = pyxbmct.Image(Poster1)
		Movie2 = pyxbmct.Image(Poster2)
		Movie3 = pyxbmct.Image(Poster3) # Button 13
		Movie4 = pyxbmct.Image(Poster4)
		Movie5 = pyxbmct.Image(Poster5)
		Movie6 = pyxbmct.Image(Poster6)
		Movie7 = pyxbmct.Image(Poster7)
		Movie8 = pyxbmct.Image(Poster8)
		Movie9 = pyxbmct.Image(Poster9)
		Movie10 = pyxbmct.Image(Poster10)
		Movie11 = pyxbmct.Image(Poster11)
		Movie12 = pyxbmct.Image(Poster12)
		Movie13 = pyxbmct.Image(Poster13)
		Movie14 = pyxbmct.Image(Poster14)
		Movie15 = pyxbmct.Image(Poster15)
		self.placeControl(Background, -10, -1, 123, 52)
		self.placeControl(Movie1, 15, 11, 26, 5) # Button 7
		self.placeControl(Movie2, 15, 19, 26, 5) # Button 10
		self.placeControl(Movie3, 15, 27, 26, 5) # Button 13
		self.placeControl(Movie4, 15, 35, 26, 5) # Button 16
		self.placeControl(Movie5, 15, 43, 26, 5) # Button 8
		self.placeControl(Movie6, 45, 11, 26, 5) # Button 11
		self.placeControl(Movie7, 45, 19, 26, 5) # Button 14
		self.placeControl(Movie8, 45, 27, 26, 5) # Button 17
		self.placeControl(Movie9, 45, 35, 26, 5) # Button 9
		self.placeControl(Movie10, 45, 43, 26, 5) # Button 12
		self.placeControl(Movie11, 75, 11, 26, 5) # Button 15
		self.placeControl(Movie12, 75, 19, 26, 5) # Button 18
		self.placeControl(Movie13, 75, 27, 26, 5) # Button 19
		self.placeControl(Movie14, 75, 35, 26, 5) # Button 20
		self.placeControl(Movie15, 75, 43, 26, 5) # Button 21
		self.placeControl(UserTitle, 85, 20, 40, 20)
		self.set_info_controls()
		self.set_active_controls()
		self.set_navigation()
		self.connect(pyxbmct.ACTION_NAV_BACK, lambda:killaddon(self))
		tick(self)
		self.connect(self.button1, lambda:MoviesWin(self,User))
		self.connect(self.button3, lambda:SearchMovie(self,User))
		self.connect(self.button4, lambda:SearchTV(self,User))
		self.connect(self.button5, lambda:_self_.openSettings())
		self.connect(self.button6, lambda:killaddon(self))
		self.connect(self.button7, lambda:openviewer(self,ID1,User))
		self.connect(self.button8, lambda:openviewer(self,ID6,User))
		self.connect(self.button9, lambda:openviewer(self,ID11,User))
		self.connect(self.button10, lambda:openviewer(self,ID2,User))
		self.connect(self.button11, lambda:openviewer(self,ID7,User))
		self.connect(self.button12, lambda:openviewer(self,ID12,User))
		self.connect(self.button13, lambda:openviewer(self,ID3,User))
		self.connect(self.button14, lambda:openviewer(self,ID8,User))
		self.connect(self.button15, lambda:openviewer(self,ID13,User))
		self.connect(self.button16, lambda:openviewer(self,ID4,User))
		self.connect(self.button17, lambda:openviewer(self,ID9,User))
		self.connect(self.button18, lambda:openviewer(self,ID14,User))
		self.connect(self.button19, lambda:openviewer(self,ID5,User))
		self.connect(self.button20, lambda:openviewer(self,ID10,User))
		self.connect(self.button21, lambda:openviewer(self,ID15,User))
		self.setFocus(self.button2)
	def set_info_controls(self):
		self.Hello = pyxbmct.Label('', textColor='0xFFF44248', font='font60', alignment=pyxbmct.ALIGN_CENTER)
		self.DATE =  pyxbmct.Label('',textColor='0xFFFFFFFF', font='font60')
		self.placeControl(self.Hello, -4, 1, 1, 50)
		self.placeControl(self.DATE,  -11, 37, 12, 24)
	def set_active_controls(self):
		self.button1 = pyxbmct.Button('',   focusTexture=Movies_ButtonS,   noFocusTexture=Movies_Button)
		self.placeControl(self.button1, 20, 0,  10, 9)
		self.button2 = pyxbmct.Button('',   focusTexture=TvShows_ButtonS,   noFocusTexture=TvShows_Button)
		self.placeControl(self.button2, 35, 0,  10, 9)
		self.button3 = pyxbmct.Button('',   focusTexture=AddMovie_ButtonS,   noFocusTexture=AddMovie_Button)
		self.placeControl(self.button3, 50, 0,  10, 9)
		self.button4 = pyxbmct.Button('',   focusTexture=AddShow_ButtonS,   noFocusTexture=AddShow_Button)
		self.placeControl(self.button4, 65, 0,  10, 9)
		self.button5 = pyxbmct.Button('',   focusTexture=Settings_ButtonS,   noFocusTexture=Settings_Button)
		self.placeControl(self.button5, 80, 0,  10, 9)
		self.button6 = pyxbmct.Button('',   focusTexture=Quit_ButtonS,   noFocusTexture=Quit_Button)
		self.placeControl(self.button6, 93, 0,  10, 9)
		self.button7 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
		self.placeControl(self.button7, 13, 10, 30, 7)
		self.button8 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
		self.placeControl(self.button8, 43, 10, 30, 7)
		self.button9 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
		self.placeControl(self.button9, 73, 10, 30, 7)
		self.button10 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
		self.placeControl(self.button10, 13, 18, 30, 7)
		self.button11 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
		self.placeControl(self.button11, 43, 18, 30, 7)
		self.button12 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
		self.placeControl(self.button12, 73, 18, 30, 7)
		self.button13 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
		self.placeControl(self.button13, 13, 26, 30, 7)
		self.button14 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
		self.placeControl(self.button14, 43, 26, 30, 7)
		self.button15 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
		self.placeControl(self.button15, 73, 26, 30, 7)
		self.button16 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
		self.placeControl(self.button16, 13, 34, 30, 7)
		self.button17 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
		self.placeControl(self.button17, 43, 34, 30, 7)
		self.button18 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
		self.placeControl(self.button18, 73, 34, 30, 7)
		self.button19 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
		self.placeControl(self.button19, 13, 42, 30, 7)
		self.button20 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
		self.placeControl(self.button20, 43, 42, 30, 7)
		self.button21 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
		self.placeControl(self.button21, 73, 42, 30, 7)
		self.connectEventList(
			[pyxbmct.ACTION_MOVE_DOWN,
			pyxbmct.ACTION_MOVE_UP,
			pyxbmct.ACTION_MOUSE_WHEEL_DOWN,
			pyxbmct.ACTION_MOUSE_WHEEL_UP,
			pyxbmct.ACTION_MOUSE_MOVE],
			self.Multi_Update)

	def set_navigation(self):
		self.button1.controlUp(self.button6)
		self.button2.controlUp(self.button1)
		self.button3.controlUp(self.button2)
		self.button4.controlUp(self.button3)
		self.button5.controlUp(self.button4)
		self.button6.controlUp(self.button5)
		self.button7.controlUp(self.button9)
		self.button8.controlUp(self.button7)
		self.button9.controlUp(self.button8)
		self.button10.controlUp(self.button12)
		self.button11.controlUp(self.button10)
		self.button12.controlUp(self.button11)
		self.button13.controlUp(self.button15)
		self.button14.controlUp(self.button13)
		self.button15.controlUp(self.button14)
		self.button16.controlUp(self.button18)
		self.button17.controlUp(self.button16)
		self.button18.controlUp(self.button17)
		self.button19.controlUp(self.button21)
		self.button20.controlUp(self.button19)
		self.button21.controlUp(self.button20)
		self.button1.controlDown(self.button2)
		self.button2.controlDown(self.button3)
		self.button3.controlDown(self.button4)
		self.button4.controlDown(self.button5)
		self.button5.controlDown(self.button6)
		self.button6.controlDown(self.button1)
		self.button7.controlDown(self.button8)
		self.button8.controlDown(self.button9)
		self.button9.controlDown(self.button7)
		self.button10.controlDown(self.button11)
		self.button11.controlDown(self.button12)
		self.button12.controlDown(self.button10)
		self.button13.controlDown(self.button14)
		self.button14.controlDown(self.button15)
		self.button15.controlDown(self.button13)
		self.button16.controlDown(self.button17)
		self.button17.controlDown(self.button18)
		self.button18.controlDown(self.button16)
		self.button19.controlDown(self.button20)
		self.button20.controlDown(self.button21)
		self.button21.controlDown(self.button19)
		self.button7.controlLeft(self.button1)
		self.button8.controlLeft(self.button1)
		self.button9.controlLeft(self.button1)
		self.button10.controlLeft(self.button7)
		self.button11.controlLeft(self.button8)
		self.button12.controlLeft(self.button9)
		self.button13.controlLeft(self.button10)
		self.button14.controlLeft(self.button11)
		self.button15.controlLeft(self.button12)
		self.button16.controlLeft(self.button13)
		self.button17.controlLeft(self.button14)
		self.button18.controlLeft(self.button15)
		self.button19.controlLeft(self.button16)
		self.button20.controlLeft(self.button17)
		self.button21.controlLeft(self.button18)
		self.button7.controlRight(self.button10)
		self.button8.controlRight(self.button11)
		self.button9.controlRight(self.button12)
		self.button10.controlRight(self.button13)
		self.button11.controlRight(self.button14)
		self.button12.controlRight(self.button15)
		self.button13.controlRight(self.button16)
		self.button14.controlRight(self.button17)
		self.button15.controlRight(self.button18)
		self.button16.controlRight(self.button19)
		self.button19.controlRight(self.button7)
		self.button17.controlRight(self.button20)
		self.button20.controlRight(self.button8)
		self.button18.controlRight(self.button21)
		self.button19.controlRight(self.button7)
		self.button21.controlRight(self.button9)
		self.button1.controlRight(self.button7)
		self.button2.controlRight(self.button7)
		self.button3.controlRight(self.button7)
		self.button4.controlRight(self.button7)
		self.button5.controlRight(self.button7)
		self.button6.controlRight(self.button7)
	def Multi_Update(self):
		tick(self)
	def setAnimation(self, control):
		control.setAnimations([('WindowOpen', 'effect=slide start=2000 end=0 time=1000',),
								('WindowClose', 'effect=slide start=100 end=1400 time=500',)])