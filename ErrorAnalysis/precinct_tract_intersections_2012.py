import qgis
import csv

from PyQt4.QtCore import *
from qgis.core import *

threshold = 10**-3

layers = qgis.utils.iface.legendInterface().layers()
for layer in layers:
    if layer.name() == "SBE_PRECINCTS_09012012":
        precinct = layer
        print("found precinct layer")
    elif layer.name() == "tl_2017_37_tract":
        tract = layer
        print("found tract layer")


tr = QgsCoordinateTransform(precinct.crs(), tract.crs())
precinct_feature_dict = {d.id(): d for d in precinct.getFeatures()}
tract_feature_dict = {d.id(): d for d in tract.getFeatures()}

index = QgsSpatialIndex()
for t in tract.getFeatures():
	index.insertFeature(t)

print("created dictionaries and spatial index")

outputRows = []
for pid in precinct_feature_dict:
    #feat.geometry().transform(tr)
    p_feat = precinct_feature_dict[pid]
    p_geom = p_feat.geometry()
    p_geom.transform(tr)
    intersecting_tracts = index.intersects(p_geom.boundingBox())
    for tid in intersecting_tracts:
    	t_feat = tract_feature_dict[tid]
    	t_geom = t_feat.geometry()
    	union = t_geom.combine(p_geom)
    	ratio = (t_geom.area()+p_geom.area()-union.area())/(p_geom.area())
    	if ratio > threshold:
    		outputRows.append([p_feat["PREC_ID"], t_feat["GEOID"], ratio])
            print(p_feat["PREC_ID"])

print("found intersections")
outFile = "C:/Users/Mitra Kiciman/Documents/gerrymanderingimpact/nc_precinct_tract_splits_2012.csv"

with open(outFile, "w") as file:
	writer = csv.writer(file, lineterminator="\n")
	writer.writerow(["Precinct", "Tract", "Area"])
	for row in outputRows:
		writer.writerow(row)

print("wrote output")
