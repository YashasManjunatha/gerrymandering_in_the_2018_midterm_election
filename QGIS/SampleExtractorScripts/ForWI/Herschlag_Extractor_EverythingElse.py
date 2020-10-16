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
FPATH = '/Users/g/Projects/WI_AmicusBrief/WIExtractedData'
LAYER_NAME = '2012_2020_Wisconsin_Election_Data_with_2017_Wards'
#LAYER_NAME = 'TESTFILE'
#Choose a marker to identify the outputs. All files outputted will then be of the form MARKERxxxx.txt
MARKER = 'Wards'
SLASH = '/' #for macs, set SLASH = '/'; for windows '\\'

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
farea   = open(FPATH+SLASH+MARKER+'AREAS.txt',      "w")
fblack  = open(FPATH+SLASH+MARKER+'BLACKS.txt',     "w")
fcounty = open(FPATH+SLASH+MARKER+'COUNTYFIPS.txt', "w")
fhisp   = open(FPATH+SLASH+MARKER+'HISPANICS.txt',  "w")
flatlong= open(FPATH+SLASH+MARKER+'LATLONG.txt',    "w")#5
fpop    = open(FPATH+SLASH+MARKER+'POPULATION.txt', "w")
ftowns  = open(FPATH+SLASH+MARKER+'TOWNSHIPS.txt',  "w")

amtDone = 0
noUnNamedTowns = 0
for f in feature_dict.values():
    idNum     = f.id()
    print 'progress on non-voting data: ', float(amtDone)/float(len(feature_dict))*100
    #print idNum, f["OBJECTID"]
    #print "NAME",f["NAME"]
    amtDone  += 1
    geom_f    = f.geometry()
    farea.write  ('\t'.join([str(int(f.id()+1)),str(f.geometry().area())]))
    fblack.write ('\t'.join([str(int(f.id()+1)),str(int(f["BLACK"]))]))
    fcounty.write('\t'.join([str(int(f.id()+1)),str(int(f["CNTY_FIPS"]))]))
    fhisp.write  ('\t'.join([str(int(f.id()+1)),str(int(f["HISPANIC"]))]))
    flatlong.write('\t'.join([str(geom_f.centroid().asPoint()[0]),str(geom_f.centroid().asPoint()[1])]))#5
    fpop.write   ('\t'.join([str(int(f.id()+1)),str(int(f["PERSONS"]))])) 
    if f["NAME"]!=NULL:
        ftowns.write ('\t'.join([str(int(f.id()+1)),f["NAME"]]))
    else:
        ftowns.write ('\t'.join([str(int(f.id()+1)),"NOTINTOWNSHIP"+str(noUnNamedTowns)]))
        noUnNamedTowns+=1
    
    farea.write("\n")
    fblack.write("\n")
    fcounty.write("\n")
    fhisp.write("\n")
    flatlong.write("\n")#5
    fpop.write("\n")
    ftowns.write("\n")
    
farea.close()
fblack.close()
fcounty.close()
fhisp.close()
flatlong.close()#5
fpop.close()
ftowns.close()

print "Finished with everything but votes"#'''

#currate voting data
'''voteFileTypes = [['PRE','16'],
                 ['USS','16'],
                 ['WSA','16'],
                 ['WSS','16'],
                 ['USH','14'],
                 ['GOV','14'],
                 ['SOS','14'],
                 ['TRS','14'],
                 ['WAG','14'],
                 ['WSA','14'],
                 ['CDA','12'],
                 ['GOV','12'],
                 ['PRE','12'],
                 ['USH','12'],
                 ['USS','12'],
                 ['WAG','12'],
                 ['WSA','12'],
                 ['WSS','12']]
amtDone = 0
for voteFileType in voteFileTypes:
    fvotes = open(FPATH+SLASH+MARKER+"VOTES"+voteFileType[0]+voteFileType[1]+".txt","w")
    print 'progress on voting data: ', float(amtDone)/float(len(voteFileTypes))*100
    amtDone+=1
    for f in feature_dict.values():
        idNum     = f.id()
        totVotes  = int(f[voteFileType[0]+"TOT"+voteFileType[1]])
        demVotes  = int(f[voteFileType[0]+"DEM"+voteFileType[1]])
        repVotes  = int(f[voteFileType[0]+"REP"+voteFileType[1]])
        fnd = False; ind = 2
        while not fnd:
            try:
                dv_other = int(f[voteFileType[0]+"DEM"+str(ind)+voteFileType[1]])
                demVotes+=dv_other
                ind     +=1
            except:
                fnd = True
        fnd = False; ind = 2
        while not fnd:
            try:
                rv_other = int(f[voteFileType[0]+"REP"+str(ind)+voteFileType[1]])
                repVotes+=rv_other
                ind     +=1
            except:
                fnd = True
        indVotes = totVotes - demVotes - repVotes
        fvotes.write('\t'.join([str(int(f.id()+1)),str(demVotes),str(repVotes),str(indVotes)]))
        fvotes.write("\n")
    fvotes.close()

print "Finished"#'''