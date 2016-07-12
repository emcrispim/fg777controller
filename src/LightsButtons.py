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
from kivy.clock import Clock 

'''
	 class LightsButtons
'''
class LightsButtons(BoxLayout):
	
	binroot = None
	vibrate = False
	current = 0

	data = {'BEACON': {'key':'/controls/lighting/beacon',
								 'down' :'true',
								 'normal':'false',
								 'current':'false'
					},
					'NAV': {'key':'/controls/lighting/nav-lights',
								 'down' :'true',
								 'normal':'false',
								 'current':'false'
					},
					'LOGO': {'key':'/controls/lighting/logo-lights',
								 'down' :'true',
								 'normal':'false',
								 'current':'false'
					},
					'WING': {'key':'/controls/lighting/wing-lights',
								 'down' :'true',
								 'normal':'false',
								 'current':'false'
					},
					'STROBE': {'key':'/controls/lighting/strobe',
								 'down' :'true',
								 'normal':'false',
								 'current':'false'
					},
					'TAXI': {'key':'/controls/lighting/taxi-lights',
								 'down' :'true',
								 'normal':'false',
								 'current':'false'
					},
					'LANDING': {'key':'/controls/lighting/landing-light',
								 'key1':'/controls/lighting/landing-light[1]',
								 'key2':'/controls/lighting/landing-light[2]',
								 'down' :'true',
								 'normal':'false',
								 'current':'false'
					}

	}

#--------------------------------------------------------------------

	def init(self,bindroot):
		self.bindroot = bindroot
		self.vibrate = bindroot.vibrate


#--------------------------------------------------------------------
	def toggle(self,state,item):
		if self.vibrate:
			vibrator.vibrate(0.05)
		self.data[item]['current'] = self.data[item][state]
		self.bindroot.setFG(self.data[item]['key'],self.data[item][state])
		if item == 'LANDING':
			self.bindroot.setFG(self.data[item]['key2'],self.data[item][state])
			self.bindroot.setFG(self.data[item]['key1'],self.data[item][state])


#--------------------------------------------------------------------

	def doEnable(self,enable):
		if enable:
			self.opacity=1
			self.size_hint=(1,1)
			self.disabled = False
			Clock.schedule_once(self.toController, 0)
		else:
			self.size_hint=(None,None)
			self.size=(0,0)
			self.disabled = True
			self.opacity=0


#--------------------------------------------------------------------

	def toController(self,dt):
		data = self.bindroot.lsFG("/controls/lighting")
		if data:
			data = data.split("\r\n")
			rep = {'beacon':'BEACON',
						 'nav-lights':'NAV',
						 'logo-lights':'LOGO',
						 'wing-lights':'WING',
						 'strobe':'STROBE',
						 'taxi-lights':'TAXI',
						 'landing-light':'LANDING'}

			for l in data:
				item = l.split('\t')[0].split(" ")[0]
				if rep.has_key(item):
					fname = rep[item]
					value = l.split('\t')[1].replace("'",'')
					if self.data[fname]['current']!=value:
						self.ToggleFromFG(fname,value)


#--------------------------------------------------------------------

	def ToggleFromFG(self,item,value):
		self.data[item]['current'] = value
		if self.data[item]['down'] == value:
			self.ids[item].state = 'down'
		else:
			self.ids[item].state = 'normal'

