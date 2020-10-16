import csv 
import os
from advancedsplitsmunicipalities import generateModelValuesForCensusTract, convertStateCodes
import numpy as np
import statsmodels.api as sm

def parseFile(file, precinctVotes):
	file = file.read()
	rows = file.split("\n")
	for i in range(1, len(rows)):
		cols = rows[i].split("\t")
		if len(cols) == 1:
			continue
		precinctVotes[cols[0]] = (float(cols[1]), float(cols[2]))

def convertToMargins(votes):
	for tract in votes:
		demVotes = votes[tract][0]
		repVotes = votes[tract][1]
		if demVotes < 0:
			demVotes = 0
		if repVotes < 0:
			repVotes = 0
		if demVotes == 0 and repVotes == 0:
			votes[tract] = None
		else:
			votes[tract] = demVotes / (demVotes + repVotes)

precinctPath = "C:/Users/Mitra Kiciman/Documents/NCClusterAnalysis/Data/VoteExtraction/CountyVoteData/2012/PrecinctVotesPRES12"
intersectionsFile = "C:/Users/Mitra Kiciman/Documents/gerrymanderingimpact/nc_precinct_tract_splits_2012.csv"

precinctVotes = dict()
for filename in os.listdir(precinctPath):
	with open(precinctPath+"/"+filename, mode="r") as file:
		parseFile(file, precinctVotes)

tractData = dict()
countyData = dict()
#read in distance data 
with open("tract_municipality_distance_haversine.csv", "r") as file:
	reader = csv.reader(file)
	next(reader, None)
	for row in reader:
		if row[1] == "NC":
			tractData[row[3]] = []
			tractData[row[3]].append(float(row[4]))
			if row[2] not in countyData:
				countyData[row[2]] = []
				countyData[row[2]].append(0)
			countyData[row[2]][0]+=float(row[4])

#read in demographic data
with open("CensusDemographicProfileData2010/CountyLevel/DEC_10_DP_DPDP1/DEC_10_DP_DPDP1_with_election_results.csv", "r") as file:
		reader = csv.reader(file)
		next(reader, None)
		next(reader, None)
		for row in reader:
			s = row[0].find("S")
			state = convertStateCodes(row[0][s+1:s+3])
			county = row[0][s+3:]
			if state == "NC" and county in countyData:
				countyData[county].append(int(row[157]))
				countyData[county].append(int(row[159]))
				countyData[county].append(float(row[375])*(int(row[157])+int(row[159])))
				countyData[county].append(float(row[376])*(int(row[157])+int(row[159])))

predictedTractVotes = generateModelValuesForCensusTract("NC", countyData, tractData)
convertToMargins(predictedTractVotes)

precinctTractSplits = dict()
with open(intersectionsFile, mode='r') as file:
	reader = csv.reader(file)
	next(reader, None)
	for row in reader:
		if row[0].lower() not in precinctTractSplits:
			precinctTractSplits[row[0].lower()] = dict()
		precinctTractSplits[row[0].lower()][row[1]] = float(row[2])

actualTractVotes = dict()
for key in precinctVotes:
	for split in precinctTractSplits[key]:
		if int(split) not in actualTractVotes:
			actualTractVotes[int(split)] = [0, 0]
		actualTractVotes[int(split)][0]+=precinctVotes[key][0]*precinctTractSplits[key][split]
		actualTractVotes[int(split)][1]+=precinctVotes[key][1]*precinctTractSplits[key][split]

convertToMargins(actualTractVotes)

for key in predictedTractVotes:
	print(key)
outputRows = []
for key in actualTractVotes:
	if key not in predictedTractVotes:
		outputRows.append([key, actualTractVotes[key], None, None, None])
		print(key)
		print(predictedTractVotes[key])
	elif predictedTractVotes[key] == None:
		outputRows.append([key, actualTractVotes[key], None, None, None])
	else:
		if predictedTractVotes[key] > 0.5 and actualTractVotes[key] > 0.5:
			outputRows.append([key, actualTractVotes[key], predictedTractVotes[key], predictedTractVotes[key]-actualTractVotes[key], True])
		elif predictedTractVotes[key] < 0.5 and actualTractVotes[key] < 0.5:
			outputRows.append([key, actualTractVotes[key], predictedTractVotes[key], predictedTractVotes[key]-actualTractVotes[key], True])
		else:
			outputRows.append([key, actualTractVotes[key], predictedTractVotes[key], predictedTractVotes[key]-actualTractVotes[key], False])

file = "nc_2012_tract_errors.csv"
with open(file, "w") as file:
	writer = csv.writer(file, lineterminator="\n")
	writer.writerow(["Tract", "ActualVotes", "PredictedVotes", "Error", "Correct"])
	for row in outputRows:
		writer.writerow(row)