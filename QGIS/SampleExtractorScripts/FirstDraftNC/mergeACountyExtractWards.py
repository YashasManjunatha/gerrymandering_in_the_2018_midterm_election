#want script to merge wards with CNTY_FIPS=55073 into a single geometry, and 
#then create a new shapefile that contains this county shape along with the 
#individual wards with CNTY_FIPS=55019

from qgis.utils import iface
from PyQt4.QtCore import QVariant
import numpy
import csv
import os
import shutil
import processing
from qgis.core import *
from qgis.analysis import *
import time

#mergeCNTY = 69

projectDir   = "/Users/g/Projects/NC_StateLeg/"
outDirStr    = projectDir+"Data/ExtractedShapeFiles/"
electionType = "StateSenate"
############
##census blocks - fine
LAYER_NAME  = 'tl_2016_37_tabblock10' 
atomicUnit  = "CensusBlocks"
countyIDStr = "COUNTYFP10"
############
##census block groups - medium
#LAYER_NAME  = 'tl_2016_37_bg' 
#atomicUnit  = "BlockGroups"
#countyIDStr = "COUNTYFP"
############
##county subdivisions - very coarse
#LAYER_NAME  = 'tl_2013_37_cousub' 
#atomicUnit  = "CountySub"
#countyIDStr = "COUNTYFP"
############

countiesAtAtomicLevel_FIPS = [51,119,183]
countiesAtAtomicLevel_Name = ["Cumberland", "Mecklenburg","Wake"]
wholeCounties_FIPS = [93,-1,69]#-1 for nothing

layers = qgis.utils.iface.legendInterface().layers()
for layerQ in layers:
	if layerQ.name() == LAYER_NAME:
		layer=layerQ



countyIndex = layer.dataProvider().fieldNameIndex(countyIDStr)

for ind in range(len(countiesAtAtomicLevel_FIPS)):
	#select atomic units with the county id to keep
	expr = QgsExpression( "\""+countyIDStr+"\"="+str(countiesAtAtomicLevel_FIPS[ind]) )
	it   = layer.getFeatures( QgsFeatureRequest( expr ) )
	ids  = [i.id() for i in it]
	print len(ids), countiesAtAtomicLevel_Name[ind]
	layer.setSelectedFeatures( ids )

	outDirectory  = outDirStr+countiesAtAtomicLevel_Name[ind]+\
	                atomicUnit+electionType+"/"
	shapeFileName = countiesAtAtomicLevel_Name[ind]+atomicUnit+electionType+".shp"
	shapeFilePath = outDirectory+shapeFileName
	if not os.path.exists(outDirectory):
		os.makedirs(outDirectory)
	
	QgsVectorFileWriter.writeAsVectorFormat( layer, shapeFilePath, 
	                                        "utf-8", layer.crs(), 
	                                        "ESRI Shapefile", 1)
	#check if the shapefile is loaded
	layerLoaded = False
	for layerQ in layers:
		if layerQ.name() == shapeFileName[:-len(".shp")]:
			layerLoaded = True
	if not layerLoaded:
		# load the new layer
		qgis.utils.iface.addVectorLayer(shapeFilePath,
		                            	shapeFileName[:-len(".shp")],
	                                   	"ogr")
		# refresh the layers list
		layers = qgis.utils.iface.legendInterface().layers()

	if wholeCounties_FIPS[ind]>0:
		for layerQ in layers:
			if layerQ.name()==shapeFileName[:-len(".shp")]:
				layerToAppend=layerQ

		newFeature      = QgsFeature()
		wholeCountyGeom = QgsGeometry.fromWkt('GEOMETRYCOLLECTION()')
		for f in layer.getFeatures():
			if int(f[countyIDStr])==int(wholeCounties_FIPS[ind]):
				wholeCountyGeom = wholeCountyGeom.combine(f.geometry())
				attributes = []
				for field in layer.pendingFields():
					attributes.append(f[field.name()])
				newFeature.setAttributes(attributes)
		newFeature.setGeometry(wholeCountyGeom)

		layerToAppend.startEditing()
		appendProvider=layerToAppend.dataProvider()
		appendProvider.addFeatures([newFeature])
		layerToAppend.commitChanges()

print "Finished"
