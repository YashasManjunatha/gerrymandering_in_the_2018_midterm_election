from qgis.utils import iface
from PyQt4.QtCore import QVariant
import csv
import numpy
import csv
import os
import math
import shutil
import processing
from qgis.core import *
from qgis.analysis import *

def haversine(lat1, lon1, lat2, lon2):
 
  R = 6372.8 # Earth radius in kilometers
 
  dLat = math.radians(lat2 - lat1)
  dLon = math.radians(lon2 - lon1)
  lat1 = math.radians(lat1)
  lat2 = math.radians(lat2)
 
  a = math.sin(dLat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dLon/2)**2
  c = 2*math.asin(math.sqrt(a))
 
  return R * c

impactRepoPath = "C:\Users\Mitra Kiciman\Documents\gerrymanderingimpact" + "/"
tractPath = impactRepoPath + "CensusTractData/"
munPath = impactRepoPath + "tl_2018_us_uac10/tl_2018_us_uac10.shp"

munLayer = qgis.utils.iface.addVectorLayer(munPath, "", "ogr")
muns = dict()
centroids = dict()

for feat in munLayer.getFeatures():
	stateIndex = feat["NAME10"].index(",")
	state = feat["NAME10"][stateIndex+2:stateIndex+4]
	if state not in muns:
		muns[state] = dict()
		centroids[state] = dict()

	muns[state][feat["GEOID10"]] = feat
	centroids[state][feat["GEOID10"]] = feat.geometry().centroid().asPoint()
	#print(centroids[state][feat["GEOID10"]].toString())\
	#print(type(centroids[state][feat["GEOID10"]].y()))

state_codes = {
    'WA': '53', 'DE': '10', 'DC': '11', 'WI': '55', 'WV': '54', 'HI': '15',
    'FL': '12', 'WY': '56', 'NJ': '34', 'NM': '35', 'TX': '48',
    'LA': '22', 'NC': '37', 'ND': '38', 'NE': '31', 'TN': '47', 'NY': '36',
    'PA': '42', 'AK': '02', 'NV': '32', 'NH': '33', 'VA': '51', 'CO': '08',
    'CA': '06', 'AL': '01', 'AR': '05', 'VT': '50', 'IL': '17', 'GA': '13',
    'IN': '18', 'IA': '19', 'MA': '25', 'AZ': '04', 'ID': '16', 'CT': '09',
    'ME': '23', 'MD': '24', 'OK': '40', 'OH': '39', 'UT': '49', 'MO': '29',
    'MN': '27', 'MI': '26', 'RI': '44', 'KS': '20', 'MT': '30', 'MS': '28',
    'SC': '45', 'KY': '21', 'OR': '41', 'SD': '46'
}

distance = QgsDistanceArea()
crs = QgsCoordinateReferenceSystem()
outRows = []
for state in state_codes:
	currMun = muns[state]
	currCentroids = centroids[state]
	tractFile = "tl_2017_" + state_codes[state] + "_tract"
	tractLayer = qgis.utils.iface.addVectorLayer(tractPath+tractFile+"/"+tractFile+".shp", "", "ogr")
	for tract_feat in tractLayer.getFeatures():
		centroid = tract_feat.geometry().centroid().asPoint()
		print(centroid.x(), centroid.y())
		distances = []
		for c in currCentroids:
			distances.append(haversine(centroid.y(), centroid.x(), currCentroids[c].y(), currCentroids[c].x()))

		outRows.append([tract_feat["STATEFP"], state, tract_feat["COUNTYFP"], tract_feat["GEOID"], min(distances)])
		print(min(distances))

	QgsMapLayerRegistry.instance().removeMapLayer(tractLayer.id())

QgsMapLayerRegistry.instance().removeMapLayer(munLayer.id())

with open(impactRepoPath + "tract_municipality_distance_haversine.csv", mode = "w") as output:
	writer = csv.writer(output, lineterminator="\n")
	writer.writerow(['statefp', 'state', 'countyFP', 'tractID', 'distance'])
	for row in outRows:
		writer.writerow([row[0], row[1], row[2], row[3], row[4]])


