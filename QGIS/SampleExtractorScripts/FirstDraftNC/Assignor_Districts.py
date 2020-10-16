from qgis.utils import iface
from PyQt4.QtCore import QVariant
import numpy
import csv
import os
import shutil
import processing
from qgis.core import *
from qgis.analysis import *

#Choose where to save the output files with FPATH
#Choose a marker to identify the outputs. 
#   All files outputted will then be of the form MARKERxxxx.txt
SLASH = '/' #for macs, set SLASH = '/'; for windows '\\'
PPATH = '/Users/g/Projects/NC_StateLeg/'
IPATH = PPATH+'Data/ExtractedShapeFiles'
FPATH = PPATH+'Data/ExtractedData'

MARKERS      = ["Wake",
                "Cumberland",
                "Mecklenburg"]
electionType  =  "StateSenate"
electionAbv   =  "SSEN"
atomicUnit    =  "CensusBlocks"
LAYER_NAMES   = [MARKER+atomicUnit+electionType for MARKER in MARKERS]
YEARS         = [2010,2011,2017]
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
    
    for year_ind in range(len(YEARS)):
        print "Working on districting", MARKERS[ind], YEARS[year_ind]
        YEAR = YEARS[year_ind]
        dataFileWPath = FPATH+SLASH+MARKER+SLASH+MARKER+ \
                        "DIST"+electionType.upper()+str(YEAR)+".txt"
        if not os.path.exists(dataFileWPath):
            print "Not found"
            continue

        layer.startEditing()
        #Adds a DISTRICT field to the wards layer
        fieldToAdd = electionAbv+str(YEAR)[2:]
        if not fieldToAdd in [field.name() for field in layer.pendingFields()]:
            layer.dataProvider().addAttributes([QgsField(fieldToAdd, QVariant.Int)])
            layer.updateFields()
        layer.commitChanges()
        fieldIndex = layer.dataProvider().fieldNameIndex(fieldToAdd)
    
        layer.startEditing()
        fDist = open(dataFileWPath,"r")
        for line in fDist:
            splitline = line.rstrip().split("\t")
            fid = int(splitline[0])-1
            dist= int(splitline[1])
            layer.changeAttributeValue(fid,fieldIndex,dist)
        fDist.close()
        layer.commitChanges()

print "Finished finding assigning districts"#'''
