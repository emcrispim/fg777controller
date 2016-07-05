##########################################################################
# Author:               Eduardo Crispim, emcrispim@gmail.com
# Date:                 July, 2016
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
#########################################################################


from kivy.uix.popup import Popup
from kivy.properties import  ObjectProperty
from plyer import accelerometer
from kivy.clock import Clock

'''
   class AcclPopup
'''   
class AcclPopup(Popup):
  
  timer = 3
  has_accl = True
  bindroot = ObjectProperty(None)

#--------------------------------------------------------------------
  def __init__(self, **kwargs):
    super(AcclPopup, self).__init__(**kwargs)

#--------------------------------------------------------------------
  def on_open(self):
    self.bindroot.update_timer=True
    try:
      accelerometer._get_acceleration()
      accelerometer.enable()
    except:
      self.has_accl = False

    if self.has_accl:
      Clock.schedule_interval(self.loop,1)
      self.ids.timer_label.text = "Calibrate in %s s" % str(self.timer)
    else:
      self.ids.timer_label.text = "Accelerometer not available"
      self.bindroot.ids.accl.state ="normal"

#--------------------------------------------------------------------
  def loop(self,dt):
    if self.timer>0:
      self.timer-=1
      self.ids.timer_label.text = "Calibrate in %s s" % str(self.timer)
    else:
      Clock.unschedule(self.loop)
      self.doacl = True
      self.dismiss()

#--------------------------------------------------------------------
  def on_dismiss(self):
    if self.has_accl:
      self.bindroot.doAccelerometer()