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

LAYER_NAME = '2012_2020_Wisconsin_Election_Data_with_2017_Wards'

#Get the ward layer
layers = qgis.utils.iface.legendInterface().layers()
for layerQ in layers:
    if layerQ.name() == LAYER_NAME:
        layer=layerQ

layer.startEditing()
if not "ASMSIM" in [field.name() for field in layer.pendingFields()]:
    print "adding layer"
    layer.dataProvider().addAttributes([QgsField("ASMSIM", QVariant.Int),])
    layer.updateFields()

#Create a dictionary of all features
feature_dict = {f.id(): f for f in layer.getFeatures()}
print layer.dataProvider().fieldNameIndex("ASM")
print layer.dataProvider().fieldNameIndex("ASMSIM")
fieldIndex = layer.dataProvider().fieldNameIndex("ASMSIM")


#first use the existing data to populate what we know
districtFile = open("/Users/g/Projects/WI_AmicusBrief/districtMapOld.txt","r")
for f in feature_dict.values():
    dist = map(int,districtFile.readline().rstrip().split())[0]
    layer.changeAttributeValue(f.id(),fieldIndex,dist)
    #print f.id(), dist
districtFile.close()
layer.commitChanges()

print "Finished creating ASMSIM"

