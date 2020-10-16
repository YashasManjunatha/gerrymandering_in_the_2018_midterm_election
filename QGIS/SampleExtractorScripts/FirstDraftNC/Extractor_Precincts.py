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
PREPATH = PPATH+'Data/ShapeFiles/Precincts'

MARKERS      = ["Wake",
                "Cumberland",
                "Mecklenburg"]
electionType  =  "StateSenate"
atomicUnit    =  "CensusBlocks"
countyField   =  "COUNTYFP10"
LAYER_NAMES   = [MARKER+atomicUnit+electionType for MARKER in MARKERS]

atomicCountyFIPs = [183,51,119]


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

#load in precinct shapefiles
for MARKER in MARKERS:
    layerLoaded = False
    for layerQ in layers:
        if MARKER.upper()+"_PRECINCTS" in layerQ.name():
            layerLoaded = True
    if not layerLoaded:
        shapeFilePath = PREPATH+SLASH+MARKER.upper()+"_PRECINCTS.kmz"
        qgis.utils.iface.addVectorLayer(shapeFilePath,
                                        MARKER.upper()+"_PRECINCTS PRECINCTS",
                                        "ogr")
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
    CNTYFIPS   = atomicCountyFIPs[ind]

    #Get the atomic layer
    layers = qgis.utils.iface.legendInterface().layers()
    for layerQ in layers:
        if layerQ.name() == LAYER_NAME:
            layer = layerQ

    #Get the precinct layer
    for layerQ in layers:
        if MARKER.upper()+"_PRECINCTS" in layerQ.name():
            layerPrecinct = layerQ

    layer.startEditing()
    #Adds a DISTRICT field to the wards layer
    fieldToAdd = "PRECINCT"
    if not fieldToAdd in [field.name() for field in layer.pendingFields()]:
        layer.dataProvider().addAttributes([QgsField(fieldToAdd, QVariant.Int)])
        layer.updateFields()
    layer.commitChanges()

    #Build a spatial index for the precincts
    index = QgsSpatialIndex()
    for p in layerPrecinct.getFeatures():
        index.insertFeature(p)
    
    #Create a dictionary of all atomic features, and another for precinct
    feature_dict = {f.id(): f for f in layer.getFeatures()}
    precinct_dict = {p.id(): p for p in layerPrecinct.getFeatures()}
    
    #Set up output files 
    layer.startEditing()
    fPrecinct = open(FPATH+SLASH+MARKER+SLASH+MARKER+'PRECINCT.txt', "w")
    for f in feature_dict.values():
        geom_f = f.geometry()
        intersecting_precincts = index.intersects(geom_f.boundingBox())
        
        if int(CNTYFIPS)!=int(f[countyField]):
            #found a whole county - set to the zero precinct
            #update shapefile
            f[fieldToAdd] = 0
            layer.updateFeature(f)
            #output
            fPrecinct.write('\t'.join([str(int(f.id()+1)),"0"]))
        else:
            areaRatios = []
            for pind in intersecting_precincts:
                p        = precinct_dict[pind]
                geom_p   = p.geometry()
                tmpUnion = geom_p.combine(geom_f)
                areaRat  = (geom_p.area()+geom_f.area()-tmpUnion.area())/geom_f.area()
                if areaRat>0:
                    areaRatios.append([areaRat,p.id()])
            maxRatio = 0
            precinct = 0
            if len(areaRatios)==0:
                print "error - no intersecting precincts found in f.id()", f.id()
                break
            for item in areaRatios:
                if item[0]>maxRatio:
                    maxRatio=item[0]
                    precinct=item[1]
            #update shapefile
            f[fieldToAdd] = precinct
            layer.updateFeature(f)
            #output
            fPrecinct.write('\t'.join([str(int(f.id()+1)),str(precinct)]))
            #
            if maxRatio<.9:
                print f.id()
        fPrecinct.write('\n')
    layer.commitChanges()
    fPrecinct.close()

print "Finished finding precincts"#'''
