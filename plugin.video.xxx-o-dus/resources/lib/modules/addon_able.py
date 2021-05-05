import datetime
import os
from sqlite3 import dbapi2 as db_lib
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
from six import PY2
translatePath = xbmc.translatePath if PY2 else xbmcvfs.translatePath
db_dir = translatePath("special://profile/Database")
if PY2: db_path = os.path.join(db_dir, 'Addons27.db')
else: db_path = os.path.join(db_dir, 'Addons33.db')

conn = db_lib.connect(db_path)
conn.text_factory = str


def set_enabled(newaddon, data=None):
    #if xbmcaddon.Addon().getAddonInfo('version') > 16.5:
        setit = 1
        if data is None:
            data = ''
        now = datetime.datetime.now()
        date_time = str(now).split('.')[0]
        # sql = 'REPLACE INTO installed (addonID,enabled) VALUES(?,?)'
        sql = 'REPLACE INTO installed (addonID,enabled,installDate) VALUES(?,?,?)'
        conn.execute(sql, (newaddon, setit, date_time,))
        conn.commit()
        # xbmc.executebuiltin("InstallAddon(%s)" % newaddon)
        xbmc.executebuiltin("UpdateLocalAddons()")
    #else:
       # pass


def setall_enable():
    #if xbmcaddon.Addon().getAddonInfo('version') > 16.5:
        addonfolder = translatePath(os.path.join('special://home', 'addons'))
        contents = os.listdir(addonfolder)
        conn.executemany('update installed set enabled=1 WHERE addonID = (?)', ((val,) for val in contents))
        conn.commit()
    #else:
        #pass
