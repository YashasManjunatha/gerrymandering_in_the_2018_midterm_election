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

#Choose where to save the output files.
FPATH = '/Users/g/Projects/WI_AmicusBrief/WIExtractedData'
LAYER_NAME = '2012_2020_Wisconsin_Election_Data_with_2017_Wards'
#Choose a marker to identify the outputs. All files outputted will then be of the form MARKERxxxx.txt
MARKER = 'Wards'
SLASH = '/' #for macs, set SLASH = '/'; for windows '\\'

#v1 and v2 are lists of qgis point geometries. These ordered points define two regions by playing "connect the dots" and taking the interior
def shapeIntersect(v1,v2):
    ring1 = QgsGeometry.fromPolyline(v1)
    ring2 = QgsGeometry.fromPolyline(v2)
    to_return = 0
    if ring1.intersects(ring2):
        to_return = ring1.intersection(ring2).length()
    return to_return
def myAdj(geom1,geom2):
    #Sometimes, geometries can be multipolygons instead of polygons. We treat this case here.
    bord_len=0
    if len(geom1.asPolygon())>0:
        v1 = [geom1.asPolygon()]
    elif len(geom1.asMultiPolygon())>0:
        v1 = geom1.asMultiPolygon()
    if len(geom2.asPolygon())>0:
        v2 = [geom2.asPolygon()]
    elif len(geom2.asMultiPolygon())>0:
        v2 = geom2.asMultiPolygon()
    intpts = 0
    #v1 and v2 are now lists of point lists corresponding to the connected components of their respective geometries.
    #We loop over every connected component to find mutual boundary segments.
    for i0 in range(0,len(v1)):
        for i1 in range(0,len(v1[i0])):
            for j0 in range(0,len(v2)):
                for j1 in range(0,len(v2[j0])):
                    bord_len+=shapeIntersect(v1[i0][i1],v2[j0][j1])
    return bord_len

### Script starts here
#Get the ward layer
layers = qgis.utils.iface.legendInterface().layers()
for layerQ in layers:
    if layerQ.name() == LAYER_NAME:
        layer=layerQ

#Create a dictionary of all features
feature_dict = {f.id(): f for f in layer.getFeatures()}
foundGADists_huh = np.zeros(len(feature_dict))
GADistsByFID     = np.zeros(len(feature_dict));
dists_found      = np.zeros(200)

#Build a spatial index
index = QgsSpatialIndex()
for f in feature_dict.values():
    index.insertFeature(f)

#first use the existing data to populate what we know
for f in feature_dict.values():
    idNum     = f.id()
    geom_f    = f.geometry()
    GA_dist   = f["ASM"]
    if GA_dist!=NULL:
        int_GA_dist = int(GA_dist)
        dists_found[int_GA_dist-1] = 1
        foundGADists_huh[idNum]    = 1
        GADistsByFID[idNum]        = int_GA_dist-1
    #special cases by city name- harrison is in district 3
    if f["NAME"]=="Harrison" and f["CNTY_FIPS"]=="55015" and GA_dist==NULL:
        int_GA_dist = 3
        dists_found[int_GA_dist-1] = 1
        foundGADists_huh[idNum]    = 1
        GADistsByFID[idNum]        = int_GA_dist-1

print sum(foundGADists_huh), len(foundGADists_huh)

#special cases by ward FID
#De Pere
foundGADists_huh[244-1]=1;GADistsByFID[244-1]=4-1;dists_found[4-1]=1
foundGADists_huh[245-1]=1;GADistsByFID[245-1]=4-1;dists_found[4-1]=1
#
foundGADists_huh[547-1]=1;GADistsByFID[547-1]=68-1;dists_found[68-1]=1
#
foundGADists_huh[891-1]=1;GADistsByFID[891-1]=79-1;dists_found[79-1]=1
#Windsor
foundGADists_huh[1249-1]=1;GADistsByFID[1249-1]=42-1;dists_found[42-1]=1
foundGADists_huh[1250-1]=1;GADistsByFID[1250-1]=42-1;dists_found[42-1]=1
foundGADists_huh[1251-1]=1;GADistsByFID[1251-1]=37-1;dists_found[37-1]=1
foundGADists_huh[1252-1]=1;GADistsByFID[1252-1]=37-1;dists_found[37-1]=1
foundGADists_huh[1253-1]=1;GADistsByFID[1253-1]=37-1;dists_found[37-1]=1
foundGADists_huh[1254-1]=1;GADistsByFID[1254-1]=79-1;dists_found[79-1]=1
#Rosendale
foundGADists_huh[1842-1]=1;GADistsByFID[1842-1]=53-1;dists_found[53-1]=1
#Somers
foundGADists_huh[2512-1]=1;GADistsByFID[2512-1]=61-1;dists_found[61-1]=1
foundGADists_huh[2513-1]=1;GADistsByFID[2513-1]=61-1;dists_found[61-1]=1
foundGADists_huh[2514-1]=1;GADistsByFID[2514-1]=61-1;dists_found[61-1]=1
foundGADists_huh[2515-1]=1;GADistsByFID[2515-1]=61-1;dists_found[61-1]=1
foundGADists_huh[2522-1]=1;GADistsByFID[2522-1]=61-1;dists_found[61-1]=1
foundGADists_huh[2516-1]=1;GADistsByFID[2516-1]=64-1;dists_found[64-1]=1
foundGADists_huh[2517-1]=1;GADistsByFID[2517-1]=64-1;dists_found[64-1]=1
foundGADists_huh[2518-1]=1;GADistsByFID[2518-1]=64-1;dists_found[64-1]=1
foundGADists_huh[2519-1]=1;GADistsByFID[2519-1]=64-1;dists_found[64-1]=1
foundGADists_huh[2520-1]=1;GADistsByFID[2520-1]=64-1;dists_found[64-1]=1
foundGADists_huh[2521-1]=1;GADistsByFID[2521-1]=64-1;dists_found[64-1]=1
foundGADists_huh[2523-1]=1;GADistsByFID[2523-1]=64-1;dists_found[64-1]=1
#La Crosse
foundGADists_huh[2645-1]=1;GADistsByFID[2645-1]=94-1;dists_found[94-1]=1
foundGADists_huh[2646-1]=1;GADistsByFID[2646-1]=94-1;dists_found[94-1]=1
#Sylvan and Forest
foundGADists_huh[4796-1]=1;GADistsByFID[4796-1]=49-1;dists_found[49-1]=1
foundGADists_huh[4796-1]=1;GADistsByFID[4796-1]=49-1;dists_found[49-1]=1
#Oshkosh
foundGADists_huh[6733-1]=1;GADistsByFID[6733-1]=53-1;dists_found[53-1]=1
foundGADists_huh[6739-1]=1;GADistsByFID[6739-1]=53-1;dists_found[53-1]=1
foundGADists_huh[6742-1]=1;GADistsByFID[6742-1]=53-1;dists_found[53-1]=1
foundGADists_huh[6749-1]=1;GADistsByFID[6749-1]=53-1;dists_found[53-1]=1
foundGADists_huh[6750-1]=1;GADistsByFID[6750-1]=53-1;dists_found[53-1]=1
foundGADists_huh[6732-1]=1;GADistsByFID[6732-1]=54-1;dists_found[54-1]=1
foundGADists_huh[6735-1]=1;GADistsByFID[6735-1]=54-1;dists_found[54-1]=1
foundGADists_huh[6736-1]=1;GADistsByFID[6736-1]=54-1;dists_found[54-1]=1
foundGADists_huh[6737-1]=1;GADistsByFID[6737-1]=54-1;dists_found[54-1]=1
foundGADists_huh[6738-1]=1;GADistsByFID[6738-1]=54-1;dists_found[54-1]=1
foundGADists_huh[6740-1]=1;GADistsByFID[6740-1]=54-1;dists_found[54-1]=1
foundGADists_huh[6741-1]=1;GADistsByFID[6741-1]=54-1;dists_found[54-1]=1
foundGADists_huh[6743-1]=1;GADistsByFID[6743-1]=54-1;dists_found[54-1]=1
foundGADists_huh[6744-1]=1;GADistsByFID[6744-1]=54-1;dists_found[54-1]=1
#Vinland
foundGADists_huh[6758-1]=1;GADistsByFID[6758-1]=56-1;dists_found[56-1]=1
foundGADists_huh[6759-1]=1;GADistsByFID[6759-1]=56-1;dists_found[56-1]=1
#Winneconne
foundGADists_huh[6769-1]=1;GADistsByFID[6769-1]=56-1;dists_found[56-1]=1
foundGADists_huh[6770-1]=1;GADistsByFID[6770-1]=56-1;dists_found[56-1]=1
#Wolf River
foundGADists_huh[6772-1]=1;GADistsByFID[6772-1]=56-1;dists_found[56-1]=1
foundGADists_huh[6773-1]=1;GADistsByFID[6773-1]=56-1;dists_found[56-1]=1

def addWard(distind, wardList,fG_huh,GAbyFID,dF_huh):
    for ward in wardList:
        fG_huh[ward-1]=1
        GAbyFID[ward-1]=distind-1
        dists_found[distind-1]=1        
#forcing contiguous:
addWard(56,[4077,4078],foundGADists_huh,GADistsByFID,dists_found)
addWard(43,[4957],foundGADists_huh,GADistsByFID,dists_found)

addWard(48,[823 ],foundGADists_huh,GADistsByFID,dists_found)
addWard(76,[1074],foundGADists_huh,GADistsByFID,dists_found)
addWard(77,[1075],foundGADists_huh,GADistsByFID,dists_found)
addWard(57,[6617],foundGADists_huh,GADistsByFID,dists_found)
addWard(58,[5912],foundGADists_huh,GADistsByFID,dists_found)
addWard(23,[4218],foundGADists_huh,GADistsByFID,dists_found)
addWard(79,[1255,1256,1257,1258,890],foundGADists_huh,GADistsByFID,dists_found)
addWard(48,[834],foundGADists_huh,GADistsByFID,dists_found)
addWard(91,[1667],foundGADists_huh,GADistsByFID,dists_found)
addWard(86,[3086],foundGADists_huh,GADistsByFID,dists_found)
addWard(86,[3082],foundGADists_huh,GADistsByFID,dists_found)
addWard(85,[3074],foundGADists_huh,GADistsByFID,dists_found)

#next step is to heal all districts that are only surrounded by one assigned district
noHealed = 0
for idNum in range(len(feature_dict)):
    if not(foundGADists_huh[idNum]):
        f       = feature_dict[idNum]
        geom_f  = f.geometry()
        intersecting_ids = index.intersects(geom_f.boundingBox())
        ASMvals = []
        for intersecting_id in intersecting_ids:
            if intersecting_id != idNum:
                if myAdj(geom_f,feature_dict[intersecting_id].geometry())>0:
                    ASMvals.append(feature_dict[intersecting_id]["ASM"])
        if len(ASMvals)==0:
            if len(intersecting_ids)>1:
                #island with known nearby wards
                for intersecting_id in intersecting_ids:
                    if intersecting_id != idNum:
                        ASMvals.append(feature_dict[intersecting_id]["ASM"])
            else:
                #island that we need to search for nearby redist
                nearestIds = index.nearestNeighbor(geom_f.centroid().asPoint(),2)
                for nearestId in nearestIds:
                    if nearestId != idNum:
                        ASMvals.append(feature_dict[nearestId]["ASM"])
        ASMval = ASMvals[0]
        AllMatchAndNotNull = (ASMval!=NULL)
        for i in range(len(ASMvals)-1):
            AllMatchAndNotNull = AllMatchAndNotNull and (ASMval==ASMvals[i+1])
        if AllMatchAndNotNull:
            foundGADists_huh[idNum]=1
            GADistsByFID[idNum]=int(ASMval)-1
            dists_found[int(ASMval)-1]=1
            noHealed+=1
print "Number healed because surrounded: ", noHealed

#search the district
def breadthFirstDistrictCount(vh,nL,distList,start):
    dist = distList[start]
    searchList = [start]
    while len(searchList)>0:
        current = searchList.pop()
        vh[current]=1
        for nghb in nL[current]:
            if nghb!=-1 and distList[nghb]==dist:
                if vh[nghb]!=1:
                    searchList.append(nghb)
print "max dist: ", max(dists_found)

print "left to deal with ", len(foundGADists_huh)-int(sum(foundGADists_huh))

layer.startEditing()
#if not "ASMSIM" in [field.name() for field in layer.pendingFields()]:
#    print "adding layer"
#    layer.dataProvider().addAttributes([QgsField("ASMSIM", QVariant.Int),])
#    layer.updateFields()
#if not "CONDIST" in [field.name() for field in layer.pendingFields()]:
#    print "adding layer"
#    layer.dataProvider().addAttributes([QgsField("CONDIST", QVariant.Int),])
#    layer.updateFields()

#
unHealedDistricts = open(FPATH+SLASH+MARKER+'UNHEALEDDISTRICTING.txt', "w")
fieldIndex = layer.dataProvider().fieldNameIndex("ASMSIM")
condIndex = layer.dataProvider().fieldNameIndex("CONDIST")
for f in feature_dict.values():
    if foundGADists_huh[f.id()]:
        dist = int(GADistsByFID[f.id()]+1.1)
        layer.changeAttributeValue(f.id(),condIndex,1)
    else:
        dist = int(0)
        layer.changeAttributeValue(f.id(),condIndex,0)
    layer.changeAttributeValue(f.id(),fieldIndex,dist,0)
    #
    unHealedDistricts.write(str(dist))
    unHealedDistricts.write("\n")
layer.commitChanges()

unHealedDistricts.close()




print "Finished finding districts"#'''

