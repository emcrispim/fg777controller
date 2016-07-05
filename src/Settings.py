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

'''
   class Settings
'''
class Settings(Popup):

	bindroot = ObjectProperty(None)

#--------------------------------------------------------------------

	def __init__(self, **kwargs):
		super(Settings, self).__init__(**kwargs)

#--------------------------------------------------------------------
	def on_open(self):
		config = self.bindroot.app.config

		self.ids.ip.text=config.get("Settings","ip")
		self.ids.outgoingport.text=config.get("Settings","outgoingport")
		self.ids.incomingport.text=config.get("Settings","incomingport")
		self.ids.telnetport.text=config.get("Settings","telnetport")
		self.ids.elevatorsensitivy.value=config.getint("Settings","elevatorsensitivy")
		self.ids.aileronsensivity.value=config.getint("Settings","aileronsensivity")
		self.ids.threshold.value=float(config.get("Settings","threshold"))
		self.ids.padautocenter.active=config.getint("Settings","padautocenter")
		self.ids.rudderautocenter.active=config.getint("Settings","rudderautocenter")
		self.ids.smoothrudder.active=config.getint("Settings","smoothrudder")
		self.ids.brakesautodisable.active=config.getint("Settings","brakesautodisable")
		self.ids.throttleancor.active=config.getint("Settings","throttleancor")		
		self.ids.ctrltimedisabled.text=config.get("Settings","ctrltimedisabled")

#--------------------------------------------------------------------

	def on_dismiss(self):
		config = self.bindroot.app.config

		s ={'ip':self.ids.ip.text,
			'outgoingport':	int(self.ids.outgoingport.text),
			'incomingport':int(self.ids.incomingport.text),
			'telnetport':int(self.ids.telnetport.text),
			'elevatorsensitivy':int(self.ids.elevatorsensitivy.value),
			'aileronsensivity':int(self.ids.aileronsensivity.value),
			'threshold':self.ids.threshold.value,
			'padautocenter':int(self.ids.padautocenter.active),
			'rudderautocenter':int(self.ids.rudderautocenter.active),
			'smoothrudder':int(self.ids.smoothrudder.active),
			'brakesautodisable':int(self.ids.brakesautodisable.active),
			'throttleancor':int(self.ids.throttleancor.active),
			'ctrltimedisabled':int(self.ids.ctrltimedisabled.text)
			}
		
		config.set("Settings","ip",s['ip'])
		config.set("Settings","outgoingport",s['outgoingport'])
		config.set("Settings","incomingport",s['incomingport'])
		config.set("Settings","telnetport",s['telnetport'])
		config.set("Settings","elevatorsensitivy",s['elevatorsensitivy'])
		config.set("Settings","aileronsensivity",s['aileronsensivity'])
		config.set("Settings","threshold",s['threshold'])
		config.set("Settings","padautocenter",s['padautocenter'])
		config.set("Settings","rudderautocenter",s['rudderautocenter'])
		config.set("Settings","smoothrudder",s['smoothrudder'])
		config.set("Settings","throttleancor",s['throttleancor'])
		config.set("Settings","brakesautodisable",s['brakesautodisable'])
		config.set("Settings","ctrltimedisabled",s['ctrltimedisabled'])	
		config.write()
		self.bindroot.settings=s



