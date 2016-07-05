##########################################################################
# Author:               Eduardo Crispim, emcrispim@gmail.com
# Date:                 July, 2016
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
#########################################################################

from kivy.uix.boxlayout import BoxLayout
from plyer import vibrator

'''
   class ViewButtons
'''
class ViewButtons(BoxLayout):

  current = 0
  bindroot = None
  vibrate = False

#--------------------------------------------------------------------
  def init(self,bindroot):
    self.bindroot = bindroot
    self.vibrate = bindroot.vibrate


#--------------------------------------------------------------------

  def doEnable(self,enable):
    if enable:
      self.opacity=1
      self.size_hint=(1,1)
      self.disabled = False
    else:
      self.size_hint=(None,None)
      self.size=(0,0)
      self.disabled = True
      self.opacity=0
#--------------------------------------------------------------------
  def setNextView(self):
    if self.vibrate:
      vibrator.vibrate(0.05)
    self.bindroot.setFG("/command/view/next","true")
    self.setControllerView(self.current+1)
    
#--------------------------------------------------------------------
  def setPreviousView(self):
    if self.vibrate:
      vibrator.vibrate(0.05)
    self.bindroot.setFG("/command/view/prev","true")
    self.setControllerView(self.current-1)

#--------------------------------------------------------------------
  def setView(self,value):
    self.bindroot.grabbed['view']={"state":"grabbed"}
    if self.vibrate:
      vibrator.vibrate(0.05)
    self.current=value
    self.bindroot.setFG("/sim/current-view/view-number",value)
    self.bindroot.grabbed['view']={"state":"ungrabbed"}

#--------------------------------------------------------------------
  def setControllerView(self,value):
    self.bindroot.grabbed['view']={"state":"grabbed"}
    self.current=value
    if value==0:
      self.ids.cpt_view.state="normal"
      self.ids.cpt_view._do_press()
    elif value==9:
      self.ids.cdu_view.state="normal"
      self.ids.cdu_view._do_press()
    elif value==10:
      self.ids.oh_view.state="normal"
      self.ids.oh_view._do_press()
    elif value==12:
      self.ids.fgear_view.state="normal"
      self.ids.fgear_view._do_press()
    elif value==1:
      self.ids.heli_view.state="normal"
      self.ids.heli_view._do_press()
    elif value==6:
      self.ids.flyby_view.state="normal"
      self.ids.flyby_view._do_press()
    else:
      self.ids.cpt_view.state="down"
      self.ids.cpt_view._do_press()
    self.bindroot.grabbed['view']={"state":"ungrabbed"}
