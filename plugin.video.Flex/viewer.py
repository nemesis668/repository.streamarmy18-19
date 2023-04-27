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
import resolveurl
import Movies
import Shows
import seasons
import pyxbmct

from datetime import datetime
dialog = xbmcgui.Dialog()
#############################################################
#################### SET ADDON ID ###########################
_addon_id_ = 'plugin.video.Flex'
_self_ = xbmcaddon.Addon(id=_addon_id_)
AddonTitle = '[B][COLOR white]FLE[COLOR blue]X[/B][/COLOR]'
dp = xbmcgui.DialogProgress()
icon  = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_, 'icon.png'))
Addonicon  = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_, 'icon.png'))
nextpage = ''
TMDBAPI = _self_.getSetting('tmdb')
if TMDBAPI == '': TMDBAPI	=	'5135334daa33251bc407e5f24cb1c6a5'
MoviesXml		= xbmcvfs.translatePath(os.path.join('special://home/userdata/addon_data/' + _addon_id_, '%smovies.xml'))
ShowsXml		= xbmcvfs.translatePath(os.path.join('special://home/userdata/addon_data/' + _addon_id_, '%sshows.xml'))
#############################################################
#################### SET ADDON THEME DIRECTORY ##############
_theme_			= _self_.getSetting('Theme')
_images_		= '/resources/' + _theme_	
#############################################################
#################### SET ADDON THEME IMAGES #################
Background_Image	= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'Viewerblack.png'))
AddMovie = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'addmovie.png'))
AddMovieS = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'addmovieS.png'))
AddShow = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'addshow.png'))
AddShowS = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'addshowS.png'))
DeleteMovie = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'deletemovie.png'))
DeleteMovieS = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'deletemovieS.png'))
DeleteShow = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'deleteshow.png'))
DeleteShowS = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'deleteshowS.png'))
ViewSeasons = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'viewseasons.png'))
ViewSeasonsS = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'viewseasonsS.png'))
FindLinks = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'findlinks.png'))
FindLinksS = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'findlinksS.png'))
Trailer = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'trailer.png'))
TrailerS = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'trailerS.png'))
Back = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'back.png'))
BackS = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'backS.png'))
Listbg = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'listbg.png'))
##############################################################
#############################GLOBALS##########################
global source
#############################################################
########## Function To Call That Starts The Window ##########
def MainWindow(type,movieid, user):
    global User
    User = user
    global source
    global Poster
    global MovieTitle
    global Release
    global desc
    global MovieRating
    global trailerkey
    global MovieLength
    global MovieID
    global AddTitle
    global AddPoster
    global MovieYear
    global IMDBNO
    global removeme
    source = movieid.split('|')[0]
    movieid = movieid.split('|')[1]
    if 'Movie' in source:
        MovieID = movieid
        url = ('https://api.themoviedb.org/3/movie/%s?api_key=%s&append_to_response=videos' % (movieid,TMDBAPI))
        link = requests.get(url).json()
        poster = link['poster_path']
        Poster = 'https://image.tmdb.org/t/p/original' + poster
        AddPoster = str(Poster)
        Poster = pyxbmct.Image(Poster)
        title = link['original_title']
        removeme = title
        IMDBNO = link['imdb_id']
        AddTitle = str(title)
        title = '[B]'+str(title)+'[/B]'
        MovieTitle = pyxbmct.Label(title,textColor='0xFFFFFFFF',font='font60',alignment=pyxbmct.ALIGN_LEFT)
        releasedate = link['release_date']
        MovieYear = releasedate.split('-')[0]
        dateformat = 'Released : ' + str(releasedate)
        Release = pyxbmct.Label(dateformat,textColor='0xFFFFFFFF',font='font24',alignment=pyxbmct.ALIGN_LEFT)
        desc = link['overview']
        rating = link['vote_average']
        try: trailerkey = link['videos']['results'][0]['key']
        except: trailerkey = 'No Trailer'
        rating = 'Rated : ' + str(rating) + ' / 10'
        MovieRating = pyxbmct.Label(rating,textColor='0xFFFFFFFF',font='font24',alignment=pyxbmct.ALIGN_LEFT)
        runtime = link['runtime']
        runtime = 'Movie Length : ' + str(runtime) + ' Mins'
        MovieLength = pyxbmct.Label(runtime,textColor='0xFFFFFFFF',font='font24',alignment=pyxbmct.ALIGN_LEFT)
        window = Main('Viewer')
        window.doModal()
        del window
    else:
        MovieID = movieid
        url = ('https://api.themoviedb.org/3/tv/%s?api_key=%s&append_to_response=videos' % (movieid,TMDBAPI))
        link = requests.get(url).json()
        poster = link['poster_path']
        Poster = 'https://image.tmdb.org/t/p/original' + poster
        AddPoster = str(Poster)
        Poster = pyxbmct.Image(Poster)
        title = link['original_name']
        removeme = title
        AddTitle = str(title)
        title = '[B]'+str(title)+'[/B]'
        MovieTitle = pyxbmct.Label(title,textColor='0xFFFFFFFF',font='font60',alignment=pyxbmct.ALIGN_LEFT)
        releasedate = link['first_air_date']
        MovieYear = releasedate.split('-')[0]
        dateformat = 'First Aired : ' + str(releasedate)
        Release = pyxbmct.Label(dateformat,textColor='0xFFFFFFFF',font='font24',alignment=pyxbmct.ALIGN_LEFT)
        desc = link['overview']
        rating = link['vote_average']
        try:
            trailerkey = link['videos']['results'][0]['key']
            trailerkey = ('TVSHOW|%s' %trailerkey)
        except:
            trailerkey = 'No Trailer'
        rating = 'Rated : ' + str(rating) + ' / 10'
        MovieRating = pyxbmct.Label(rating,textColor='0xFFFFFFFF',font='font24',alignment=pyxbmct.ALIGN_LEFT)
        runtime = link['episode_run_time']
        runtime = str(runtime).replace('[','').replace(']','')
        runtime = 'Avg Episode Runtime : ' + str(runtime) + ' Mins'
        MovieLength = pyxbmct.Label(runtime,textColor='0xFFFFFFFF',font='font24',alignment=pyxbmct.ALIGN_LEFT)
        window = Main('Viewer')
        window.doModal()
        del window
def GoToNextPage(self,url):
	MainWindow(url)
	self.close()
def ShowText(self,text):
    new_text = text.encode("ascii", "ignore")
    updated_text = new_text.decode()
    self.textbox.autoScroll(4000, 4000, 4000)
    self.textbox.setText(updated_text)
def PlayTrailer(self,id,desc):
    if 'TVSHOW' in id:
        url = ('https://api.themoviedb.org/3/tv/%s?api_key=%s&append_to_response=videos' % (MovieID,TMDBAPI))
    else:
        url = ('https://api.themoviedb.org/3/movie/%s?api_key=%s&append_to_response=videos' % (MovieID,TMDBAPI))
    if 'No Trailer' in id:
        dialog.notification(AddonTitle, '[COLOR red][B]Sorry No Trailer Available For This Media[/B][/COLOR]', icon, 5000, False)
        quit()
    dialog.notification(AddonTitle, '[COLOR red][B]Finding Trailer Source Now[/B][/COLOR]', icon, 5000, False)
    link = requests.get(url).json()
    tailer = link['videos']['results']
    trailertitle = []
    trialerlinks = []
    for data in tailer:
        title = data['name']
        key = data['key']
        #playurl = ('plugin://plugin.video.youtube/play/?video_id=%s' % key)
        playurl = ('https://www.youtube.com/watch?v=%s' % key)
        trailertitle.append(title)
        trialerlinks.append(playurl)
    select = dialog.select('[B][COLOR red]F[COLOR white]ound these trailers[/COLOR][/B]',trailertitle)
    if select < 0: quit()
    stream_url = resolveurl.HostedMediaFile(trialerlinks[select]).resolve()
    liz = xbmcgui.ListItem(str(MovieTitle))
    liz.setArt({"thumb": str(Poster)})
    liz.setInfo('video', {'Plot': str(desc)})
    liz.setPath(stream_url)
    xbmc.Player ().play(stream_url, liz, False)
    quit()

def AddMovieToList(self,AddTitle,AddPoster,MovieID,IMDBNO,User):
	with open(MoviesXml % User, 'a') as f:
		newstring = ('\n%s|%s|%s|%s' % (AddTitle,AddPoster,MovieID,IMDBNO))
		f.write(newstring)
		f.close()
		dialog.notification(AddonTitle, '[COLOR red][B]Movie Added To Your Collection[/B][/COLOR]', icon, 5000, False)
	Movies.MainWindow(User)
	self.close()
def AddShowToList(self,AddTitle,AddPoster,MovieID,User):
	with open(ShowsXml % User, 'a') as f:
		newstring = ('\n%s|%s|%s' % (AddTitle,AddPoster,MovieID))
		f.write(newstring)
		f.close()
		dialog.notification(AddonTitle, '[COLOR red][B]Show Added To Your Collection[/B][/COLOR]', icon, 5000, False)
	Shows.MainWindow(User)
	self.close()
def List_Selected(self):
	Player(AddTitle, str(Media_Link), AddPoster,desc)
def FindSources(self,name,year,IMDBNO,desc):
    global Item_Title
    global Item_Link
    global Item_Icon
    Item_Title =  []
    Item_Link  =  []
    Item_Icon  =  []
    Media_Link =  []
    MovieTitle.setVisible(False)
    Release.setVisible(False)
    MovieRating.setVisible(False)
    MovieLength.setVisible(False)
    self.textbox.setVisible(False)
    self.List.setVisible(True)
    Item_Title.append('[B][COLOR deepskyblue]SOURCES FOR % s[/B][/COLOR]' % name)
    self.List.addItem('[B][COLOR deepskyblue]SOURCES FOR % s[/B][/COLOR]' % name)
    Item_Link.append('')
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    headers = {'User-Agent': ua}
    url = ('https://torrentio.strem.fun/yts,eztv,rarbg,1337x,kickasstorrents,torrentgalaxy,magnetdl,horriblesubs,nyaasi,nyaapantsu/stream/movie/%s.json' % IMDBNO)
    link = requests.get(url,headers=headers).json()
    for data in link['streams']:
        quality = data['name'].replace('Torrentio','').strip()
        title = data['title'].strip().replace('\n','')
        new_title = title.encode("ascii", "ignore")
        updated_title = new_title.decode()
        hashfile = data['infoHash']
        self.List.addItem('[B][COLOR deepskyblue]%s | %s[/B][/COLOR]' % (quality,updated_title))
        playconstruct = ('magnet:?xt=urn:btih:%s' % hashfile)
        Item_Link.append(playconstruct)
    self.setFocus(self.List)
    self.setFocus(self.List)


def DeleteMovieFromList(self,removeme,MovieID,User):
	with open(MoviesXml % User, "r") as f:
		lines = f.readlines()
	with open(MoviesXml % User, "w") as f:
		for line in lines:
			if MovieID not in line:
				f.write(line)
	dialog.notification(AddonTitle, '[COLOR red][B]Movie Removed From Your Collection[/B][/COLOR]', icon, 5000, False)
	ReturnHome(self,User)
def DeleteShowFromList(self,removeme,MovieID,User):
	with open(ShowsXml % User, "r") as f:
		lines = f.readlines()
	with open(ShowsXml % User, "w") as f:
		for line in lines:
			if MovieID not in line:
				f.write(line)
	dialog.notification(AddonTitle, '[COLOR red][B]Show Removed From Your Collection[/B][/COLOR]', icon, 5000, False)
	ReturnHome(self,User)
def ReturnHome(self,User):
	if 'Movie' in source:
		Movies.MainWindow(User)
		self.close()
	else:
		Shows.MainWindow(User)
		self.close()
def ShowSeasons(self,removeme,MovieID):
	seasons.listwindow(removeme,MovieID)
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
class Main(pyxbmct.AddonFullWindow):
	xbmc.executebuiltin("Dialog.Close(busydialog)")
	def __init__(self, title='Flex'):
		super(Main, self).__init__(title)
		self.setGeometry(1280, 720, 100, 50)
		Background  = pyxbmct.Image(Background_Image)
		self.placeControl(Background, -10, -1, 123, 52)
		self.set_info_controls()
		self.set_active_controls()
		self.set_navigation()
		self.connect(pyxbmct.ACTION_NAV_BACK, lambda:ReturnHome(self,User))
		self.connect(self.button5, lambda:ReturnHome(self,User))
		self.connect(self.button2, lambda:DeleteMovieFromList(self,removeme,MovieID,User))
		self.connect(self.button1, lambda:AddMovieToList(self,AddTitle,AddPoster,MovieID,IMDBNO,User))
		self.connect(self.button3, lambda:PlayTrailer(self,trailerkey,desc))
		self.connect(self.button4, lambda:FindSources(self,AddTitle,MovieYear,IMDBNO,desc))
		self.connect(self.List, lambda:List_Selected(self))
		if 'TV' in source:
			self.connect(self.button6, lambda:AddShowToList(self,AddTitle,AddPoster,MovieID,User))
			self.connect(self.button7, lambda:DeleteShowFromList(self,removeme,MovieID,User))
			self.connect(self.button8, lambda:ShowSeasons(self,removeme,MovieID))
		ShowText(self,desc)
		self.placeControl(Poster, 30, 2, 70, 11)
		self.placeControl(MovieTitle, 30, 16, 40, 20)
		self.placeControl(Release, 40, 16, 40, 15)
		self.placeControl(MovieRating, 40, 40, 40, 15)
		self.placeControl(MovieLength, 45, 16, 40, 15)
		if 'TV' in source:
			self.setFocus(self.button6)
		else: self.setFocus(self.button1)
	def set_info_controls(self):
		self.textbox = pyxbmct.TextBox()
		self.Hello = pyxbmct.Label('', textColor='0xFFF44248', font='font60', alignment=pyxbmct.ALIGN_CENTER)
		self.placeControl(self.Hello, -4, 1, 1, 50)
		self.placeControl(self.textbox, 55, 16, 37, 30)
	def set_active_controls(self):
		#else:
		self.button1 = pyxbmct.Button('',   focusTexture=AddMovieS,   noFocusTexture=AddMovie)
		self.placeControl(self.button1, 95, 16,  7, 5)
		self.button2 = pyxbmct.Button('',   focusTexture=DeleteMovieS,   noFocusTexture=DeleteMovie)
		self.placeControl(self.button2, 95, 22,  7, 5)
		self.button3 = pyxbmct.Button('',   focusTexture=TrailerS,   noFocusTexture=Trailer)
		self.placeControl(self.button3, 95, 28,  7, 5)
		self.button4 = pyxbmct.Button('',   focusTexture=FindLinksS,   noFocusTexture=FindLinks)
		self.placeControl(self.button4, 95, 34,  7, 5)
		self.button5 = pyxbmct.Button('',   focusTexture=BackS,   noFocusTexture=Back)
		self.placeControl(self.button5, 95, 40,  7, 5)
		self.List =	pyxbmct.List(buttonFocusTexture=Listbg,_space=12,_itemTextYOffset=-7,_itemTextXOffset=-1,textColor='0xFFFFFFFF')
		self.placeControl(self.List, 27, 15, 70, 30)
		self.List.setVisible(False)
		# self.button7.setVisible(False)
		if 'TV' in source:
			self.button6 = pyxbmct.Button('',   focusTexture=AddShowS,   noFocusTexture=AddShow)
			self.placeControl(self.button6, 95, 16,  7, 5)
			self.button7 = pyxbmct.Button('',   focusTexture=DeleteShowS,   noFocusTexture=DeleteShow)
			self.placeControl(self.button7, 95, 22,  7, 5)
			self.button8 = pyxbmct.Button('',   focusTexture=ViewSeasonsS,   noFocusTexture=ViewSeasons)
			self.placeControl(self.button8, 95, 34,  7, 5)
			self.button1.setVisible(False)
			self.button2.setVisible(False)
			self.button4.setVisible(False)
			self.button6.setVisible(True)
			self.button7.setVisible(True)
			self.button8.setVisible(True)
		self.connectEventList(
			[pyxbmct.ACTION_MOVE_DOWN,
			 pyxbmct.ACTION_MOVE_UP,
			 pyxbmct.ACTION_MOUSE_WHEEL_DOWN,
			 pyxbmct.ACTION_MOUSE_WHEEL_UP,
			 pyxbmct.ACTION_MOUSE_MOVE,
			 pyxbmct.ACTION_MOVE_LEFT,
			 pyxbmct.ACTION_MOVE_RIGHT],
			self.List_update)
	def set_navigation(self):
		self.button1.controlRight(self.button2)
		self.button1.controlUp(self.List)
		self.button2.controlRight(self.button3)
		self.button2.controlUp(self.List)
		self.button3.controlRight(self.button4)
		self.button3.controlUp(self.List)
		self.button4.controlRight(self.button5)
		self.button4.controlUp(self.List)
		self.button5.controlRight(self.button1)
		self.button5.controlUp(self.List)
		self.List.controlLeft(self.button1)
		self.List.controlRight(self.button1)
		if 'TV' in source:
			self.button3.controlRight(self.button8)
			self.button6.controlRight(self.button7)
			self.button7.controlRight(self.button3)
			self.button5.controlRight(self.button6)
			self.button8.controlRight(self.button5)

		self.button1.controlLeft(self.button5)
		self.button2.controlLeft(self.button1)
		self.button3.controlLeft(self.button2)
		self.button4.controlLeft(self.button3)
		self.button5.controlLeft(self.button4)
		if 'TV' in source:
			self.button3.controlLeft(self.button7)
			self.button7.controlLeft(self.button6)
			self.button6.controlLeft(self.button5)
			self.button5.controlLeft(self.button8)
			self.button8.controlLeft(self.button3)

	def setAnimation(self, control):
		control.setAnimations([('WindowOpen', 'effect=slide start=2000 end=0 time=1000',),
								('WindowClose', 'effect=slide start=100 end=1400 time=500',)])
	def List_update(self):
		global Media_Link
		if self.getFocus() == self.List:
			position = self.List.getSelectedPosition()
			Media_Link  = Item_Link[position]