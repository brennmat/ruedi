# Python script for testing the ruediPy code
# 
#
# Copyright 2016, Matthias Brennwald (brennmat@gmail.com) and Yama Tomonaga
# 
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


# make shure Python knows where to look for the RUEDI Python code
# http://stackoverflow.com/questions/4580101/python-add-pythonpath-during-command-line-module-run
# Example (bash): export PYTHONPATH=~/ruedi/python

from classes.rgams		import rgams
from classes.selectorvalve	import selectorvalve
from classes.datafile	import datafile
import matplotlib.pyplot as plt

from datetime import datetime


# initialize instrument objects:
#VALVE     = selectorvalve('INLETSELECTVALVE','/dev/ttyUSB3')	# init VICI selector valve
#MS        = rgams('RGA-MS','/dev/ttyUSB4') 	 				# init RGA / MS
MS    = rgams('RGA-MS','/dev/serial/by-id/pci-WuT_USB_Cable_2_WT2304837-if00-port0')
VALVE = selectorvalve('INLETSELECTVALVE','/dev/serial/by-id/pci-WuT_USB_Cable_2_WT2350938-if00-port0')


DATAFILE  = datafile('~/ruedi/data') 						# init object for data files

DATAFILE.next() # start a new data file

# change valve positions:
VALVE.setpos(1,DATAFILE)
print 'Valve position is ' + str(VALVE.getpos())
VALVE.setpos(2,DATAFILE)
print 'Valve position is ' + str(VALVE.getpos())
VALVE.setpos(3,DATAFILE)
print 'Valve position is ' + str(VALVE.getpos())

# print some MS information:
print 'MS has electron multiplier: ' + MS.hasMultiplier()
print 'MS max m/z range: ' + MS.mzMax()

# change MS configuraton:
MS.setElectronEnergy(60)
print 'Ionizer electron energy: ' + MS.getElectronEnergy() + ' eV'
print 'Set ion beam to Faraday detector...'
MS.setDetector('F')
print MS.getDetector()
MS.filamentOn() # turn on with default current
print 'Filament current: ' + MS.getFilamentCurrent() + ' mA'

print 'Data output to ' + DATAFILE.name()


# get scan data:
print 'Scanning... '
MS.setGateTime(0.3) # set gate time for each reading
m,s,unit = MS.scan(38,42,15,0.5,DATAFILE)
print '...done.'

# plot scan data:
plt.plot(m,s)
plt.xlabel('m/z')
plt.ylabel('Ion current (' + unit +')')
print 'Close plot window to continue...'
# plt.ion() # turn on interactive mode (so Python does not stop until plot window is closed)
plt.show()

print 'Single mass measurements at mz = 40...'
k = 0
while k < 10:
	peak,unit = MS.peak(40,0.2,DATAFILE)
	k = k + 1
	print str(k) + ' peak = ' + str(peak) + ' ' + unit
print '...done.'

# turn off filament:
MS.filamentOff()
print 'Filament current: ' + MS.getFilamentCurrent() + ' mA'

print '...done.'
