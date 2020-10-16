import csv 
import os
from advancedsplitsmunicipalities import generateModelValuesForCensusTract, convertStateCodes, generateCountyDistrictTractMappings
import numpy as np
import statsmodels.api as sm

def convertToMargins(votes):
	for county in votes:
		demVotes = votes[county][0]
		repVotes = votes[county][1]
		if demVotes < 0:
			demVotes = 0
		if repVotes < 0:
			repVotes = 0
		if demVotes == 0 and repVotes == 0:
			votes[county] = None
		else:
			votes[county] = demVotes / (demVotes + repVotes)

#read in distance data 
distByState = dict()
distByTract = dict()
with open("tract_municipality_distance_haversine.csv", "r") as file:
	reader = csv.reader(file)
	next(reader, None)
	for row in reader:
		if row[1] not in distByState:
			distByState[row[1]] = dict()
		if row[2] not in distByState[row[1]]:
			distByState[row[1]][row[2]] = []
			distByState[row[1]][row[2]].append(0)
		distByState[row[1]][row[2]][0]+=float(row[4])
		if row[3] in distByTract:
			print("tract already in dict")
		else:
			distByTract[row[3]] = []
			distByTract[row[3]].append(float(row[4]))

#read in demographic and elecion data 
with open("CensusDemographicProfileData2010/CountyLevel/DEC_10_DP_DPDP1/DEC_10_DP_DPDP1_with_election_results.csv", "r") as file:
	reader = csv.reader(file)
	next(reader, None)
	next(reader, None)
	for row in reader:
		s = row[0].find("S")
		state = convertStateCodes(row[0][s+1:s+3])
		county = row[0][s+3:]
		if county in distByState[state]:
			distByState[state][county].append(int(row[157]))
			distByState[state][county].append(int(row[159]))
			distByState[state][county].append(float(row[375])*(int(row[157])+int(row[159])))
			distByState[state][county].append(float(row[376])*(int(row[157])+int(row[159])))

		else:
			print(state, county)

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

outputRows = []
predictedCountyVotesByState = dict()
for state in distByState:
	if state == "DC" or state == "AK":
		continue
	currentPredictions = generateModelValuesForCensusTract(state, distByState[state], distByTract)
	CountyTract, CountyDistrictTract = generateCountyDistrictTractMappings(state, "current")

	for county in CountyTract.keys():
		CountyTractList = CountyTract[county] 
		demCountySum = 0
		repCountySum = 0
		for tract in CountyTractList:
			modelValues = currentPredictions.get(tract[0], None)
			if modelValues == None:
				#print(tract[0])
				modelValues = [0,0]
			demCountySum += modelValues[0]
			repCountySum += modelValues[1]

		if state not in predictedCountyVotesByState:
			predictedCountyVotesByState[state] = dict()
		county = str(county)
		while len(county) < 3:
			county = "0" + county
		predictedCountyVotesByState[state][county] = [demCountySum, repCountySum]

for state in predictedCountyVotesByState:
	convertToMargins(predictedCountyVotesByState[state])
	for county in predictedCountyVotesByState[state]:
		if county not in distByState[state]:
			outputRows.append([state, county, predictedCountyVotesByState[state][county], None, None, None])
			print(county)
		else:
			actualDemVotes = distByState[state][county][3]/(distByState[state][county][1]+distByState[state][county][2])
			if predictedCountyVotesByState[state][county] > 0.5 and actualDemVotes > 0.5:
				outputRows.append([state, county, predictedCountyVotesByState[state][county], actualDemVotes, predictedCountyVotesByState[state][county]-actualDemVotes, True])
			elif predictedCountyVotesByState[state][county] < 0.5 and actualDemVotes < 0.5:
				outputRows.append([state, county, predictedCountyVotesByState[state][county], actualDemVotes, predictedCountyVotesByState[state][county]-actualDemVotes, True])
			else:
				outputRows.append([state, county, predictedCountyVotesByState[state][county], actualDemVotes, predictedCountyVotesByState[state][county]-actualDemVotes, False])

file = "county_level_errors.csv"
with open(file, "w") as file:
	writer = csv.writer(file, lineterminator="\n")
	writer.writerow(["State", "County", "PredictedVotes", "ActualVotes", "Error", "Correct"])
	for row in outputRows:
		writer.writerow(row)