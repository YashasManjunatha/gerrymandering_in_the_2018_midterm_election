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
electionType =  "StateSenate"
atomicUnit   =  "CensusBlocks"
geoIDfieldnm =  "GEOID10"
LAYER_NAMES = [MARKER+atomicUnit+electionType for MARKER in MARKERS]

wholeCountyFIPS = [69,93,-1]

#load in shapefiles
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
    print "Working on map", MARKERS[ind]
    LAYER_NAME = LAYER_NAMES[ind]
    MARKER     = MARKERS[ind]
    #Get the ward layer
    layers = qgis.utils.iface.legendInterface().layers()
    for layerQ in layers:
        if layerQ.name() == LAYER_NAME:
            layer = layerQ
        
    #Create a dictionary of all features
    feature_dict = {f.id(): f for f in layer.getFeatures()}
    
    #Build a spatial index
    index = QgsSpatialIndex()
    for f in feature_dict.values():
        index.insertFeature(f)
    
    #Set up output files 
    fgeoID = open(FPATH+SLASH+MARKER+SLASH+MARKER+'GEOID.txt', "w")
    for f in feature_dict.values():
        countyFIPs=int(f[geoIDfieldnm][2:5])
        if countyFIPs==wholeCountyFIPS[ind]:
            fgeoID.write('\t'.join([str(int(f.id()+1)),str(37000+countyFIPs)]))
        else:
            fgeoID.write('\t'.join([str(int(f.id()+1)),str(f[geoIDfieldnm])]))
        fgeoID.write('\n')
    fgeoID.close()

print "Finished finding geoIDs"#'''
