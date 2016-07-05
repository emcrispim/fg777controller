##########################################################################
# Author:               Eduardo Crispim, emcrispim@gmail.com
# Date:                 July, 2016
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
#########################################################################

from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from plyer import vibrator
from kivy.graphics import Rectangle


'''
   class GearKnobWidget
'''
class GearKnobWidget(Widget):
  bindroot = None
  toffsety = None

#--------------------------------------------------------------------
  def on_touch_down(self,touch):
    if self.collide_point(*touch.pos):
      tx,ty = touch.pos
      self.toffsety = self.center_y - ty
      touch.grab(self)
      self.bindroot.grabbed['gear']={"state":"grabbed"}

#--------------------------------------------------------------------
  def on_touch_move(self,touch):
    if touch.grab_current is self:
      tx,ty = touch.pos
      ofy = ty + self.toffsety
      yref = self.parent.height
      if ofy>yref*0.33 and ofy<yref*0.78:
        self.center_y = ofy

#--------------------------------------------------------------------
  def on_touch_up(self,touch):
    if touch.grab_current is self:
      yref = self.parent.height
      if self.center_y<yref*0.55:
        #gear down
        self.toController(1)
        self.bindroot.setFG("/controls/gear/gear-down",1)
      else:
        #gear up
        self.toController(0)
        self.bindroot.setFG("/controls/gear/gear-down",0)
      touch.ungrab(self)
      self.bindroot.grabbed['gear']={"state":"ungrabbed"}

#--------------------------------------------------------------------
  def toController(self,value):
    yref = self.parent.height
    self.bindroot.current['gear']=value
    if value==0:
      self.center_y = yref*0.78
    else:
      self.center_y = yref*0.33


'''
   class AutoBrakeKnobWidget
'''
class AutoBrakeKnobWidget(Widget):

  trans_autobrakes = [{'UI':'RTO','CT':55},
                      {'UI':'OFF','CT':0},
                      {'UI':'DISARM','CT':-30},
                      {'UI':'1','CT':-55},
                      {'UI':'2','CT':-90},
                      {'UI':'3','CT':-120},
                      {'UI':'4','CT':-150},
                      {'UI':'MAX','CT':-180}
  ]

  angle = NumericProperty(0)
  bindroot = None
  cy = 0

#--------------------------------------------------------------------
  def on_touch_down(self,touch):
    if self.collide_point(*touch.pos):
      xy,self.cy = touch.pos
      touch.grab(self)
      self.bindroot.grabbed['autobrake']={"state":"grabbed"}

#--------------------------------------------------------------------
  def on_touch_move(self,touch):
    if touch.grab_current is self:
      tx,ty = touch.pos
      if abs(self.cy-ty)>20:
        if self.cy-ty>0:
          inc=-1
        else:
          inc=+1
        if self.bindroot.vibrate:
          vibrator.vibrate(0.02)
        self.setController(self.bindroot.current['autobrake']+inc)  
        self.cy = ty

#--------------------------------------------------------------------
  def on_touch_up(self,touch):
    if touch.grab_current is self:
      touch.ungrab(self)
      self.bindroot.setFG('/autopilot/autobrake/step',self.bindroot.current['autobrake'])
      self.bindroot.grabbed['autobrake']={"state":"ungrabbed"}
  
#--------------------------------------------------------------------
  def setController(self,value):
    if value>=-2 and value<=5:
      self.bindroot.current['autobrake'] = value
      self.angle = self.trans_autobrakes[value+2]['CT']


'''
   class ElevatorTrimWidget
'''
class ElevatorTrimWidget(Widget):

  bindroot = None

#--------------------------------------------------------------------
  def set(self,direction):
    self.bindroot.grabbed['elevatortrim']={"state":"grabbed"}
    if self.bindroot.vibrate:
      vibrator.vibrate(0.05)
    if direction=="up" and self.bindroot.current['elevatortrim']<1:
      self.toController(self.bindroot.current['elevatortrim']+0.01)
    elif direction=="down" and self.bindroot.current['elevatortrim']>-1:
      self.toController(self.bindroot.current['elevatortrim']-0.01)
    self.bindroot.update()
    self.bindroot.grabbed['elevatortrim']={"state":"ungrabbed"}

#--------------------------------------------------------------------
  def toController(self,value):
    self.bindroot.current['elevatortrim']=value
    self.center_y=self.parent.height/2+value*(self.parent.height/5.5)


'''
   class PadCtrl
'''
class PadCtrl(Widget):


  angle = NumericProperty(0)
  padactive=1
  bindroot = None
  threshold = None
  toffsetx = None
  toffsety = None

#--------------------------------------------------------------------
  def __init__(self,**kwargs):
    super(PadCtrl, self).__init__(**kwargs)

#--------------------------------------------------------------------
  def on_touch_down(self,touch):
    if self.collide_point(*touch.pos) and self.padactive:
      tx,ty = touch.pos
      self.toffsetx = self.center_x - tx
      self.toffsety = self.center_y - ty
      touch.grab(self)
      self.bindroot.grabbed['pad']={"state":"grabbed"}

#--------------------------------------------------------------------
  def on_touch_move(self,touch):
    if (touch.grab_current is self) and self.padactive:
      tx,ty=touch.pos
      ofx = tx + self.toffsetx
      ofy = ty + self.toffsety
      if (ofx>=self.width/2) and ofx<=(self.parent.width-self.width/2):
        self.center_x = ofx
        self.ControllerToFGCoordinates()
      if (ofy>=self.height/2) and (ofy<self.parent.height-self.height/2):
        self.center_y = ofy
        self.ControllerToFGCoordinates()

#--------------------------------------------------------------------
  def on_touch_up(self,touch):
    if (touch.grab_current is self) and self.padactive:
      self.do_center()
      touch.ungrab(self)
      self.bindroot.grabbed['pad']={"state":"ungrabbed"}

#--------------------------------------------------------------------
  def do_center(self):
    if self.bindroot.settings['padautocenter']:
      self.center=self.parent.width/2,self.parent.height/2
      self.ControllerToFGCoordinates()

#--------------------------------------------------------------------
  def FGToControllerCoordinates(self,x,y):
    nx = self.parent.width/2*x + self.parent.width/2
    ny = self.parent.height/2*y+ self.parent.height/2
    if self.padactive:
      nx = self.parent.width/2*x + self.parent.width/2
    else:
      nx = self.parent.width/2
      self.angle = -x*30.0
    self.setposition(nx,ny)

#--------------------------------------------------------------------
  def ControllerToFGCoordinates(self):
    x,y = self.center
   
    try:  
      ny = 2/(self.parent.height)*y -1
    except:
      ny = 0

    if self.padactive:
      try:
        nx = 2/(self.parent.width)*x -1
      except:
        nx = 0
    else:
      nx = -self.angle/30.0
    
    threshold =  self.bindroot.settings['threshold']
    nx=nx/(11-float(self.bindroot.settings['aileronsensivity']))
    ny=ny/(11-float(self.bindroot.settings['elevatorsensitivy']))
    if ((abs(self.bindroot.current['aileron']-nx)>threshold) or (abs(self.bindroot.current['elevator']-ny)>threshold)):
      self.bindroot.current['aileron'] = nx
      self.bindroot.current['elevator'] = ny
      self.bindroot.update()

#--------------------------------------------------------------------
  def setposition(self,x,y):
    self.center=(x,y)

#--------------------------------------------------------------------
  def  AcclMode(self):
    self.padactive=0
    self.showpad = False

#--------------------------------------------------------------------
  def PadMode(self):
    self.padactive=1
    self.showpad = True
    

'''
   class ThrootleKnob
'''
class ThrootleKnob(Widget):
  bindroot = None
  item = None
  toffsety = None

#--------------------------------------------------------------------
  def on_touch_down(self,touch):
    if self.collide_point(*touch.pos):
      tx,ty = touch.pos
      self.toffsety = self.center_y - ty
      touch.grab(self)
      if self.bindroot.settings['throttleancor']:
        self.bindroot.grabbed['throttleleft']={"state":"grabbed"}
        self.bindroot.grabbed['throttleright']={"state":"grabbed"}
      else:
        self.bindroot.grabbed[self.item]={"state":"grabbed"}

#--------------------------------------------------------------------
  def on_touch_move(self,touch):
    if touch.grab_current is self:
      tx,ty=touch.pos
      ofy = ty + self.toffsety
      if (ofy>=self.parent.height*0.08) and (ofy<=self.parent.height*0.92):
        self.center_y=ofy
        a=self.parent.height*0.09
        b=self.parent.height*(0.90-0.09)
        self.bindroot.current[self.item]=(self.center_y-a)/b
        self.checkancored(self.bindroot.current[self.item])
        self.bindroot.update()

#--------------------------------------------------------------------
  def on_touch_up(self,touch):
    if touch.grab_current is self:
      a=self.parent.height*0.09
      b=self.parent.height*(0.90-0.09)
      y=(self.center_y-a)*20/b
      self.center_y= int(y)*b/20+a
      self.bindroot.current[self.item] = int(y)/20.0
      self.checkancored(self.bindroot.current[self.item])
      self.bindroot.update()
      touch.ungrab(self)
      if self.bindroot.settings['throttleancor']:
        self.bindroot.grabbed['throttleleft']={"state":"ungrabbed"}
        self.bindroot.grabbed['throttleright']={"state":"ungrabbed"}
      else:
        self.bindroot.grabbed[self.item]={"state":"ungrabbed"}

#--------------------------------------------------------------------
  def toController(self,value):
    a=self.parent.height*0.09
    b=self.parent.height*(0.90-0.09)
    self.center_y = (value)*b+a
    self.bindroot.current[self.item]=float(value)

#--------------------------------------------------------------------
  def checkancored(self,value):
    if self.bindroot.settings['throttleancor']:
      if self.item=="throttleleft":
        self.bindroot.throttleright.toController(value)
      else:
        self.bindroot.throttleleft.toController(value)


'''
   class SpeedBrakeKnob
'''
class SpeedBrakeKnob(Widget):

  bindroot = None
  toffsety = None

#--------------------------------------------------------------------
  def on_touch_down(self,touch):
    if self.collide_point(*touch.pos):
      tx,ty = touch.pos
      self.toffsety = self.center_y - ty
      touch.grab(self)
      self.bindroot.grabbed['speedbrake']={"state":"grabbed"}

#--------------------------------------------------------------------
  def on_touch_move(self,touch):
    if touch.grab_current is self:
      tx,ty=touch.pos
      ofy = ty + self.toffsety
      if (ofy>=self.parent.height*0.20) and (ofy<self.parent.height*0.87):
        self.center_y=ofy

#--------------------------------------------------------------------
  def on_touch_up(self,touch):
    if touch.grab_current is self:
      if (self.center_y<=self.parent.height*0.5):
        #down
        self.center_y=self.parent.height*0.20
        self.bindroot.current['speedbrake']=2
        self.bindroot.setFG('/controls/flight/speedbrake-lever',2)
      elif(self.center_y<=self.parent.height*0.8):
        #armed
        self.center_y=self.parent.height*0.75
        self.bindroot.current['speedbrake']=2
        self.bindroot.setFG('/controls/flight/speedbrake-lever',1)
      else:
        #up
        self.center_y=self.parent.height*0.87
        self.bindroot.current['speedbrake']=2
        self.bindroot.setFG('/controls/flight/speedbrake-lever',0)
      touch.ungrab(self)
      self.bindroot.grabbed['speedbrake']={"state":"ungrabbed"}

#--------------------------------------------------------------------
  def toController(self,value):
    sw=int(value)
    if (sw==0):
      self.center_y=self.parent.height*0.87
    elif (sw==1):
      self.center_y=self.parent.height*0.75
    else:
      self.center_y=self.parent.height*0.20

    self.bindroot.current['speedbrake']=float(value)


'''
   class RudderKnob
'''
class RudderKnob(Widget):

  bindroot = None
  toffsetx = None

#--------------------------------------------------------------------
  def __init__(self,**kwargs):
    super(RudderKnob, self).__init__(**kwargs)

#--------------------------------------------------------------------
  def on_touch_down(self,touch):
    if self.collide_point(*touch.pos):
      tx,ty = touch.pos
      self.toffsetx = self.center_x - tx
      touch.grab(self)
      self.bindroot.grabbed['rudder']={"state":"grabbed"}

#--------------------------------------------------------------------
  def on_touch_move(self,touch):
    if touch.grab_current is self:
      xref = self.parent.width
      tx,ty=touch.pos
      ofx = tx + self.toffsetx
      if (ofx>=xref*0.05) and (ofx<=xref*0.95):
        self.center_x=ofx
        self.update()

#--------------------------------------------------------------------
  def on_touch_up(self, touch):
    if touch.grab_current is self:
      if self.bindroot.settings['rudderautocenter']:
        self.docenter()
        self.update()
      elif abs(self.center_x-self.parent.width*0.5)<23:
        self.docenter()
        self.update()
      touch.ungrab(self)
      self.bindroot.grabbed['rudder']={"state":"ungrabbed"}

#--------------------------------------------------------------------
  def update(self):
    xref = self.parent.width
    xmax = xref*0.9
    xmiddle = xref/2.0
    # y [-1,1]
    y = 2*((self.center_x-xmiddle)/xmax)
    #cubic
    if self.bindroot.settings['smoothrudder']:
      if y>=0:
        y=pow(y,1.6)
      else:
        y=-pow(-y,1.6)
    self.bindroot.current['rudder'] = y
    self.bindroot.update() 

#--------------------------------------------------------------------
  def toController(self,value):
    y = float(value)
    if self.bindroot.settings['smoothrudder']:
      if y>=0:
        y=pow(y,1.6)
      else:
        y=-pow(-y,1.6)
    xref = self.parent.width
    xmax = xref*0.9
    xmiddle = xref/2.0
    x =  y*xmax/2 + xmiddle
    self.center_x = x
    self.bindroot.current['rudder'] = y

#--------------------------------------------------------------------
  def docenter(self):
    self.center_x=self.parent.width*0.5

  
'''
   class BrakesKnob
'''
class BrakesKnob(Widget):

  bindroot = None
  toffsetx = None

#--------------------------------------------------------------------
  def __init__(self,**kwargs):
    super(BrakesKnob, self).__init__(**kwargs)

#--------------------------------------------------------------------
  def on_touch_down(self,touch):
    if self.collide_point(*touch.pos):
      tx,ty = touch.pos
      self.toffsetx = self.center_x - tx
      touch.grab(self)
      self.bindroot.grabbed['brakes']={"state":"grabbed"}

#--------------------------------------------------------------------
  def on_touch_move(self,touch):
    if touch.grab_current is self:
      xref = self.parent.width
      tx,ty=touch.pos
      ofx = tx + self.toffsetx
      if (ofx>=xref*0.1) and (ofx<=xref*0.90):
        self.center_x=ofx
        self.update()

#--------------------------------------------------------------------
  def on_touch_up(self, touch):
    if touch.grab_current is self:
      if self.bindroot.settings['brakesautodisable']:
        self.do_disable()
        self.update()
      touch.ungrab(self)
      self.bindroot.grabbed['brakes']={"state":"ungrabbed"}

#--------------------------------------------------------------------
  def update(self):
    xref = self.parent.width
    xmax = xref*0.8
    xoffset = xref*0.1
    y = (self.center_x-xoffset)/xmax 
    self.bindroot.current['brakes'] = y
    self.bindroot.update() 

#--------------------------------------------------------------------
  def do_disable(self):
    self.bindroot.current['brakes'] = 0
    xref = self.parent.width
    self.center_x = xref*0.15
    self.update()

#--------------------------------------------------------------------
  def toController(self,value):
    y = float(value)
    xref = self.parent.width
    xmax = xref*0.9
    xoffset = xref*0.05
    self.center_x = y*xmax - xoffset 
    self.bindroot.current['brakes']=y


'''
   class FlapsKnob
'''
class FlapsKnob(Widget):

  trans_flaps = [{'CT':0.125,'FG':1}, #30
         {'CT':0.218,'FG':0.833},     #25
         {'CT':0.312,'FG':0.666},     #20
         {'CT':0.406,'FG':0.5},       #15
         {'CT':0.5 ,'FG':0.166},      #5
         {'CT':0.594 ,'FG':0.033},    #1
         {'CT':0.875,'FG':0}          #UP
        ]

  bindroot = None
  toffsety = None

#--------------------------------------------------------------------
  def on_touch_down(self,touch):
    if self.collide_point(*touch.pos):
      tx,ty = touch.pos
      self.toffsety = self.center_y - ty
      touch.grab(self)
      self.bindroot.grabbed['flaps']={"state":"grabbed"}

#--------------------------------------------------------------------
  def on_touch_move(self,touch):
    if touch.grab_current is self:
      tx,ty=touch.pos
      ofy = ty + self.toffsety
      if (ofy>=self.parent.height*0.11) and (ofy<self.parent.height*0.89):
        self.center_y=ofy

#--------------------------------------------------------------------
  def on_touch_up(self,touch):
    if touch.grab_current is self:
      yref=self.parent.height
      if (self.center_y<yref*0.17):
        #Flaps 30
        self.center_y=yref*self.trans_flaps[0]['CT']
        self.toFG(0)

      elif (self.center_y<yref*0.264):
        #Flaps 25
        self.center_y=yref*self.trans_flaps[1]['CT']
        self.toFG(1)

      elif (self.center_y<yref*0.360):
        #Flaps 20
        self.center_y=yref*self.trans_flaps[2]['CT']
        self.toFG(2)

      elif (self.center_y<yref*0.452):
        #Flaps 15
        self.center_y=yref*self.trans_flaps[3]['CT']
        self.toFG(3)

      elif (self.center_y<yref*0.548):
        #Flaps 5
        self.center_y=yref*self.trans_flaps[4]['CT']
        self.toFG(4)

      elif (self.center_y<yref*0.737):
        #Flaps 1
        self.center_y=yref*self.trans_flaps[5]['CT']
        self.toFG(5)

      else:
      # UP
        self.center_y=yref*self.trans_flaps[6]['CT']
        self.toFG(6)

      touch.ungrab(self)
      self.bindroot.grabbed['flaps']={"state":"ungrabbed"}

#--------------------------------------------------------------------
  def toFG(self,pos):
    self.bindroot.setFG("/controls/flight/flaps",self.trans_flaps[pos]['FG'])

#--------------------------------------------------------------------
  def toText(self,pos):
    return self.trans_flaps[pos]['UI']

#--------------------------------------------------------------------
  def toController(self,value):
    target = float(value)
    #get all values from key FG
    L=map(lambda d: d['FG'], self.trans_flaps)
    # get the closest value from list L
    cv=min(range(len(L)), key=lambda i: abs(L[i]-target))
    #apply the index to slider flaps
    self.center_y=self.parent.height*self.trans_flaps[cv]['CT']
    self.bindroot.current['flaps']=target

#--------------------------------------------------------------------
  def doEnable(self,enable):
    if enable:
      self.opacity = 1
      self.disabled = False
    else:
      self.opacity = 0
      self.disabled = True


