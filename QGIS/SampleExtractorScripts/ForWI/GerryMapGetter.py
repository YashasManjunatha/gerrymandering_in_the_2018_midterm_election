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
outDir  = "Results/out_p2200_idealcounty0p6_comp0p8_mino100_H20KL20K/WSA12_H/"
outFile = "origGerrymanderingIndexByDistrict"

fileStr = projDir+outDir+outFile
gFile   = open(fileStr,"r")
gData   = []
for line in gFile:
	gData.append(line.split("\t"))
gFile.close()

#Get the ward layer
LAYER_NAME = '2012_2020_Wisconsin_Election_Data_with_2017_Wards'
layers = qgis.utils.iface.legendInterface().layers()
for layerQ in layers:
    if layerQ.name() == LAYER_NAME:
        layer=layerQ
#Create a dictionary of all features
feature_dict = {f.id(): f for f in layer.getFeatures()}


#print [field.name() for field in layer.pendingFields()]
#addField="GASMd"
#if not addField in [field.name() for field in layer.pendingFields()]:
layer.startEditing()
#addField="GASMd"
#if not addField in [field.name() for field in layer.pendingFields()]:
#    print "adding layer"
#    layer.dataProvider().addAttributes([QgsField(addField, QVariant.Double),])
#    layer.updateFields()
#addField="DGAd"
#if not addField in [field.name() for field in layer.pendingFields()]:
#    print "adding layer"
#    layer.dataProvider().addAttributes([QgsField(addField, QVariant.Double),])
#    layer.updateFields()
##fieldIndexASM = layer.dataProvider().fieldNameIndex("ASMSIM")
fieldIndexGD  = layer.dataProvider().fieldNameIndex("GASMd")
fieldIndexDGD = layer.dataProvider().fieldNameIndex("DGAd")

for f in feature_dict.values():
	gDataIndex = f["ASMSIM"]-1
	#print f.id(), gDataIndex, float(gData[gDataIndex][1]), float(gData[gDataIndex][2])
	layer.changeAttributeValue(f.id(),fieldIndexGD, float(gData[gDataIndex][1]))
	layer.changeAttributeValue(f.id(),fieldIndexDGD,float(gData[gDataIndex][2]))
layer.commitChanges()#'''
