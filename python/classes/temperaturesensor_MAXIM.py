# Code for the MAXIM DS1820 type temperature sensors.
# This is just a wrapper class for the pydigitemp package; you may need to install pydigitemp first. Your can run the following command to install pydigitemp: pip install https://github.com/neenar/pydigitemp/archive/master.zip
# 
# DISCLAIMER:
# This file is part of ruediPy, a toolbox for operation of RUEDI mass spectrometer systems.
# 
# ruediPy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ruediPy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with ruediPy.  If not, see <http://www.gnu.org/licenses/>.
# 
# ruediPy: toolbox for operation of RUEDI mass spectrometer systems
# Copyright (C) 2016  Matthias Brennwald
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2016, 2017, Matthias Brennwald (brennmat@gmail.com)

import numpy
import os

from classes.misc	 import misc
from digitemp.master import UART_Adapter
from digitemp.device import AddressableDevice
from digitemp.device import DS18B20

havedisplay = "DISPLAY" in os.environ
if havedisplay: # prepare plotting environment
	import matplotlib
	matplotlib.rcParams['legend.numpoints'] = 1
	matplotlib.rcParams['axes.formatter.useoffset'] = False
	# suppress mplDeprecation warning:
	import warnings
	import matplotlib.cbook
	warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)
	matplotlib.use('GTKAgg') # use this for faster plotting
	import matplotlib.pyplot as plt

class temperaturesensor_MAXIM:
	"""
	ruediPy class for MAXIM DS1820 type temperature sensors (wrapper class for pydigitemp package).
	"""


	########################################################################################################
	
	
	def __init__( self , serialport , romcode = '', label = 'TEMPERATURESENSOR' , max_buffer_points = 500 , fig_w = 6.5 , fig_h = 5):
		'''
		temperaturesensor_MAXIM.__init__( serialport , romcode, label = 'TEMPERATURESENSOR' , max_buffer_points = 500 , fig_w = 6.5 , fig_h = 5 )
		
		Initialize TEMPERATURESENSOR object (MAXIM), configure serial port / 1-wire bus for connection to DS18B20 temperature sensor chip
		
		INPUT:
		serialport: device name of the serial port for 1-wire connection to the temperature sensor, e.g. serialport = '/dev/ttyUSB3'
		romcode: ROM code of the temperature sensor chip (you can find the ROM code using the digitemp program or using the pydigitemp package). If there is only a single temperature sensor connected to the 1-wire bus on the given serial port, romcode can be left empty.
		label (optional): label / name of the TEMPERATURESENSOR object (string). Default: label = 'TEMPERATURESENSOR'
		max_buffer_points (optional): max. number of data points in the PEAKS buffer. Once this limit is reached, old data points will be removed from the buffer. Default value: max_buffer_points = 500
		fig_w, fig_h (optional): width and height of figure window used to plot data (inches)
		
		OUTPUT:
		(none)
		'''
		
		# configure 1-wire bus for communication with MAXIM temperature sensor chip
		r = AddressableDevice(UART_Adapter(serialport)).get_connected_ROMs()
		
		if r is None:
			print ('Couldn not find any 1-wire devices on ' + serialport)
		else:
			bus = UART_Adapter(serialport)
			if romcode == '':
				if len(r) == 1:
					# print ('Using 1-wire device ' + r[0] + '\n')
					self._sensor = DS18B20(bus)
					self._ROMcode = r[0]
				else:
					print ('Too many 1-wire devices to choose from! Try again with specific ROM code...')
					for i in range(1,len(r)):
						print ('Device ' + i + ' ROM code: ' + r[i-1] +'\n')
			else:
				self._sensor = DS18B20(bus, rom=romcode)
				self._ROMcode = romcode
		
		self._label = label

		# data buffer for temperature values:
		self._tempbuffer_t = numpy.array([])
		self._tempbuffer_T = numpy.array([])
		self._tempbuffer_unit = ['x'] * 0 # empty list
		self._tempbuffer_max_len = max_buffer_points
	
		# set up plotting environment
		self._has_display = havedisplay
		if self._has_display: # prepare plotting environment and figure

			# set up plotting environment
			self._fig = plt.figure(figsize=(fig_w,fig_h))
			t = 'MAXIM DS1820'
			if self._label:
				t = t + ' (' + self.label() + ')'
			self._fig.canvas.set_window_title(t)

			# set up panel for temperature history plot:
			self._tempbuffer_ax = plt.subplot(1,1,1)
			self._tempbuffer_ax.set_title('TEMPBUFFER (' + self.label() + ')',loc="center")
			plt.xlabel('Time')
			plt.ylabel('Temperature')
			self._tempbuffer_ax.hold(False)
			
			plt.ion() # enables interactive mode

			# plt.pause(0.1) # allow some time to update the plot *** DON'T SHOW THE WINDOW YET, WAIT FOR DATA PLOTTING

		if hasattr(self,'_sensor'):
			print ('Successfully configured DS18B20 temperature sensor (ROM code ' + self._ROMcode + ')' )
		else:
			self.warning('Could not initialize MAXIM DS1820 temperature sensor.')

	
	########################################################################################################


	def label(self):
		"""
		label = temperaturesensor_MAXIM.label()

		Return label / name of the TEMPERATURESENSOR object
		
		INPUT:
		(none)
		
		OUTPUT:
		label: label / name (string)
		"""
		
		return self._label

	
	########################################################################################################
		

	def temperature(self,f,add_to_tempbuffer=True):
		"""
		temp,unit = temperaturesensor_MAXIM.temperature(f)
		
		Read out current temperaure value.
		
		INPUT:
		f: file object for writing data (see datafile.py). If f = 'nofile', data is not written to any data file.
		add_to_tempbuffer (optional): flag to indicate if data get appended to temperature buffer (default=True)

		OUTPUT:
		temp: temperature value (float)
		unit: unit of temperature value (string)
		"""	

		temp = self._sensor.get_temperature()
		unit = 'deg.C'
		
		# add data to peakbuffer
		if add_to_tempbuffer:
			self.tempbuffer_add(t,T,unit)

		# write data to datafile
		if not ( f == 'nofile' ):
			# get timestamp
			t = misc.now_UNIX()
			f.write_temperature('TEMPERATURESENSOR_MAXIM',self.label(),temp,unit,t)

		return temp,unit


	########################################################################################################
	

	def warning(self,msg):
		'''
		temperaturesensor_MAXIM.warning(msg)
		
		Issue warning about issues related to operation of pressure sensor.
		
		INPUT:
		msg: warning message (string)
		
		OUTPUT:
		(none)
		'''
		
		misc.warnmessage (self.label(),msg)





	########################################################################################################
	

	def tempbuffer_add(self,t,T,unit):
		"""
		temperaturesensor_MAXIM.tempbuffer_add(t,T,unit)
		
		Add data to temperature data buffer
				
		INPUT:
		t: epoch time
		T: temperature value
		unit: unit of pressure value (char/string)
		
		OUTPUT:
		(none)
		"""
				
		self._tempbuffer_t = numpy.append( self._tempbuffer_t , t )
		self._tempbuffer_T = numpy.append( self._tempbuffer_T , T )
		self._tempbuffer_unit.append( unit )

		N = self._tempbuffer_max_len
		
		if self._tempbuffer_t.shape[0] > N:
			self._tempbuffer_t 	     = self._tempbuffer_t[-N:]
			self._tempbuffer_T 	     = self._tempbuffer_T[-N:]
			self._tempbuffer_unit        = self._tempbuffer_unit[-N:]


	########################################################################################################


	def plot_tempbuffer(self):
		'''
		temperaturesensor_MAXIM.plot_tempbuffer()

		Plot trend (or update plot) of values in temperature data buffer (e.g. after adding data)
		NOTE: plotting may be slow, and it may therefore be a good idea to keep the update interval low to avoid affecting the duty cycle.

		INPUT:
		(none)

		OUTPUT:
		(none)
		'''

		if not self._has_display:
			self.warning('Plotting of tempbuffer trend not possible (no display system available).')

		else:
			t0 = misc.now_UNIX()
			self._tempbuffer_ax.plot( self._tempbuffer_t - t0 , self._tempbuffer_T , 'ko-' , markersize = 10 )

			t0 = time.strftime("%b %d %Y %H:%M:%S", time.localtime(t0))
			self._tempbuffer_ax.set_title('TEMPBUFFER (' + self.label() + ') at ' + t0)
                        self._tempbuffer_ax.set_xlabel('Time (s)')
                        self._tempbuffer_ax.set_ylabel('Temperature ('+self._tempbuffer_unit[0]+')')

			plt.show() # update the plot
			plt.pause(0.015) # allow some time to update the plot


	########################################################################################################



