from CountyLevelElectionResults import getPresidentialCountyVotes
from CountyLevelElectionResults import getHouseCountyVotes
from CountyLevelElectionResults import VoteCount
from DistrictCountySimpleSplit import County
import csv
import math

import statsmodels.api as sm
import numpy as np
import pandas as pd
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
from sklearn.model_selection import KFold
from sklearn.model_selection import LeaveOneOut 
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn import metrics

def appendElectionResultsToCountyData(electionDate = "2016"):
	CountyCensusDataFilePath = "CensusDemographicProfileData2010/CountyLevel/DEC_10_DP_DPDP1/DEC_10_DP_DPDP1_with_ann.csv"
	with open(CountyCensusDataFilePath) as file:
		reader = csv.reader(file)

		outputPath = "CensusDemographicProfileData2010/CountyLevel/DEC_10_DP_DPDP1/DEC_10_DP_DPDP1_with_house_election_results.csv"
		with open(outputPath, mode = 'w') as output:
			writer = csv.writer(output, lineterminator="\n")
			row = next(reader, None)
			writer.writerow(row + ["DemVoteFraction", "RepVoteFraction"])
			row = next(reader, None)
			writer.writerow(row + ["DemVoteFraction", "RepVoteFraction"])

			currentStateID = None
			for row in reader:
				stateID = convertStateCodes('{:02d}'.format(int(math.floor(int(row[1])/1000.0))))
				if stateID != 'AK':
					countyID = int(row[1]) % 1000
					countyName = row[2]
					countyObject = County(countyID, countyName)
					if currentStateID == None or currentStateID != stateID:
						#currentStateResults = getPresidentialCountyVotes(stateID, electionDate)
						currentStateResults = getHouseCountyVotes(stateID, electionDate)
					#if countyObject not in currentStateResults.keys():
					#	print(countyObject)
					countyResults = currentStateResults.get(countyObject, VoteCount())
					row[3] = int(row[3].split('(')[0])
					#####
					if countyObject in currentStateResults.keys():
					#####
						writer.writerow(row + [countyResults.getDemSplit(), countyResults.getRepSplit()])

def generateModelValuesForCensusTract(state):
	#CountyCensusDataFilePath = "CensusDemographicProfileData2010/CountyLevel/DEC_10_DP_DPDP1/clean_county_census_data.csv"
	#df = pd.read_csv(CountyCensusDataFilePath, skiprows=[1], usecols=range(2, 19))
	#target = pd.read_csv(CountyCensusDataFilePath, skiprows=[1], usecols=[19,20])

	CountyCensusDataFilePath = "CensusDemographicProfileData2010/CountyLevel/DEC_10_DP_DPDP1/DEC_10_DP_DPDP1_with_house_election_results.csv"
	data = pd.read_csv(CountyCensusDataFilePath, skiprows=[1])
	df = data.iloc[:,2:-2]
	target = data.iloc[:,-2:]

	#XColumns = ["HD02_S078", "HD02_S079"]
	XColumns = ["HD02_S051", "HD02_S078", "HD02_S079", "HD02_S081", "HD02_S107"]

	X = df[XColumns]
	yDem = target["DemVoteFraction"]
	modelDem = sm.OLS(yDem, X).fit()
	#print(modelDem.summary())

	yRep = target["RepVoteFraction"]
	modelRep = sm.OLS(yRep, X).fit()
	#print(modelRep.summary())

	TractModelValues = {}
	TractCensusDataFilePath = "CensusDemographicProfileData2010/CensusTractLevel/"+state+"_DEC_10_DP_DPDP1/DEC_10_DP_DPDP1_with_ann.csv"

	with open(TractCensusDataFilePath) as file:
		reader = csv.reader(file)
		row = next(reader, None)
		XColumnLocations = []
		for index,entry in enumerate(row):
			if entry in XColumns:
				XColumnLocations.append(index)
		next(reader, None)

		for row in reader:
			if row[4] == "(X)":
				modelValues = [0.0, 0.0]
			else:
				XTract = []
				for index in XColumnLocations:
					XTract.append(float(row[index].split('(')[0]))
				totalPopulation = int(row[153].split('(')[0])
				modelDemValue = max(0, min(modelDem.predict(XTract)[0], 1))
				modelRepValue =  max(0, min(modelRep.predict(XTract)[0], 1))
				modelValues = [modelDemValue * totalPopulation, modelRepValue * totalPopulation]
			TractModelValues.update({int(row[1]): modelValues})

	return TractModelValues

def readModelValuesForCensusTract(state):
	FilePath = "voting_model_data/tract_dem_rep_percentage_data.csv"
	TractModelValues = {}
	with open(FilePath) as file:
		reader = csv.reader(file)
		next(reader, None)
		for row in reader:
			if row[0] == state:
				modelValues = [int(row[2]), int(row[4])]
				TractModelValues.update({int(row[1]): modelValues})
	return TractModelValues


def generateCountyDistrictTractMappings(state, maptype):
	TractFilePath = "tract_district_splits.csv"
	CountyTract = {}
	CountyDistrictTract = {}
	with open(TractFilePath) as file:
		reader = csv.reader(file)
		next(reader, None)
		for row in reader:
			if row[1] == state and row[2] == maptype:
				countyFP = int(row[3])%1000
				tractID = int(row[4])
				district = int(row[5])
				percentage = float(row[6])

				if CountyTract.has_key(countyFP):
					TractList = CountyTract[countyFP]
					TractList.append((tractID, percentage))
					CountyTract[countyFP] = TractList
				else:
					CountyTract.update({countyFP:[(tractID, percentage)]})
						
				if CountyDistrictTract.has_key((countyFP, district)):
					TractList = CountyDistrictTract[(countyFP, district)]
					TractList.append((tractID, percentage))
					CountyDistrictTract[(countyFP, district)] = TractList
				else:
					CountyDistrictTract.update({(countyFP, district):[(tractID, percentage)]})

	return CountyTract, CountyDistrictTract

def generateUniqueStateMapPairs():
	UniqueStateMapPairs = []
	File = "redistricting-atlas-data/county_assignments.csv"
	with open(File) as file:
		reader = csv.reader(file)
		next(reader, None)
		for row in reader:
			StateMapPair = (row[1], row[2])
			if StateMapPair not in UniqueStateMapPairs:
				UniqueStateMapPairs.append(StateMapPair)
	return UniqueStateMapPairs

def generateAdvancedSplits():
	outputPath = "CensusDemographicProfileData2010/advanced_county_splits_house_2016.csv"
	#outputPath = "voting_model_data/advanced_county_splits.csv"
	with open(outputPath, mode = 'w') as output:
		writer = csv.writer(output, lineterminator="\n")
		writer.writerow(["stateFP", "state", "maptype", "countyFP", "county", "district", "demPercentage", "repPercentage"])

		stateModelValues = {}

		UniqueStateMapPairs = generateUniqueStateMapPairs()
		for StateMapPair in UniqueStateMapPairs:
			print(StateMapPair)
			state = StateMapPair[0]
			maptype = StateMapPair[1]
			CountyTract, CountyDistrictTract = generateCountyDistrictTractMappings(state, maptype)
			if state not in stateModelValues.keys():
				TractModelValues = generateModelValuesForCensusTract(state)
				stateModelValues.update({state: TractModelValues})
			else:
				TractModelValues = stateModelValues.get(state)

			for countydistrict in CountyDistrictTract.keys():
				countyFP = countydistrict[0]
				district = countydistrict[1]
				TractList = CountyDistrictTract[countydistrict]
				CountyTractList = CountyTract[countyFP]
			
				demCountyDistrictSum = 0
				repCountyDistrictSum = 0
				for tract in TractList:
					modelValues = TractModelValues.get(tract[0], None)
					if modelValues == None:
						#print(tract[0])
						modelValues = [0,0]
					demCountyDistrictSum += modelValues[0] * tract[1]
					repCountyDistrictSum += modelValues[1] * tract[1]

				demCountySum = 0
				repCountySum = 0
				for tract in CountyTractList:
					modelValues = TractModelValues.get(tract[0], None)
					if modelValues == None:
						#print(tract[0])
						modelValues = [0,0]
					demCountySum += modelValues[0] * tract[1]
					repCountySum += modelValues[1] * tract[1]

				if demCountySum != 0:
					demPercentage = float(demCountyDistrictSum)/demCountySum
				if repCountySum != 0:
					repPercentage = float(repCountyDistrictSum)/repCountySum

				writer.writerow([convertStateCodes(state), state, maptype, countyFP, "...", district, demPercentage, repPercentage])

def convertStateCodes(state):
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
	if state_codes.has_key(state):
		return state_codes[state]
	else:
		reverseStateCodes = dict((v,k) for k,v in state_codes.iteritems())
		if reverseStateCodes.has_key(state):
			return reverseStateCodes[state]
	return None

def runRegression():
	CountyCensusDataFilePath = "CensusDemographicProfileData2010/CountyLevel/DEC_10_DP_DPDP1/DEC_10_DP_DPDP1_with_house_election_results.csv"
	data = pd.read_csv(CountyCensusDataFilePath, skiprows=[1])
	df = data.iloc[:,2:-2]
	target = data.iloc[:,-2:]

	#Linear Regression in Statsmodels
	#X = sm.add_constant(X)
	#model = sm.OLS(y, X).fit()
	#predictions = model.predict(X)
	#print(model.summary())

	XColumns = ["HD01_S001", "HD02_S078", "HD02_S079"]
	XColumns = ["HD02_S051", "HD02_S078", "HD02_S079", "HD02_S081", "HD02_S107"]
	X = df[XColumns]

	yDem = target["DemVoteFraction"]
	modelDem = sm.OLS(yDem, X).fit()
	print(modelDem.summary())
	
	yRep = target["RepVoteFraction"]
	modelRep = sm.OLS(yRep, X).fit()
	print(modelRep.summary())

	#Linear Regression in SKLearn
	#X = df
	#y = target["DemSplit"]
	#lm = linear_model.LinearRegression()
	#model = lm.fit(X,y)
	#predictions = lm.predict(X)
	#print(lm.score(X,y))
	#print(lm.coef_)

	#Train/Test Split
	#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
	
	#lm = linear_model.LinearRegression()
	#model = lm.fit(X_train, y_train)
	#predictions = lm.predict(X_test)
	#print ("Score:", model.score(X_test, y_test))

	#model = sm.OLS(y_train, X_train).fit()
	#predictions = model.predict(X_test)
	#print(model.summary())

	#plt.scatter(y_test, predictions)
	#plt.xlabel("True Values")
	#plt.ylabel("Predictions")
	#plt.show()

	#K-Folds Cross Validation
	#kf = KFold(n_splits=2)
	#kf.get_n_splits(X)
	#for train_index, test_index in kf.split(X):
	#	print("TRAIN:", train_index, "TEST:", test_index)
	#	X_train, X_test = X.loc[train_index], X.loc[test_index]
	#	y_train, y_test = y.loc[train_index], y.loc[test_index]

	#Leave One Out Cross Validation (LOOCV)
	#loo = LeaveOneOut()
	#loo.get_n_splits(X)
	#
	#for train_index, test_index in loo.split(X):
	#	print("TRAIN:", train_index, "TEST:", test_index)
	#	X_train, X_test = X.loc[train_index], X.loc[test_index]
	#	y_train, y_test = y.loc[train_index], y.loc[test_index]
	#	print(X_train, X_test, y_train, y_test)

	#Cross Validation
	#scores = cross_val_score(model, df, y, cv=6)
	#print ("Cross-validated scores:", scores)
	#predictions = cross_val_predict(model, df, y, cv=6)
	#plt.scatter(y, predictions)
	#plt.show()
	#accuracy = metrics.r2_score(y, predictions)
	#print ("Cross-Predicted Accuracy:", accuracy)

def main():
	#appendElectionResultsToCountyData()
	runRegression()
	generateAdvancedSplits()

if __name__ == "__main__":
    main()