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

def tractCountyIntersects(stateFP):
	tracts = {}
	currentTract = "tl_2017_%s_tract" % stateFP
	currentTractPath = tractPath + currentTract + "/" + currentTract + ".shp"
	tractLayer = qgis.utils.iface.addVectorLayer(currentTractPath, "", "ogr")
	for feature in tractLayer.getFeatures():
		tracts[feature["GEOID"]] = feature

	return tractLayer, tracts

threshold = 10**-3
impactRepoPath = "C:\Users\Mitra Kiciman\Documents\gerrymanderingimpact" + "/"
atlasPath = impactRepoPath + "redistricting-atlas-data/"
tractPath = impactRepoPath + "CensusTractData/"
state_codes = {
    'WA': '53', 'DE': '10', 'DC': '11', 'WI': '55', 'WV': '54', 'HI': '15',
    'FL': '12', 'WY': '56', 'PR': '72', 'NJ': '34', 'NM': '35', 'TX': '48',
    'LA': '22', 'NC': '37', 'ND': '38', 'NE': '31', 'TN': '47', 'NY': '36',
    'PA': '42', 'AK': '02', 'NV': '32', 'NH': '33', 'VA': '51', 'CO': '08',
    'CA': '06', 'AL': '01', 'AR': '05', 'VT': '50', 'IL': '17', 'GA': '13',
    'IN': '18', 'IA': '19', 'MA': '25', 'AZ': '04', 'ID': '16', 'CT': '09',
    'ME': '23', 'MD': '24', 'OK': '40', 'OH': '39', 'UT': '49', 'MO': '29',
    'MN': '27', 'MI': '26', 'RI': '44', 'KS': '20', 'MT': '30', 'MS': '28',
    'SC': '45', 'KY': '21', 'OR': '41', 'SD': '46'
}

#mapTypes = ["Compact", "Dem", "GOP", "MajMin", "Proportional", "Competitive", "current"]
shapeFileNames = []
mapTypes = ["Compact", "Dem", "GOP", "current"]
 
counties = {}
with open(atlasPath + "county_assignments.csv", mode = 'r') as file:
	reader = csv.reader(file)
	next(reader, None)
	for row in reader:
		if row[2] in mapTypes:
			currentMap = row[1] + "-" + row[2] +".shp"
			if currentMap not in shapeFileNames:
					shapeFileNames.append(currentMap)
					#print(currentMap)
			countyFP = row[3]			
			if len(countyFP) == 4 or len(countyFP) == 2:
				countyFP = "0" + countyFP
			elif len(countyFP) == 1:
				countyFP = "00" + countyFP
			if len(countyFP) == 3:
				stateFP = row[0]
				if len(stateFP) == 1:
					stateFP = "0" + stateFP
				countyFP = stateFP + countyFP

			if countyFP not in counties:
				counties[countyFP] = {}
			current = counties[countyFP]
			if row[2] not in current:
				current[row[2]] = []
		
			district = row[5] 
			if len(district) == 1:
				district = "0" + district
			current[row[2]].append(district)

shapeFileNames.sort()

outRows = []
prev = ""
for file in shapeFileNames:
	districtLayer = qgis.utils.iface.addVectorLayer(atlasPath + "shp/" + file, "", "ogr")
	mapType = file[3:-4]

	if prev != state_codes[file[0:2]]:
		if prev != "":
			QgsMapLayerRegistry.instance().removeMapLayer(tractLayer.id())
		tractLayer, tracts = tractCountyIntersects(state_codes[file[0:2]])
		prev = state_codes[file[0:2]]

	district_feature_dict = {d.id(): d for d in districtLayer.getFeatures()}
	index = QgsSpatialIndex()
	for d in districtLayer.getFeatures():
		index.insertFeature(d)

	for tid in tracts:
		t_feat = tracts[tid]
		if t_feat["ALAND"] == 0:
			continue

		cid = t_feat["STATEFP"] + t_feat["COUNTYFP"]
		ratios = {}
		print(cid)
		if len(counties[cid][mapType]) == 1:
			outRows.append([t_feat["STATEFP"], file[0:2], mapType, cid, t_feat["GEOID"], counties[cid][mapType][0], 1.0])
			continue
		t_geom = t_feat.geometry()

		intersections = index.intersects(t_geom.boundingBox())
		for inter in intersections:
			d_feat = district_feature_dict[inter]
			d_geom = d_feat.geometry()
			union = t_geom.combine(d_geom)
			ratio = (d_geom.area() + t_geom.area() - union.area())/t_geom.area()
			if ratio > threshold:
				ratios[d_feat["DISTRICT"]] = ratio
		total = sum(ratios.values())
		if total < 0.05:
			continue
		elif total != 1.0:
			difference = 1.0 - total
			for key in ratios:
				ratios[key] = ratios[key] + ((ratios[key]/total)*difference)
				outRows.append([t_feat["STATEFP"], file[0:2], mapType, cid, t_feat["GEOID"], key, ratios[key]])

		print(sum(ratios.values()))

	QgsMapLayerRegistry.instance().removeMapLayer(districtLayer.id())

QgsMapLayerRegistry.instance().removeMapLayer(tractLayer.id())
with open(impactRepoPath + "tract_district_splits.csv", mode = "w") as output:
	writer = csv.writer(output, lineterminator="\n")
	writer.writerow(['statefp', 'state', 'maptype', 'countyFP', 'tractID', 'district', 'percentage'])
	for row in outRows:
		writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6]])