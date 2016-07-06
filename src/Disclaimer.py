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
	class Disclaimer1
'''

class Disclaimer1(Popup):

	bindroot = ObjectProperty(None)

#--------------------------------------------------------------------

	def __init__(self, **kwargs):
		super(Disclaimer1, self).__init__(**kwargs)


	def on_dismiss(self):
		if self.ids.chkbox.active:
			self.bindroot.app.config.set("Settings","disclaimer",1)
			self.bindroot.app.config.write()
		if self.bindroot.settings['ip']=='0.0.0.0':
			self.bindroot.doSettings()