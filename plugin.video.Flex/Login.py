#############################################################
#################### START ADDON IMPORTS ####################
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import os
import re
import requests
import sys
import base64
import json
import time
import datetime
import Movies
import pyxbmct

dialog = xbmcgui.Dialog()
#############################################################
#################### SET ADDON ID ###########################
_addon_id_ = 'plugin.video.Flex'
_self_ = xbmcaddon.Addon(id=_addon_id_)
AddonTitle = '[B][COLOR white]FLE[COLOR blue]X[/B][/COLOR]'
dp = xbmcgui.DialogProgress()
icon  = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_, 'icon.png'))
#############################################################
#################### SET ADDON THEME DIRECTORY ##############
_theme_			= _self_.getSetting('Theme')
_images_		= '/resources/' + _theme_	
UsersXml		= xbmcvfs.translatePath(os.path.join('special://home/userdata/addon_data/' + _addon_id_, 'users.xml'))
#############################################################
#################### SET ADDON THEME IMAGES #################
Background_Image	= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'loginbackgroundblack.png'))
### FRAMES
MaleAdult = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'man.png'))
FemaleAdult = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'women.png'))
MaleChild = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'boy.png'))
FemaleChild = xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'girl.png'))
Frame1				= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'Frame.png'))
Frame1S				= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'FrameS.png'))
UserAdd				= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'Adduser.png'))
UserAddS				= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'AdduserS.png'))
UserRemove				= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'Deleteuser.png'))
UserRemoveS				= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'DeleteuserS.png'))
MoviesXml		= xbmcvfs.translatePath(os.path.join('special://home/userdata/addon_data/' + _addon_id_, '%smovies.xml'))
ShowsXml		= xbmcvfs.translatePath(os.path.join('special://home/userdata/addon_data/' + _addon_id_, '%sshows.xml'))
#IntroVideo		= xbmcvfs.translatePath(os.path.join('special://home/addons/' + _addon_id_, 'FlexIntro.mp4'))
addontemp		= xbmcvfs.translatePath(os.path.join('special://home/userdata/addon_data/' + _addon_id_))

#############################################################
########## Function To Call That Starts The Window ##########
#xbmc.executebuiltin('xbmc.activatewindow(10000)')
            #xbmc.Player().stop()
def PIN():
    pin = _self_.getSetting('pin')
    if pin == '': pin = 'EXPIRED'
    if pin == 'EXPIRED':
        _self_.setSetting('pinused','False')
        dialog.ok(AddonTitle,"[COLOR yellow]Please visit [COLOR lime]https://pinsystem.co.uk[COLOR yellow] to generate an Access Token For [COLOR lime]Flex[COLOR yellow] then enter it after clicking ok[/COLOR]")
        string =''
        keyboard = xbmc.Keyboard(string, '[COLOR red]Please Enter Pin Generated From Website(Case Sensitive)[/COLOR]')
        keyboard.doModal()
        if keyboard.isConfirmed():
            string = keyboard.getText()
            if len(string)>1:
                term = string.title()
                _self_.setSetting('pin',term)
                PIN()
            else: quit()
        else:
            quit()
    if not 'EXPIRED' in pin:
        pinurlcheck = ('https://pinsystem.co.uk/service.php?code=%s&plugin=RnVja1lvdSE' % pin)
        link = requests.get(pinurlcheck,verify=False).text
        if len(link) <=2 or 'Pin Expired' in link:
            _self_.setSetting('pin','EXPIRED')
            PIN()
        else:
            registerpin = _self_.getSetting('pinused')
            if registerpin == 'False':
                try:
                    requests.get('https://pinsystem.co.uk/checker.php?code=99999&plugin=Flex').text
                    _self_.setSetting('pinused','True')
                except: pass
            else: pass
            
def MainWindow():
    PIN()
    if not os.path.exists(addontemp):
        os.makedirs(addontemp)
    if not os.path.exists(UsersXml):
        open(UsersXml, 'a').close()
    window = Main('Flex')
    window.doModal()
    del window
def POPUSERS():
    # PlayIntro = _self_.getSetting('introvid')
    # if PlayIntro == 'true':
        # xbmc.Player().play(IntroVideo)
        # time.sleep(10)
    logos = []
    titles = []
    global Poster1
    global Poster2
    global Poster3
    global Poster4
    global Person1
    global Person2
    global Person3
    global Person4
    with open(UsersXml) as F:
        for cnt, line in enumerate(F):
            if line == '\n': continue
            else:
                try:
                    name = line.split('|')[0]
                    sex = line.split('|')[1]
                    age = line.split('||')[1]
                    if 'MALE' in sex and 'ADULT' in age:
                        logos.append(MaleAdult)
                    elif 'MALE' in sex and 'CHILD' in age:
                        logos.append(MaleChild)
                    elif 'WOMEN' in sex and 'ADULT' in age:
                        logos.append(FemaleAdult)
                    elif 'WOMEN' in sex and 'CHILD' in age:
                        logos.append(FemaleChild)
                    titles.append(name)
                except: pass
    try: Poster1 = logos[0]
    except: Poster1 = ''
    try: Poster2 = logos[1]
    except: Poster2 = ''
    try: Poster3 = logos[2]
    except: Poster3 = ''
    try: Poster4 = logos[3]
    except: Poster4 = ''
    try: Person1 = titles[0]
    except: Person1 = ''
    try: Person2 = titles[1]
    except: Person2 = ''
    try: Person3 = titles[2]
    except: Person3 = ''
    try: Person4 = titles[3]
    except: Person4 = ''
def CheckUsers(self):
    with open(UsersXml) as f:
        first = f.read()
        first = first.replace('\n','')
        if first == '':
            dialog.ok(AddonTitle,"Welcome To Flex, No Users Have Been Setup Yet, Please Create Your First User, Click Ok To Proceed")
            string =''
            keyboard = xbmc.Keyboard(string, '[COLOR white][B]What Is The Users Name?[/B][/COLOR]')
            keyboard.doModal()
            if keyboard.isConfirmed():
                string = keyboard.getText()
                if len(string)>=1:
                    username = string.upper()
            else:
                dialog.ok(AddonTitle,"Sorry You Need To Setup At Least One User")
                quit()
            MORF = xbmcgui.Dialog().yesno(AddonTitle, 'Is %s Male Or Female?' % username,yeslabel='Male',nolabel='Female')
            if MORF: sex = 'MALE'
            else: sex = 'WOMEN'
            AGE = xbmcgui.Dialog().yesno(AddonTitle, 'Is %s An Adult Or Child?' % username,yeslabel='Adult',nolabel='Child')
            if AGE: prop = 'ADULT'
            else: prop = 'CHILD'
            with open(UsersXml,'a') as f:
                newstring = ('%s|%s||%s\n' % (username,sex,prop))
                f.write(newstring)
                if not os.path.exists(ShowsXml % username):
                    open(ShowsXml % username, 'a').close()
                if not os.path.exists(MoviesXml % username):
                    open(MoviesXml % username, 'a').close()
            MainWindow()
            self.close()
        else:
            POPUSERS()
def DeleteUser(self):
	names = []
	pos = []
	with open(UsersXml) as F:
		for cnt, line in enumerate(F):
			if line == '\n': continue
			else:
				try:
					name = line.split('|')[0]
					names.append(name)
					pos.append(cnt)
				except: pass
	dialog = xbmcgui.Dialog()
	select = dialog.select("Delete Which User?",names)
	if select < 0: quit()
	with open(UsersXml, "r") as f:
		lines = f.readlines()
	with open(UsersXml, "w") as f:
		for cnt,line in enumerate(lines):
			if str(pos[select]) not in str(cnt):
				f.write(line)
	os.remove(MoviesXml % names[select])
	os.remove(ShowsXml % names[select])
	dialog.notification(AddonTitle, '[COLOR red][B]User %s Removed[/B][/COLOR]' % names[select], icon, 5000, False)
	MainWindow()
	self.close()
def AddUser(self):
	if Person4 == '':
		string =''
		keyboard = xbmc.Keyboard(string, '[COLOR white][B]What Is The Users Name?[/B][/COLOR]')
		keyboard.doModal()
		if keyboard.isConfirmed():
			string = keyboard.getText()
			if len(string)>1:
				username = string.upper()
		else: quit ()
		MORF = xbmcgui.Dialog().yesno(AddonTitle, 'Is %s Male Or Female?' % username,'',yeslabel='Male',nolabel='Female')
		if MORF: sex = 'MALE'
		else: sex = 'WOMEN'
		AGE = xbmcgui.Dialog().yesno(AddonTitle, 'Is %s An Adult Or Child?' % username,'',yeslabel='Adult',nolabel='Child')
		if AGE: prop = 'ADULT'
		else: prop = 'CHILD'
		with open(UsersXml,'a') as f:
			newstring = ('%s|%s||%s\n' % (username,sex,prop))
			f.write(newstring)
			if not os.path.exists(ShowsXml % username):
				open(ShowsXml % username, 'a').close()
			if not os.path.exists(MoviesXml % username):
				open(MoviesXml % username, 'a').close()
		MainWindow()
		self.close()
	else: dialog.notification(AddonTitle, '[COLOR red][B]Sorry You Can Only Have 4 Users[/B][/COLOR]', icon, 5000, False)
def LoadProfile(self,profile):
	Movies.MainWindow(profile)
	self.close()
def QuitAddon(self):
    xbmc.executebuiltin("Container.Update(path,replace)")
    xbmc.executebuiltin("ActivateWindow(Home)")
    self.close()


#############################################################
######### Class Containing the GUi Code / Controls ##########
class Main(pyxbmct.AddonFullWindow):
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    def __init__(self, title='Flex'):
        super(Main, self).__init__(title)
        self.setGeometry(1280, 720, 100, 50)
        Background  = pyxbmct.Image(Background_Image)
        CheckUsers(self)
        # T , L , H , W
        #Movie1 = pyxbmct.Image(Poster1)
        self.placeControl(Background, -10, -1, 123, 52)
        self.set_info_controls()
        User1 = pyxbmct.Image(Poster1)
        User2 = pyxbmct.Image(Poster2)
        User3 = pyxbmct.Image(Poster3)
        User4 = pyxbmct.Image(Poster4)
        NameTitle1 = pyxbmct.Label(Person1,textColor='0xFFFFFFFF',font='font18',alignment=pyxbmct.ALIGN_CENTER)
        NameTitle2 = pyxbmct.Label(Person2,textColor='0xFFFFFFFF',font='font18',alignment=pyxbmct.ALIGN_CENTER)
        NameTitle3 = pyxbmct.Label(Person3,textColor='0xFFFFFFFF',font='font18',alignment=pyxbmct.ALIGN_CENTER)
        NameTitle4 = pyxbmct.Label(Person4,textColor='0xFFFFFFFF',font='font18',alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(NameTitle1, 40, 7, 10, 6)
        self.placeControl(NameTitle2, 40, 17, 10, 6)
        self.placeControl(NameTitle3, 40, 27, 10, 6)
        self.placeControl(NameTitle4, 40, 37, 10, 6)
        self.placeControl(User1, 49, 7, 30, 6)
        self.placeControl(User2, 49, 17, 30, 6)
        self.placeControl(User3, 49, 27, 30, 6)
        self.placeControl(User4, 49, 37, 30, 6)
        self.set_active_controls()
        self.connect(self.button1, lambda:LoadProfile(self,Person1))
        self.connect(self.button2, lambda:LoadProfile(self,Person2))
        self.connect(self.button3, lambda:LoadProfile(self,Person3))
        self.connect(self.button4, lambda:LoadProfile(self,Person4))
        self.connect(self.button5, lambda:AddUser(self))
        self.connect(self.button6, lambda:DeleteUser(self))
        self.setFocus(self.button1)
        self.set_navigation()
        self.connect(pyxbmct.ACTION_NAV_BACK, lambda:QuitAddon(self))
        #self.connect(self.button2, lambda:TvShows(self))
    def set_info_controls(self):
        self.Hello = pyxbmct.Label('', textColor='0xFFF44248', font='font60', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.Hello, -4, 1, 1, 50)
    def set_active_controls(self):
        self.button1 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
        self.placeControl(self.button1, 47, 5, 34, 10)
        self.button2 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
        self.placeControl(self.button2, 47, 15, 34, 10)
        self.button3 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
        self.placeControl(self.button3, 47, 25, 34, 10)
        self.button4 = pyxbmct.Button('',   focusTexture=Frame1S,   noFocusTexture=Frame1)
        self.placeControl(self.button4, 47, 35, 34, 10)
        self.button5 = pyxbmct.Button('',   focusTexture=UserAddS,   noFocusTexture=UserAdd)
        self.placeControl(self.button5, 82, 22, 11, 6)
        self.button6 = pyxbmct.Button('',   focusTexture=UserRemoveS,   noFocusTexture=UserRemove)
        self.placeControl(self.button6, 94, 22, 11, 6)
        # self.connectEventList(
            # [pyxbmct.ACTION_MOVE_DOWN,
            # pyxbmct.ACTION_MOVE_UP,
            # pyxbmct.ACTION_MOUSE_WHEEL_DOWN,
            # pyxbmct.ACTION_MOUSE_WHEEL_UP,
            # pyxbmct.ACTION_MOUSE_MOVE],)
    def set_navigation(self):
        self.button1.controlRight(self.button2)
        self.button2.controlRight(self.button3)
        self.button3.controlRight(self.button4)
        self.button4.controlRight(self.button1)
        self.button1.controlLeft(self.button4)
        self.button2.controlLeft(self.button1)
        self.button3.controlLeft(self.button2)
        self.button4.controlLeft(self.button3)
        self.button1.controlDown(self.button5)
        self.button2.controlDown(self.button5)
        self.button3.controlDown(self.button5)
        self.button4.controlDown(self.button5)
        self.button5.controlDown(self.button6)
        self.button5.controlUp(self.button1)
        self.button6.controlUp(self.button5)
    def setAnimation(self, control):
        control.setAnimations([('WindowOpen', 'effect=slide start=2000 end=0 time=1000',),
                                ('WindowClose', 'effect=slide start=100 end=1400 time=500',)])
if __name__ == '__main__': MainWindow()
