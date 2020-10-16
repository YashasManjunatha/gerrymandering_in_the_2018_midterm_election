from qgis.utils import iface
from PyQt4.QtCore import QVariant
import csv
import numpy
import csv
import os
import shutil
import processing
from qgis.core import *
from qgis.analysis import *

#Replace path below with path to impact repo on your computer
impactRepoPath = "C:/Users/Mitra Kiciman/Documents/gerrymanderingimpact/"
atlasPath = impactRepoPath + "redistricting-atlas-data/"
countyFilePath = atlasPath + "county_assignments.csv"
countyShpPath = impactRepoPath + "tl_2017_us_county/tl_2017_us_county.shp"

#Replace with desired output file
outputPath = impactRepoPath + "county_district_percentages.csv"
#Load county shape file layer
countyLayer = qgis.utils.iface.addVectorLayer(countyShpPath, "", "ogr")
layers = qgis.utils.iface.legendInterface().layers()

#mapTypes = ["Compact", "Dem", "GOP", "algorithmic-compact", "current"]
mapTypes = ["Compact", "Dem", "GOP", "current"]
prevState = ""
currentMap = None

county_feature_dict = {}

for county_feat in countyLayer.getFeatures():
	if county_feat["STATEFP"] not in county_feature_dict:
		county_feature_dict[county_feat["STATEFP"]] = {}

	currentDict = county_feature_dict[county_feat["STATEFP"]]
	if "Ana" in county_feat["NAMELSAD"] and county_feat["STATEFP"] == "35":
		currentDict["Dona Ana County"] = county_feat
	else:	
		currentDict[county_feat["NAMELSAD"]] = county_feat
"""
CSV FILE KEY
0: StateFP Code
1: State 2 letter abbreviation
2: Maptype
3: CountyFP
4: CountyName
5: District Number
"""
dataList = []
with open(countyFilePath, mode='r') as file:
	reader = csv.reader(file) #creates object to read file
	next(reader, None) #skips first line (headings)
	for row in reader:
		if row[2] in mapTypes:
			if row[1] != prevState:
				#Loads current state / maptype file, deletes old one
				if currentMap != None:
					QgsMapLayerRegistry.instance().removeMapLayer(currentMap.id())

				if row[2] == "algorithmic-compact":
					statePath = atlasPath + "shp/" + row[1] + "-" + "compact-algorithm" + ".shp"
				else:
					statePath = atlasPath + "shp/" + row[1] + "-" + row[2] + ".shp"
				currentMap = qgis.utils.iface.addVectorLayer(statePath, "", "ogr")
				layers = qgis.utils.iface.legendInterface().layers()
				prevState = row[1]
				current_state_dict = county_feature_dict[row[0]]
				currentDistricts = {d["DISTRICT"]: d for d in currentMap.getFeatures()}
			
			if "La Salle" in row[4] and row[1] == "LA":
				county_geom = current_state_dict["LaSalle Parish"].geometry()
			elif "Bedford city" in row[4] and row[1] == "VA":
				continue
			else:
				county_geom = current_state_dict[row[4]].geometry()
			district = int(row[5])
			if district < 10:
				district = "0" + str(district)

			else:
				district = str(district)

			district_geom = currentDistricts[district].geometry()
			union = district_geom.combine(county_geom)
			area = (district_geom.area() + county_geom.area() - union.area())
			areaRatio = area / county_geom.area()

			if row[2] != "current":
				countyFP = row[3][len(row[3])-3:]
			else:
				countyFP = row[3]
			currentData = [row[0], row[1], row[2], countyFP, row[4], row[5], areaRatio]
			dataList.append(currentData)
			print(row[1] + row[2] + ": " + row[4] + ": " + row[5] + ": " + str(areaRatio))

with open(outputPath, mode = 'w') as output:
	writer = csv.writer(output, lineterminator="\n")
	writer.writerow(['statefp', 'state', 'maptype', 'countyFP', 'county', 'district', 'percentage'])
	for row in dataList:
		writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6]])