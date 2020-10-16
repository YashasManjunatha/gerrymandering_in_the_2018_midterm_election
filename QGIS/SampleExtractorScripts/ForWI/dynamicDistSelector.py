from qgis.utils import iface
from PyQt4.QtCore import QVariant
import numpy
import csv
import os
import shutil
import processing
from qgis.core import *
from qgis.analysis import *
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.gui import *
from qgis.utils import *
from glob import glob
import time

projDir = "/Users/g/Projects/WI_AmicusBrief/"
#outDir  = "out/PopCompOnlyKaluza8_11/out_p1K_comp1em3_H20KL20K_combined/districtmaps/"
#outDir = "out/PopCompCountyKepler8_12/out_p1K_county0p1_comp0p25_H20KL20K_1normComp/WICuratedData_2575247ALLNEW/districtmaps/"
outDir = "out/WICurrent/districtmaps/"
distSearchDirectory = ''.join([projDir,outDir])
distFileStrings = glob(''.join([distSearchDirectory,"*"]))
runInds = []

print "No files found: ", len(distFileStrings)

for distFileString in distFileStrings:
	indexString = distFileString[(len(distSearchDirectory)+len("districtMap")):-len(".txt")]	
	runInds.append(int(indexString))
runInds.sort()

# load in the map
mapOldIndToNew = []
mapFile = open(''.join([projDir,"WICuratedData/WardsToSuperWards.txt"]))
for line in mapFile:
	mapOldIndToNew.append(int(line.split("\t")[1])-1)
mapFile.close()

#Get the ward layer
LAYER_NAME = '2012_2020_Wisconsin_Election_Data_with_2017_Wards'
layers = qgis.utils.iface.legendInterface().layers()
for layerQ in layers:
    if layerQ.name() == LAYER_NAME:
        layer=layerQ
#Create a dictionary of all features
feature_dict = {f.id(): f for f in layer.getFeatures()}
fieldIndex = layer.dataProvider().fieldNameIndex("ASMSIM")

quit_huh = False
while not quit_huh:
	inputStr = QInputDialog.getText(None,"",''.join(["input district in range [0-",
	                                                 str(len(runInds)-1),"];\n",
	                                                 " a #1 #2 to animate for #2 steps starting at #1;\n",
	                                                 " q to quit;"]))#
	splitInput = inputStr[0].split()
	print splitInput
	if splitInput[0]=="q":
		print "quitting..."
		quit_huh = True	
	elif splitInput[0]=="a":
		try: 
			[startInd,noSteps] = map(int,splitInput[1:])
		except:
			startInd = -1
			noSteps  = -1
		if startInd>=0 and startInd+noSteps<len(runInds):
			print "animating..."
			for ind in range(startInd,startInd+noSteps):
				print ind
				getDistrictingStr = ''.join([projDir,outDir,"districtMap",
				                         str(runInds[ind]),".txt"])
				#print getDistrictingStr
				districting = []
				distFile = open(getDistrictingStr,"r")
				for line in distFile:
					districting.append(int(line.split("\t")[1]))
				distFile.close()
				#edit the ASMSIMS
				layer.startEditing()
				for fid in range(len(mapOldIndToNew)):
					layer.changeAttributeValue(fid,fieldIndex,districting[mapOldIndToNew[fid]],0)
				layer.commitChanges()
				time.sleep(1)
		else:
			print "Invalid input: ", inputStr[0], "... try again."
	else:
		try:
			ind = int(splitInput[0])
		except:
			ind = -1
		if ind>=0 and ind<len(runInds):
			print "Changing ASM..."
			print runInds[ind]
			getDistrictingStr = ''.join([projDir,outDir,"districtMap",
				                         str(runInds[ind]),".txt"])
			#print getDistrictingStr
			districting = []
			distFile = open(getDistrictingStr,"r")
			for line in distFile:
				districting.append(int(line.split("\t")[1]))
			distFile.close()
			#edit the ASMSIMS
			layer.startEditing()
			for fid in range(len(mapOldIndToNew)):
				layer.changeAttributeValue(fid,fieldIndex,districting[mapOldIndToNew[fid]],0)
			layer.commitChanges()
		else:
			print "Invalid input: ", inputStr[0], "... try again."#'''
