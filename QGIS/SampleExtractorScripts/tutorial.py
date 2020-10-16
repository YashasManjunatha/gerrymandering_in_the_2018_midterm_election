from qgis.utils import iface
from PyQt4.QtCore import QVariant
import numpy
import csv
import os
import shutil
import processing
from qgis.core import *
from qgis.analysis import *

threshold = 10**-3
layers = qgis.utils.iface.legendInterface().layers()

districtLayerName = "AL-current"
countyLayerName = "tl_2017_us_county" 

#for seeing how to load layers that are not loaded, 
#see e.g. "SampleExtractorScripts/FirstDraftNC/Extractor_Precincts.py"

for layer in layers:
    if districtLayerName==layer.name():
        districtLayer = layer
    elif countyLayerName==layer.name():
        countyLayer = layer

county_feature_dict = {}
for cnty_feat in countyLayer.getFeatures():
    if cnty_feat['STATEFP']=="01":
        county_feature_dict[cnty_feat.id()] = cnty_feat

district_feature_dict = {d.id(): d for d in districtLayer.getFeatures()}

#Build a spatial index for the districts
index = QgsSpatialIndex()
for d in districtLayer.getFeatures():
    index.insertFeature(d)

fileOut = open("/Users/g/Projects/gerrymandering/BassConnections2018/"+
               "gerrymanderingimpact/countyAssignment.txt", "w")
for cid in county_feature_dict.keys():
    c_feat = county_feature_dict[cid]
    c_geom = c_feat.geometry()
    intersecting_districts = index.intersects(c_geom.boundingBox())

    areaRatios = []
    aT = 0

    for int_d in intersecting_districts:
        d_feat = district_feature_dict[int_d]
        d_geom = d_feat.geometry()
        tmpUnion = d_geom.combine(c_geom)
        areaRat  = (d_geom.area()+c_geom.area()-tmpUnion.area())/c_geom.area()
        if areaRat>threshold:
            areaRatios.append([areaRat,int_d])
            aT += areaRat

    fileOut.write("\t".join(["Enacted","01",str(c_feat["COUNTYFP"])]))
    for aR in areaRatios:
        if aR[0]/aT>threshold:
            d_id = aR[1]
            d_dist = district_feature_dict[d_id]["DISTRICT"]
            fileOut.write("\t("+str(aR[0]/aT)+","+str(d_dist)+")\t")
    fileOut.write("\n")

    #if c_feat["COUNTYFP"]=="103":
    #    print intersecting_districts
    #    print areaRatios
    #    break

fileOut.close()   

print "Finished splitting counties"


