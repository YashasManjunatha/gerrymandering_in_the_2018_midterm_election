from qgis.utils import iface
from PyQt4.QtCore import QVariant
import numpy
import csv
import os
import shutil
import processing
import math
import pandas as pd
from qgis.core import *
from qgis.analysis import *

#Choose where to save the output files with FPATH
#Choose a marker to identify the outputs. 
#   All files outputted will then be of the form MARKERxxxx.txt
SLASH = '/' #for macs, set SLASH = '/'; for windows '\\'
PPATH = 'E://NC_StateLeg/'
IPATH = PPATH+'Data/ExtractedShapeFiles'
FPATH = PPATH+'Data/ExtractedData'
EXCELPATH = 'E://NC_StateLeg/Data/DataExtractionScripts/studentQGISData.xls'
MARKERS      = ["Wake",
                "Cumberland",
                "Mecklenburg"]
electionType  =  "StateSenate"
electionAbv   =  "SSEN"
atomicUnit    =  "CensusBlocks"
LAYER_NAMES   = [MARKER+atomicUnit+electionType for MARKER in MARKERS]
SUFFIX               = "STUD"
#atomicCountyFIPs = [183,51,119]

layers = qgis.utils.iface.legendInterface().layers()

#load in atomic level shapefiles
for LAYER_NAME in LAYER_NAMES:
    layerLoaded = False
    for layerQ in layers:
        if layerQ.name() == LAYER_NAME:
            layerLoaded = True
    if not layerLoaded:
        shapeFilePath = IPATH+SLASH+LAYER_NAME+SLASH+LAYER_NAME+".shp"
        qgis.utils.iface.addVectorLayer(shapeFilePath,LAYER_NAME,"ogr")
        # refresh the layers list
        layers = qgis.utils.iface.legendInterface().layers()

#create output directories if needed
for MARKER in MARKERS:
    directory = FPATH+SLASH+MARKER
    if not os.path.exists(directory):
        os.makedirs(directory)

		
#Read student excel file
studentData = pd.read_excel(EXCELPATH)
print studentData.shape[0]
geoIDBlkGrpInd = 8;
distBlkGrpInd = 164;

for ind in range(len(LAYER_NAMES)):
    LAYER_NAME = LAYER_NAMES[ind]
    MARKER     = MARKERS[ind]

    #Get the atomic layer
    layers = qgis.utils.iface.legendInterface().layers()
    for layerQ in layers:
        if layerQ.name() == LAYER_NAME:
            layer = layerQ

    #Create a dictionary of all atomic features
    feature_dict = {f.id(): f for f in layer.getFeatures()}
    

    print "Working on districting", MARKERS[ind], SUFFIX
    layer.startEditing()
    #Adds a DISTRICT field to the wards layer
    fieldToAdd = electionAbv+SUFFIX
    if not fieldToAdd in [field.name() for field in layer.pendingFields()]:
        layer.dataProvider().addAttributes([QgsField(fieldToAdd, QVariant.Int)])
        layer.updateFields()
    layer.commitChanges()
    fieldIndex = layer.dataProvider().fieldNameIndex(fieldToAdd)
    
    layer.startEditing()
    districtLabels = []
    assignedDistrict = []
    rowInTable = -1
    for f in layer.getFeatures():
        currentFID = int(f.id())
        currentGeoID = float(f["GEOID10"] )+ 0.0
        blockGroupID = int(math.floor((currentGeoID+0.0)/1000.0))
        for i in range(studentData.shape[0]):
            if blockGroupID == studentData.iat[i,geoIDBlkGrpInd]:
                rowInTable = i
                break
    
        currentDistrict = studentData.iat[rowInTable,distBlkGrpInd]
        if currentDistrict in districtLabels:
            print "FID " + str(currentFID) + " is assigned District " +str(districtLabels.index(currentDistrict))
            layer.changeAttributeValue(currentFID,fieldIndex,districtLabels.index(currentDistrict))
        else:
            layer.changeAttributeValue(currentFID,fieldIndex,len(districtLabels))
            print "FID " + str(currentFID) + " is assigned District " +str(len(districtLabels))
            districtLabels.append(currentDistrict)
    layer.commitChanges()

print "Finished finding assigning districts"#'''
