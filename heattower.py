#!/usr/bin/env python
import sys
import os
import numpy as np

# taken from Markus Dutschke https://stackoverflow.com/questions/50299172/python-range-or-numpy-arange-with-end-limit-include
def cust_range(*args, rtol=1e-05, atol=1e-08, include=[True, False]):
	"""
	Combines numpy.arange and numpy.isclose to mimic
	open, half-open and closed intervals.
	Avoids also floating point rounding errors as with
	>>> numpy.arange(1, 1.3, 0.1)
	array([1. , 1.1, 1.2, 1.3])

	args: [start, ]stop, [step, ]
		as in numpy.arange
	rtol, atol: floats
		floating point tolerance as in numpy.isclose
	include: boolean list-like, length 2
		if start and end point are included
	"""
	# process arguments
	if len(args) == 1:
		start = 0
		stop = args[0]
		step = 1
	elif len(args) == 2:
		start, stop = args
		step = 1
	else:
		assert len(args) == 3
		start, stop, step = tuple(args)

	# determine number of segments
	n = (stop-start)/step + 1

	# do rounding for n
	if np.isclose(n, np.round(n), rtol=rtol, atol=atol):
		n = np.round(n)

	# correct for start/end is exluded
	if not include[0]:
		n -= 1
		start += step
	if not include[1]:
		n -= 1
		stop -= step

	return np.linspace(start, stop, int(n))

def crange(*args, **kwargs):
	return cust_range(*args, **kwargs, include=[True, True])

def orange(*args, **kwargs):
	return cust_range(*args, **kwargs, include=[True, False])
	
   

if len(sys.argv) != 5:
	print("Usage: heattower.py </path/to/file.gcode> <max temp> <min temp> <temp step>")
	sys.exit()

#print(sys.argv)

filePath = sys.argv[1]

if not filePath.endswith(".gcode"):
	print("GCode file needs to end with \".gcode\".")
	sys.exit()

temps = [float(temp) for temp in sys.argv[2:5]]
#print(temps)
try:
	f = open(filePath, "r")
except IOError:
	print("Can't read the gcode file")

if temps[0] > temps[1]:
	temps[2] = abs(temps[2]) * (-1)
else:
	temps[2] = abs(temps[2])

tempSteps = crange(temps[0], temps[1], temps[2])

#print(tempSteps)

beforeLC = []
afterLC = []
counter = 0
while True:
	line = f.readline()
	if not line:
		break
	counter += 1
	
	if "BEFORE_LAYER_CHANGE" in line:
		beforeLC.append(counter)
	if "AFTER_LAYER_CHANGE" in line:
		afterLC.append(counter)

nLayers = len(beforeLC)

print("%s lines were read" % counter)
print("%s layers were found" % nLayers)

nLayersPerTempStep = round(len(beforeLC) / len(tempSteps))
layersTempChange = list(range(1, nLayers, nLayersPerTempStep))

print("Temperature change at every %s layers." % nLayersPerTempStep)
print("Tower temperatures:")
print(tempSteps)
print(" at these layers:")
print(layersTempChange)
#sys.exit()
#print(filePath)
f.seek(0)

adjFileName = filePath.replace(".gcode", "_temp_set.gcode")
try:
	fadj = open(adjFileName, "w+")
except IOError:
	print("File error, can't write to file")

counter = 0
layerCounter = 0
while True:
	line = f.readline()
	if not line:
		break
	counter += 1
	
	fadj.writelines(line)
	
	if "BEFORE_LAYER_CHANGE" in line:
		layerCounter += 1
		
		if layerCounter in layersTempChange:
			layerIndex = layersTempChange.index(layerCounter)
			newTemp = tempSteps[layerIndex]
			fadj.writelines("M104 S" + str(newTemp) + "\n")

fadj.close()
f.close()
