from qgis.utils import iface
from PyQt4.QtCore import QVariant
import numpy
import csv
import os
import shutil
import processing
from qgis.core import *
from qgis.analysis import *

#Choose where to save the output files.
FPATH = '/Users/g/Projects/Wisconsin_SCOTUS/WIExtractedData'
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

#Build a spatial index
index = QgsSpatialIndex()
for f in feature_dict.values():
    index.insertFeature(f)

#Set up output files 
boarderOut = open(FPATH+SLASH+MARKER+'BORDER_LENGTHS.txt', "w")
amtDone = 0
islandsToCheck = []
print len(feature_dict)
nghbList = []
for i in range(len(feature_dict)):
    nghbList.append([])

for f in feature_dict.values():
    idNum     = f.id()
    print "progress: ", int(amtDone), " of ", len(feature_dict), " wards examined"
    amtDone  += 1
    geom_f    = f.geometry()

    # Find all features that intersect the bounding box of the current feature.
    # We use spatial index to find the features intersecting the bounding box
    # of the current feature. This will narrow down the features that we need
    # to check neighboring features.
    intersecting_ids = index.intersects(geom_f.boundingBox())
    # Initalize neighbors list and sum

    tot_int_perim_length = 0
    perimeter = -1
    for intersecting_id in intersecting_ids:
        length = myAdj(feature_dict[intersecting_id].geometry(), geom_f)
        if intersecting_id != idNum:
            tot_int_perim_length += length
            if length > 10**-12:
                out_str = '\t'.join([str(int(idNum)+1),str(int(intersecting_id)+1),str(length)])
                boarderOut.write(out_str)
                boarderOut.write('\n')
                nghbList[idNum].append(int(intersecting_id))
                #ngbListOut.write(''.join(["\t",str(int(intersecting_id)+1)]))
        else:
            perimeter = length
    # it is possible that there is some weirdness in the shapefile - if so, heal it
    if tot_int_perim_length==0:
        #we could have an island, which would be fine, we would just create zero length connections
        #one type of island will have a bounding box that intersects other wards
        #if this is the case, just create connections between these wards
        print "possible island: ", idNum+1
        islandsToCheck.append(idNum+1)
        if len(intersecting_ids)>1:
            for intersecting_id in intersecting_ids:
                if intersecting_id != idNum:
                    out_str = '\t'.join([str(int(idNum)+1),str(int(intersecting_id)+1),str(0.00000000001)])
                    boarderOut.write(out_str)
                    boarderOut.write('\n')
                    nghbList[idNum].append(int(intersecting_id))
                    nghbList[int(intersecting_id)].append(idNum)
                    #ngbListOut.write(''.join(["\t",str(int(intersecting_id)+1)]))
        else: 
            #assume we have an island and connect it to the ward with the nearest centroid
            nearestIds = index.nearestNeighbor(geom_f.centroid().asPoint(),2)
            for nearestId in nearestIds:
                if nearestId != idNum:
                    out_str = '\t'.join([str(int(idNum)+1),str(int(nearestId)+1),str(0.00000000001)])
                    boarderOut.write(out_str)
                    boarderOut.write('\n')
                    nghbList[idNum].append(int(nearestId))
                    nghbList[int(nearestId)].append(idNum)
                    #ngbListOut.write(''.join(["\t",str(int(nearestId)+1)]))
    boarder_length = perimeter - tot_int_perim_length
    if abs(boarder_length/perimeter) > 10**-8:
        out_str = '\t'.join([str(-1),str(int(idNum)+1),str(boarder_length)])
        boarderOut.write(out_str)
        boarderOut.write('\n')
        nghbList[idNum].append(-1)
        #ngbListOut.write(''.join(["\t",str(-1)]))
    #ngbListOut.write('\n')
boarderOut.close()

ngbListOut = open(FPATH+SLASH+MARKER+'NEIGHBOR_LIST.txt', "w")
for idNum in range(len(feature_dict)):
    ngbListOut.write(str(int(idNum)+1))
    for nghbind in nghbList[idNum]:
        if nghbind!=-1:
            ngbListOut.write(''.join(["\t",str(int(nghbind)+1)]))
        else: 
            ngbListOut.write(''.join(["\t",str(-1)]))
    ngbListOut.write('\n')
ngbListOut.close()

print "possible island FIDs: ", islandsToCheck
print "Finished finding common boarders and neighbor list"
