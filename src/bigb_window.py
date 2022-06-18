# -*- coding: UTF-8 -*-

import sys
import xbmc
import xbmcgui
import xbmcplugin

class bigb_window(xbmcgui.Window) :
    def onInit(self) :
        xbmc.log('bigb_window onInit...')
        return

    def onAction(self, action) :
        if action.getId() == ACTION_PREVIOUS_MENU:
            print('action received: previous')
            self.close()
        if action.getId() == ACTION_SHOW_INFO:
            print('action received: show info')
        if action.getId() == ACTION_STOP:
            print('action received: stop')
        if action.getId() == ACTION_PAUSE:
            print('action received: pause')
        return

    def onControl(self, control):
        print("Window.onControl(control=[%s])" %control)
        return

    def onClick(self,controlId):
        print("onClick: The control with Id(%d) is clicked" %(controlId))
        return
    
    def onFocus(self,controlId):
        print("onFocus: The control with Id(%d) is focused" %(controlId))
        return
