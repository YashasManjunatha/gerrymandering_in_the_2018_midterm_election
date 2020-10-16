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
FPATH = '/Users/g/Desktop/WIData'
LAYER_NAME = '2012_2020_Wisconsin_Election_Data_with_2017_Wards'
#LAYER_NAME = 'TESTFILE'
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
    special cases by city name- harrison is in district 3
    if f["NAME"]=="Harrison" and f["CNTY_FIPS"]=="55015" and GA_dist==NULL:
        int_GA_dist = 3
        dists_found[int_GA_dist-1] = 1
        foundGADists_huh[idNum]    = 1
        GADistsByFID[idNum]        = int_GA_dist-1

print "remaining vs total: ", sum(foundGADists_huh), len(foundGADists_huh)

#special cases by ward FID
#De Pere
'''foundGADists_huh[244-1]=1;GADistsByFID[244-1]=4-1;dists_found[4-1]=1
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

#Very funky stuff:
addWard(43,[1190],foundGADists_huh,GADistsByFID,dists_found)
addWard(45,[2020],foundGADists_huh,GADistsByFID,dists_found)
addWard(47,[1063, 1064, 1066, 1068, 1069],foundGADists_huh,GADistsByFID,dists_found)
addWard(61,[2466],foundGADists_huh,GADistsByFID,dists_found)

addWard(78,[1050],foundGADists_huh,GADistsByFID,dists_found)
addWard(79,[1049, 1060, 1062, 1212, 1255, 1256, 1257, 1258],foundGADists_huh,GADistsByFID,dists_found)
addWard(85,[3074],foundGADists_huh,GADistsByFID,dists_found)
addWard(86,[3081],foundGADists_huh,GADistsByFID,dists_found)
addWard(93,[1604, 1669, 1671, 1672, 1674, 1675, 1678, 1680, 1681],foundGADists_huh,GADistsByFID,dists_found)

#will get taken care of naturally with perimeter healing:
#6796

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
            GADistsByFID[idNum]=int(ASMval)
            dists_found[int(ASMval)-1]=1
            noHealed+=1
print "Number healed because surrounded: ", noHealed

##here check population not perfectly accounted for vs total population
#totPop           = 0
#totPopNotPerfect = 0
#for idNum in range(len(feature_dict)):
#    totPop += int(feature_dict[idNum]["PERSONS"])
#    if not(foundGADists_huh[idNum]):
#        totPopNotPerfect += int(feature_dict[idNum]["PERSONS"])
#print "pop not perfect vs tot pop ", totPopNotPerfect, totPop
#
##how many left with non-zero population
#left = 0
#for idNum in range(len(feature_dict)):
#    if not(foundGADists_huh[idNum]):
#        pop =  int(feature_dict[idNum]["PERSONS"])
#        if pop>0:
#            print "still need to figure out: ", idNum+1
#            left+=1
#print "left with pop geq threshold ", left

#Niave completion:
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
        for i in range(len(ASMvals)):
            if ASMvals[i]!=NULL:
                ASMval = ASMvals[i]
        if ASMval!=NULL:
            foundGADists_huh[idNum]=1
            GADistsByFID[idNum]=int(ASMval)
            dists_found[int(ASMval)-1]=1
        else: 
            print idNum+1


#print feature_dict[1053].geometry().asPolygon()

#print "describing isolated districts..."
#noIso = 0
#for idNum in range(len(feature_dict)):
#    f       = feature_dict[idNum]
#    geom_f  = f.geometry()
#    intersecting_ids = index.intersects(geom_f.boundingBox())
#    nobdryels = 0
#    for intersecting_id in intersecting_ids:
#        if intersecting_id != idNum:
#            if myAdj(geom_f,feature_dict[intersecting_id].geometry())>0:
#                nobdryels+=1
#    if nobdryels==0:
#        noIso+=1
#        print idNum
#print "number isolated: ", noIso
#listofisodists = [63,108,402,509,718,789,793,795,825,1053,1054,1167,1210,1229,1288,1295,1333,1357,1469,1666,1744,1753,1763,1805,1812,1880,1891,1893,1942,1952,1977,1996,2064,2087,2127,2193,2200,2301,2548,2712,2726,2762,2847,2889,2925,2950,3182,3788,3804,3805,3831,3860,3863,3873,3896,4180,4197,4317,4333,4340,4421,4443,4492,4562,4624,4759,4978,4985,5011,5022,5040,5196,5206,5266,5271,5339,5363,5470,5516,5609,5633,6072,6428,6442,6543,6548,6637,6638,6683,6735,6778,6797,6890]
#noIso = 0
#for idNum in listofisodists:
#    f       = feature_dict[idNum]
#    geom_f  = f.geometry()
#    intersecting_ids = index.intersects(geom_f.boundingBox())
#    nobdryels = 0
#    for intersecting_id in intersecting_ids:
#        if intersecting_id != idNum:
#            if myAdj(geom_f,feature_dict[intersecting_id].geometry())>0:
#                nobdryels+=1
#    if nobdryels==0 and len(intersecting_ids)!=2:
#        noIso+=1
#        print idNum, len(intersecting_ids)
#print "number isolated: ", noIso
#
#geom_f = feature_dict[0].geometry()
#print dir(geom_f.boundingBox())
#print geom_f.boundingBox().asPolygon()
#print len(geom_f.boundingBox().asPolygon())
#print geom_f.boundingBox().asPolygon().split(",")[0].split(" ")
#
#2615

#heal things iteratively in a way that makes sense
#   1.) look at the ids of the boundaries with the same city name that are assigned to an ASM)
#       - assign to the ASM with the most boarder
#   2.) if there is no one above, or if the max boarder length is zero or no ASM, then look at other boarders
#   Repeat this process until a step of this algorithm dosen't progress.

#check for contiguity'''

'''#next heal only the data which is obvious
noFound = 0
for f in feature_dict.values():
    idNum     = f.id()

    if not(foundGADists_huh[idNum]):
        print idNum+1
        geom_f = f.geometry()
        intersecting_ids = index.intersects(geom_f.boundingBox())
        for intersecting_id in intersecting_ids:
            print intersecting_id+1, foundGADists_huh[intersecting_id],
            print GADistsByFID[intersecting_id]+1, myAdj(geom_f,feature_dict[intersecting_id].geometry())
        print
        noFound+=1
        #if noFound==3:
        if idNum+1==925:
            break
print noFound   '''

#if the population is zero, ensure contiguity - first look to see if any one shares the name
#idea is to find maximum amount of connecting area of district - if the "NAME" is shared with a district, 
#only count these things first


#fdist   = open(FPATH+SLASH+MARKER+'DISTRICTS.txt',  "w")

print "left to deal with ", len(foundGADists_huh)-int(sum(foundGADists_huh))

#fdist.close()


print "Finished finding districts"

