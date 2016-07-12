
##########################################################################
# Author:               Eduardo Crispim, emcrispim@gmail.com
# Date:                 July, 2016
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
#########################################################################


__version__ = '1.0.0' #declare the app version. Will be used by buildozer

from kivy.support import install_twisted_reactor

install_twisted_reactor()


from twisted.internet import reactor
from twisted.internet import protocol
from telnetlib import Telnet
from kivy.logger import Logger 
from kivy.app import App 
from kivy.lang import Builder
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from plyer import accelerometer 
from plyer import vibrator
from kivy.clock import Clock 
from kivy.properties import  ObjectProperty
from ViewButtons import ViewButtons
from LightsButtons import LightsButtons
from Controllers import *
from Disclaimer import *
from APMenu import APMenu
from AcclPopup import AcclPopup
from Settings import Settings
from socket import socket,AF_INET,SOCK_DGRAM
from kivy.core.window import Window
from math import atan2,sqrt
from jnius import autoclass


# Set log level
Config.set('kivy', 'log_level', 'debug')
Config.write()  


# keep the screen always on
try:
	PythonActivity = autoclass('org.renpy.android.PythonActivity')
	View = autoclass('android.view.View')
	Params = autoclass('android.view.WindowManager$LayoutParams')
	PythonActivity.mActivity.getWindow().addFlags(Params.FLAG_KEEP_SCREEN_ON)
except:
	Logger.debug("jnius autoclass exception, app is not running on android")

# for PC only
#Window.size = (960, 540)


#--------------------------------------------------------------------
#                            ---GLOBALS---

			 
UPDATE_FG_RATE=20.0 #Hz

Builder.load_file('APMenu.kv')
Builder.load_file('ViewButtons.kv')
Builder.load_file('LightsButtons.kv')
Builder.load_file('Settings.kv')
Builder.load_file('Disclaimer.kv')


'''
	 class InfoPopup
'''
class InfoPopup(Popup):

	txt = ''
	bindroot = ObjectProperty(None)

#--------------------------------------------------------------------
	def __init__(self, **kwargs):
		super(InfoPopup, self).__init__(**kwargs)

#--------------------------------------------------------------------
	def on_open(self):
		self.ids.txt.text = self.txt

#--------------------------------------------------------------------
	def on_dismiss(self):
		Logger.debug("infopopup on_close")
		self.bindroot.infopopup = False


'''
	 class EchoProtocol
'''
class EchoProtocol(protocol.DatagramProtocol):


	def __init__(self,app):
		self.app = app

	def datagramReceived(self, data, (host, port)):
				self.app.handle_message(data)
				self.transport.write(data, (host, port))


'''
	 class MainUI
'''
class MainUI(BoxLayout):#the app ui
	
	app            = ObjectProperty(None)
	padctrl        = ObjectProperty(None)
	flaps          = ObjectProperty(None)
	rudder         = ObjectProperty(None)
	brakes         = ObjectProperty(None)
	speedbrake     = ObjectProperty(None)
	throttleleft   = ObjectProperty(None)
	throttleright  = ObjectProperty(None)
	elevatortrim   = ObjectProperty(None)
	autobrake      = ObjectProperty(None)
	gear           = ObjectProperty(None)
	viewbuttons    = ObjectProperty(None)
	lightsbuttons  = ObjectProperty(None)
	apmenu         = ObjectProperty(None)

	controlsFG = None
	accloffsety = 0
	initiated = False
	telnetconnected = True
	infopopup = False
	fx = 0
	fy = 0
	fz = 0
	alpha = 0.5
	settings = {}
	grabbed={}
	telnetcommand=[]
	telnetwrite = False

	current={'throttleleft':0,
					 'throttleright':0,
					 'flaps':0,
					 'elevatortrim':0,
					 'rudder':0,
					 'brakes':0,
					 'speedbrake':0,
					 'aileron':0,
					 'elevator':0,
					 'autobrake':-1,
					 'gear':1,
					 'speed':0,
					 'altitude':0,
					 'vsi':0,
					 'heading':0}


#--------------------------------------------------------------------
	def __init__(self, **kwargs):
		super(MainUI, self).__init__(**kwargs) 
		self.vibrate = True
		try:
			vibrator.exists()
		except NotImplementedError:
			self.vibrate = False

 
		self.apmenu = APMenu(vibrate=self.vibrate,bindroot=self)
		self.viewbuttons.init(self)
		self.lightsbuttons.init(self)
		self.autobrake.bindroot=self
		self.flaps.bindroot=self
		self.gear.bindroot=self
		self.speedbrake.bindroot=self
		self.throttleleft.bindroot=self
		self.throttleright.bindroot=self
		self.throttleleft.item='throttleleft'
		self.throttleright.item='throttleright'
		self.rudder.bindroot=self
		self.elevatortrim.bindroot=self
		self.brakes.bindroot=self
		self.padctrl.bindroot=self
		self.padctrl.FGToControllerCoordinates(0,0)

	 
#--------------------------------------------------------------------
	def init5(self):
		if not self.initiated:
			self.telnetconnect()
			if self.app.config.getint("Settings","disclaimer")==0:
				Logger.debug("Open Disclaimer1")
				d = Disclaimer1(bindroot=self)
				d.open()
			else:
				self.checkTelnet()

			self.UDPSock_out = socket(AF_INET,SOCK_DGRAM)
			self.rudder.docenter()
			self.elevatortrim.toController(self.current['elevatortrim'])
			self.gear.toController(self.current['gear'])
			self.flaps.toController(self.current['flaps'])
			self.speedbrake.toController(self.current['speedbrake'])
			self.throttleleft.toController(self.current['throttleleft'])
			self.throttleright.toController(self.current['throttleright'])
			Clock.schedule_interval(self.loop,0.1)
			self.initiated = True
	
	

#--------------------------------------------------------------------
# clock function callback
	def loop(self, dt):
		pop = False
		for key in self.grabbed:
			if self.grabbed[key]['state']=='ungrabbed':
				self.grabbed[key]={'state':'countdown','timer':self.settings['ctrltimedisabled']*10}
			elif self.grabbed[key]['state']=='countdown':
				self.grabbed[key]['timer']-=1
				if self.grabbed[key]['timer']<0:
					pop=key
		if pop:
			Logger.debug(key+" poped")
			self.grabbed.pop(key)

		if self.telnetwrite == False and len(self.telnetcommand)>0:
			self.telnetwrite = True
			Clock.schedule_once(self.setFGcallback, 0)


#--------------------------------------------------------------------
# clock function accelerometer callback
	def accl(self,dt):
		try:
			x = accelerometer.acceleration[0]-self.accloffsety #read the X value
			y = accelerometer.acceleration[1]  # Y
			z = accelerometer.acceleration[2] # Z
			
			self.fx = x * self.alpha + (self.fx * (1.0 - self.alpha))
			self.fy = y * self.alpha + (self.fy * (1.0 - self.alpha))
			self.fz = z * self.alpha + (self.fz * (1.0 - self.alpha))
		except:
			x = 1
			y = 1
			z = 1

		#Roll & Pitch Equations
		aileron  = atan2(self.fy, self.fz)*57.3
		elevator = atan2(-self.fx, sqrt(self.fy*self.fy + self.fz*self.fz))*57.3
		
		elevator = elevator / 45.0
		aileron = aileron / 60.0
		
		if elevator>1:
			elevator=1
		elif elevator<-1:
			elevator=-1
		if aileron>1:
			aileron=1
		elif aileron<-1:
			aileron=-1

	 
		self.padctrl.FGToControllerCoordinates(aileron,elevator)
		self.padctrl.ControllerToFGCoordinates()
 
	
#--------------------------------------------------------------------
	def update_ctrl(self,data):
		 
		controls=data.strip("\n").split(',')
		self.controlsFG = controls

		speed           =   int(float(controls[14]))
		altitude        =   int(float(controls[15])/10)
		vsi             =   int(float(controls[16])/100)
		heading         =   int(float(controls[19]))


		if self.apmenu.ctrlupdate:
			self.apmenu.toController()

		if self.current['speed']!=speed:
			self.current['speed']=speed
			self.ids.label_spd.text = 'SPD:'+str(speed)

		if self.current['altitude']!=altitude:
			self.current['altitude']=altitude
			self.ids.label_alt.text = 'ALT:'+str(altitude)+'0'


		if self.current['vsi']!=vsi:
			self.current['vsi']=vsi
			self.ids.label_vsi.text = 'VSI:'+str(vsi)+'00'

		if self.current['heading']!=heading:
			self.current['heading']=heading
			self.ids.label_hdg.text = 'HDG:'+str(heading)

		if not self.grabbed.has_key('throttleleft'):
			throttleleft    = float(controls[2])
			if self.current['throttleleft']!=throttleleft:
				self.throttleleft.toController(throttleleft)
				Logger.debug("update throttleleft from FG")

		if not self.grabbed.has_key('throttleright'):
			throttleright   = float(controls[3])
			if self.current['throttleright']!=throttleright:
				self.throttleright.toController(throttleright)
				Logger.debug("update throttleright from FG")

		if not self.grabbed.has_key('flaps'):
			flaps   = float(controls[8])
			if self.current['flaps']!=flaps:
				self.flaps.toController(flaps)
				Logger.debug("update flaps from FG")

		if not self.grabbed.has_key('elevatortrim'):
			elevatortrim   = float(controls[5])
			if self.current['elevatortrim']!=elevatortrim:
				self.elevatortrim.toController(elevatortrim)
				Logger.debug("update elevatortrim from FG")

		if not self.grabbed.has_key('rudder'):
			rudder  = round(float(controls[4]),3)
			if self.current['rudder']!=rudder:
				Logger.debug("update rudder from FG, old value %f, new value %f" %(self.current['rudder'],rudder))
				self.rudder.toController(rudder)

		if not self.grabbed.has_key('brakes'):
			brakes   = float(controls[6])
			if self.current['brakes']!=brakes:
				self.brakes.toController(brakes)
				Logger.debug("update brakes from FG")

		if not self.grabbed.has_key('speedbrake'):
			speedbrake   = float(controls[9])
			if self.current['speedbrake']!=speedbrake:
				self.speedbrake.toController(speedbrake)
				Logger.debug("update brakes from FG")

		if not self.grabbed.has_key('reverse'):
			reverse   = float(controls[7])
			if self.ids.reverse.state != self.FGToToogleButton(reverse):
				self.ids.reverse.state = self.FGToToogleButton(reverse)
				Logger.debug("update reverse from FG")

		if not self.grabbed.has_key('gear'):
			gear   = int(controls[10])
			if self.current['gear']!=gear:
				self.gear.toController(gear)
				Logger.debug("update gear from FG")

		if not self.grabbed.has_key('parkingbrake'):
			parkingbrake   = float(controls[11])
			if self.ids.parkingbrake.state != self.FGToToogleButton(parkingbrake):
				self.ids.parkingbrake.state = self.FGToToogleButton(parkingbrake)
				Logger.debug("update parkingbrake from FG")

		if self.padctrl.padactive and not self.grabbed.has_key('pad'):
				aileron  = float(controls[0])
				elevator = float(controls[1])
				if (self.current['aileron']!=aileron):
					self.current['aileron']=aileron
					self.padctrl.FGToControllerCoordinates(aileron,elevator)
					Logger.debug("update aileron from FG:"+str(aileron))

				if (self.current['elevator']!=elevator):
					self.current['elevator']=elevator
					self.padctrl.FGToControllerCoordinates(aileron,elevator)
					Logger.debug("update elevator from FG:"+str(elevator))

		if not self.grabbed.has_key('view'):
			view = int(controls[12])
			if self.viewbuttons.current!=view:
				self.viewbuttons.setControllerView(view)
				Logger.debug("update view from FG:"+str(view))

		if not self.grabbed.has_key('autobrake'):
			autobrake = int(controls[13])
			if self.current['autobrake']!=autobrake:
				self.autobrake.setController(autobrake)
				Logger.debug("update autobrake from FG:"+str(autobrake))			
			
#--------------------------------------------------------------------    
	def update(self):
			txt= "%f,%f,%f,%f,%f,%f,%f,%f\n" %(self.current['aileron'],
													 self.current['elevator'],
													 self.current['throttleleft'],
													 self.current['throttleright'],
													 self.current['rudder'],
													 self.current['elevatortrim'],
													 self.current['brakes'],
													 self.current['brakes']
													 )
			try:
				self.UDPSock_out.sendto(txt,(self.settings['ip'],self.settings['outgoingport']))
			except:
				self.showInfoPopup("Cannot open socket.\nCheck your network")


#--------------------------------------------------------------------
	def showAPMenu(self):
		if self.vibrate:
			vibrator.vibrate(0.05)  
		self.apmenu.open()

#--------------------------------------------------------------------
	def FGToToogleButton(self,value):
		if (float(value)>0.1):
			return "down"
		else:
			return "normal"

#--------------------------------------------------------------------
	def onControllerParkingBrakeChange(self,state):
		self.grabbed['parkingbrake']={"state":"grabbed"}
		if self.vibrate:
			vibrator.vibrate(0.05)
		if state=='down':
			self.setFG("/controls/gear/brake-parking",1)
		else:
			self.setFG("/controls/gear/brake-parking",0)
		self.grabbed['parkingbrake']={"state":"ungrabbed"}

#--------------------------------------------------------------------
	def onControllerReverseChange(self,state):
		self.grabbed['reverse']={"state":"grabbed"}
		if self.vibrate:
			vibrator.vibrate(0.05)
		if state=='down':
			self.current['throttleleft']=0
			self.current['throttleright']=0
			self.throttleleft.toController(0)
			self.throttleright.toController(0)
			self.update()
			self.setFG("/controls/engines/engine[0]/reverser","true")
			self.setFG("/controls/engines/engine[1]/reverser","true")

		else:
			self.current['throttleleft']=0
			self.current['throttleright']=0
			self.throttleleft.toController(0)
			self.throttleright.toController(0)
			self.update()
			self.setFG("/controls/engines/engine[0]/reverser","false")
			self.setFG("/controls/engines/engine[1]/reverser","false")

		self.grabbed['reverse']={"state":"ungrabbed"}
	
#--------------------------------------------------------------------
	def onView(self,state):
		if self.vibrate:
			vibrator.vibrate(0.05)
		if state == "down":
			self.flaps.doEnable(False)
			self.viewbuttons.doEnable(True)
			self.lightsbuttons.doEnable(False)
		else:
			self.flaps.doEnable(True)
			self.viewbuttons.doEnable(False)

#--------------------------------------------------------------------
	def onLights(self,state):
		if self.vibrate:
			vibrator.vibrate(0.05)
		if state == "down":
			self.flaps.doEnable(False)
			self.viewbuttons.doEnable(False)
			self.lightsbuttons.doEnable(True)
		else:
			self.flaps.doEnable(True)
			self.lightsbuttons.doEnable(False)

#--------------------------------------------------------------------
	def  onSetAccelerometer(self,state):
		if self.vibrate:
			vibrator.vibrate(0.05)
		if state == "down":
			p = AcclPopup(bindroot=self)
			p.open()
		else:
			accelerometer.disable()
			Clock.unschedule(self.accl)
			self.padctrl.PadMode()

#--------------------------------------------------------------------
	def doAccelerometer(self):
		self.padctrl.AcclMode()
		accelerometer.enable()

		Clock.schedule_interval(self.accl,1/UPDATE_FG_RATE)
		self.accloffsety = accelerometer.acceleration[0]

#--------------------------------------------------------------------
	def doSettings(self):
		p = Settings(bindroot=self)
		p.open()

#--------------------------------------------------------------------
	def telnetconnect(self):
		self.telnetconnected = True
		Logger.debug("Connect to telnet:%s:%d" % (self.settings['ip'],self.settings['telnetport']))
		try:
			self.telnet = Telnet(self.settings['ip'],self.settings['telnetport'],3)
		except:
			self.telnetconnected = False

#--------------------------------------------------------------------
	def checkTelnet(self):
		if not self.telnetconnected:
			self.telnetconnect()
			if not self.telnetconnected:
				self.showInfoPopup("Failed connect to FlightGear telnet. \nCheck settings") 
				return False
			else:
				return True
		else:
			return True

#--------------------------------------------------------------------
	def showInfoPopup(self,msg):
		if not self.infopopup:
			Logger.debug("show infopopup")
			p = InfoPopup(bindroot=self)
			p.txt = msg
			p.open()
			self.infopopup = True

#--------------------------------------------------------------------

	def setFGcallback(self,dt):
		#Logger.debug("telnet buffer:"+str(self.telnetcommand))
		#self.telnet.write(self.telnetcommand[0])
		#self.telnet.read_until('/> ',2)
		#self.telnetcommand.pop(0)

		for l in self.telnetcommand:
			Logger.debug(str(self.telnetcommand))
			self.telnet.write(l)
			self.telnet.read_until('/> ',2)
			self.telnetcommand.pop(0)
		#self.telnetcommand = []
		self.telnetwrite = False


#--------------------------------------------------------------------
	def setFG(self,key,value):
		if self.checkTelnet():
			Logger.debug("Arm telnet command:%s,%s"%(str(key),str(value)))
			self.telnetcommand.append("set %s %s \r\n" % (str(key),str(value)))
			#Clock.schedule_once(self.setFGcallback, 0)
			
#--------------------------------------------------------------------

	def lsFG(self,dir):
		if self.checkTelnet():
			self.telnet.write("ls %s \r\n"%dir)
			data = self.telnet.read_until('/> ',2)
			return data
		else:
			return False


'''
	 class FG777controller
'''
class FG777controller(App): #our app
	use_kivy_settings = False

#--------------------------------------------------------------------
	def build(self):
		
		reactor.listenUDP(self.config.getint("Settings","incomingport"),EchoProtocol(self))

		Window.bind(on_draw=self.ondraw)  
		self.ui = MainUI(app=self)# create the UI
		self.ui.settings['ip']=self.config.get("Settings","ip")
		self.ui.settings['outgoingport']=self.config.getint("Settings","outgoingport")
		self.ui.settings['incomingport']=self.config.getint("Settings","incomingport")
		self.ui.settings['telnetport']=self.config.getint("Settings","telnetport")
		self.ui.settings['elevatorsensitivy']=self.config.getint("Settings","elevatorsensitivy")
		self.ui.settings['aileronsensivity']=self.config.getint("Settings","aileronsensivity")
		self.ui.settings['threshold']=float(self.config.get("Settings","threshold"))
		self.ui.settings['padautocenter']=self.config.getint("Settings","padautocenter")
		self.ui.settings['rudderautocenter']=self.config.getint("Settings","rudderautocenter")
		self.ui.settings['smoothrudder']=self.config.getint("Settings","smoothrudder")
		self.ui.settings['brakesautodisable']=self.config.getint("Settings","brakesautodisable")
		self.ui.settings['ctrltimedisabled']=self.config.getint("Settings","ctrltimedisabled")
		self.ui.settings['throttleancor'] = self.config.getint("Settings","throttleancor")
		return self.ui #show it

#--------------------------------------------------------------------
	def build_config(self,config):
		config.setdefaults('Settings',{
			'IP':'0.0.0.0',
			'outgoingport':9009,
			'incomingport':9010,
			'telnetport':9000,
			'elevatorsensitivy':10,
			'aileronsensivity':10,
			'threshold':0.02,
			'padautocenter':1,
			'rudderautocenter':1,
			'smoothrudder':1,
			'brakesautodisable':1,
			'ctrltimedisabled':5,
			'throttleancor':1,
			'disclaimer':0
			})

#--------------------------------------------------------------------
	def ondraw(self,arg1):
		self.ui.init5()

#--------------------------------------------------------------------
	def open_settings(self, *largs):
		pass

#--------------------------------------------------------------------
	def handle_message(self, msg):
		self.ui.update_ctrl(msg)

#--------------------------------------------------------------------
	def on_pause(self):
		Logger.debug("FGcontroller entered in pause")
		if self.ui.ids.accl.state == "down":
			self.ui.onSetAccelerometer("normal")
			self.ui.ids.accl.state = "normal"
		# Here you can save data if needed
		return True

#--------------------------------------------------------------------
	def on_resume(self):
		Logger.debug("FGcontroller resumed")

		# Here you can check if any data needs replacing (usually nothing)
		pass



if __name__ == '__main__':
	FG777controller().run() #start our app
