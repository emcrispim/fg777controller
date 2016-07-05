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
from plyer import vibrator
from kivy.clock import Clock

'''
   class APMenu
'''
class APMenu(Popup):

  vibrate = ObjectProperty(None)
  bindroot = ObjectProperty(None)
  ctrlupdate = False

  data = {'AP': {'key':'/instrumentation/afds/inputs/AP',
                 'down' :1,
                 'normal':0,
                 'current':0
          },
          'AT':{'key':'/instrumentation/afds/inputs/autothrottle-index',
                'down':5,
                'normal':0,
                'current':0
          },
          'FD':{'key':'/instrumentation/afds/inputs/FD',
                'down':1,
                'normal':0,
                'current':0
          },
          'VS':{'key':'/instrumentation/afds/inputs/vertical-index',
                'down':2,
                'normal':0,
                'current':0
          },
          'FLCH':{'key':'/instrumentation/afds/inputs/vertical-index',
                'down':8,
                'normal':0,
                'current':0
          },
          'VNAV':{'key':'/instrumentation/afds/inputs/vertical-index',
                'down':3,
                'normal':0,
                'current':0
          },
          'atarmed':{'key':'/instrumentation/afds/inputs/at-armed',
                'down':1,
                'normal':0,
                'current':0
          },
          'atarmed1':{'key':'/instrumentation/afds/inputs/at-armed[1]',
                'down':1,
                'normal':0,
                'current':0
          },
          'IAS':{'key':'/autopilot/settings/target-speed-kt',
                'current':200
          },
          'HDG':{'key':'/autopilot/settings/heading-bug-deg',
                'current':0
          },
          'HDGHold':{'key':'/instrumentation/afds/inputs/lateral-index',
                'down':2,
                'normal':1,
                'current':0
          },
          'LNAV':{'key':'/instrumentation/afds/inputs/lateral-index',
                'down':3,
                'normal':2,
                'current':0
          },
          'LOC':{'key':'/instrumentation/afds/inputs/lateral-index',
                'down':4,
                'normal':2,
                'current':0
                # disabled when app armed or in glidescope
          },
          'APP':{'key':'/instrumentation/afds/inputs/gs-armed',
                'down':1,
                'normal':0,
                'current':0
                # active if gs-armed true
                # or 
                # gs-armed false and vertical-index = 6
          },
          'ALT':{'key':'/autopilot/settings/counter-set-altitude-ft',
                'current':10000
          },
          'ALTHold':{'key':'/instrumentation/afds/inputs/vertical-index',
                'down':1,
                'normal':0,
                'current':0
          },
          'VFS':{'key':'/autopilot/settings/vertical-speed-fpm',
                'current':0
          }

}

#--------------------------------------------------------------------
  def __init__(self, **kwargs):
    super(APMenu, self).__init__(**kwargs)

#--------------------------------------------------------------------
  def on_open(self):
    self.toController()
    self.bindroot.update_timer=True
    self.ctrlupdate = True

#--------------------------------------------------------------------
  def on_dismiss(self):
    self.ctrlupdate = False

#--------------------------------------------------------------------
  def toController(self):
    if self.bindroot.controlsFG!=None:
      controls = self.bindroot.controlsFG
      self.ToggleFromFG('AP',int(controls[20]))
      self.iToggleFromFG('AT',int(controls[21]))
      self.ToggleFromFG('FD',int(controls[22]))
      self.ToggleFromFG('VS',int(controls[23]))
      self.ToggleFromFG('FLCH',int(controls[23]))
      self.ToggleFromFG('VNAV',int(controls[23]))
      self.ToggleFromFG('ALTHold',int(controls[23]))
      self.ToggleFromFG('atarmed',int(controls[24]))
      self.ToggleFromFG('atarmed1',int(controls[25]))
      self.data['IAS']['current'] = int(controls[26])
      self.ids.label_ias.text = 'IAS '+controls[26]
      self.data['HDG']['current'] = int(controls[27])
      self.ids.label_hdg.text = 'HDG '+ controls[27]
      self.data['ALT']['current'] = int(controls[28])
      self.ids.label_alt.text = 'ALT '+ controls[28]
      self.data['VFS']['current'] = int(controls[29])
      self.ids.label_vfs.text = 'VFS '+ controls[29]
      self.ToggleFromFG('HDGHold',int(controls[30]))
      self.ToggleFromFG('LNAV',int(controls[30]))
      self.ToggleFromFG('LOC',int(controls[30]))

      if int(controls[31])==1 or int(controls[23])==6:
        self.ToggleFromFG('APP',1)
        self.ToggleFromFG('LOC',2)
      else:
        self.ToggleFromFG('APP',0)
      


      
#--------------------------------------------------------------------
  def enableUpdate(self,dt):
    self.ctrlupdate = True


#--------------------------------------------------------------------
  def iToggleFromFG(self,item,value):
    if self.data[item]['current']!= value:
      self.data[item]['current'] = value
      if self.data[item]['normal'] == value:
        self.ids[item].state = 'normal'
      else:
        self.ids[item].state = 'down'

#--------------------------------------------------------------------
  def ToggleFromFG(self,item,value):
    if self.data[item]['current']!= value:
      self.data[item]['current'] = value
      if self.data[item]['down'] == value:
        self.ids[item].state = 'down'
        
      else:
        self.ids[item].state = 'normal'

#--------------------------------------------------------------------
  def setToggle(self,state,item):
    if (item=='LOC' or item=='VNAV' or item=='FLCH' or item=='ALTHold' or item=='HDGHold' or item=='VS') and state =='normal':
      self.ids[item].state ='down'
    else:
      if item=='HDGHold':
        self.data['HDG']['current'] = self.bindroot.current['heading']
        self.setHDG(0)
      elif item=='FLCH':
        self.setFG('VS',self.data['VS']['key'],8)
        self.setFG('AT',self.data['AT']['key'],1)
      elif item=='APP' and state=='normal' and int(self.bindroot.controlsFG[23])==6:
        self.ids[item].state='down'
      else:  
        self.setFG(item,self.data[item]['key'],self.data[item][state])

#--------------------------------------------------------------------
  def setIAS(self,delta):
    self.data['IAS']['current']+=delta
    IAS = self.data['IAS']
    self.ids.label_ias.text = 'IAS '+str(IAS['current'])
    self.setFG('IAS',IAS['key'],IAS['current'])

#--------------------------------------------------------------------
  def setHDG(self,delta):
    newvalue = self.data['HDG']['current']+delta
    if newvalue<0:
      self.data['HDG']['current']=360-abs(newvalue)
    elif newvalue>359:
      self.data['HDG']['current']=newvalue-360
    else:
      self.data['HDG']['current'] = newvalue

    self.ids.label_hdg.text = 'HDG '+str(self.data['HDG']['current'])
    self.setFG('HDG',self.data['HDG']['key'],self.data['HDG']['current'])


#--------------------------------------------------------------------
  def setALT(self,delta):
    newvalue = self.data['ALT']['current']+delta
    if newvalue > 0 and newvalue < 50000:
      self.data['ALT']['current'] = newvalue
      self.ids.label_alt.text = 'ALT '+str(newvalue)
      self.setFG('ALT',self.data['ALT']['key'],newvalue)

#--------------------------------------------------------------------
  def setVFS(self,delta):
    newvalue = self.data['VFS']['current']+delta
    if newvalue > -8000 and newvalue < 6000:
      self.data['VFS']['current'] = newvalue
      self.ids.label_vfs.text = 'VFS '+str(newvalue)
      self.setFG('VFS',self.data['VFS']['key'],newvalue)

#--------------------------------------------------------------------
  def setFG(self,item,key,value):
    self.data[item]['current']=value
    self.ctrlupdate = False
    Clock.unschedule(self.enableUpdate)
    if self.vibrate:
      vibrator.vibrate(0.05)
    self.bindroot.setFG(key,value)
    Clock.schedule_once(self.enableUpdate,2)


