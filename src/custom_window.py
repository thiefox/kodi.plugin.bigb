# -*- coding: UTF-8 -*-

import sys
import xbmcgui
import xbmcplugin

class PY_sort_window(xbmcgui.Window) :
	def onInit(self):
		print("Window.onInit method called from Kodi")
		return
	
	def onAction(self, action):
		if action.getId() == ACTION_PREVIOUS_MENU :
			print('action received: previous')
			self.close()
		if action.getId() == ACTION_SHOW_INFO :
			print('action received: show info')
		if action.getId() == ACTION_STOP :
			print('action received: stop')
		if action.getId() == ACTION_PAUSE :
			print('action received: pause')
		return


addon_handle = int(sys.argv[1])

#设置内容类别，'movies/videos'
xbmcplugin.setContent(addon_handle, 'movies')

url = 'nfs://10.10.0.3/volume2/BB8/FGT/三级/与鸭共舞.1992/与鸭共舞.1992.BDRip.2AC3.HFKACT.mkv'
#li = xbmcgui.ListItem('thiefox First Video!', iconImage='DefaultVideo.png')
li = xbmcgui.ListItem('thiefox与鸭共舞')
xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

url = 'nfs://10.10.0.3/volume2/BB8/CHD'
li = xbmcgui.ListItem('CHD')
xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)


xbmcplugin.endOfDirectory(addon_handle)