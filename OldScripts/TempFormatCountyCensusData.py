import csv
import math
from CountyLevelPresidentialResults import getCountyVotes
from CountyLevelPresidentialResults import VoteCount
from DistrictCountySimpleSplit import County

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

def constructWriteRow(row):
	writerow = [row[1], row[2]]
	for i in range (158, 192, 2):
		writerow.append(row[i])
	return writerow

def reverseStateCodes():
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
	return dict((v,k) for k,v in state_codes.iteritems())

state_names = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'}
reverse_state_names = dict((v,k) for k,v in state_names.iteritems())

def constructExistingSet(state, year="2016", countyMap = None):
	countyVotes = {}
	ElectionResultsFile = "CQElectionData/President_CountyDetail_"+year+".csv"
	with open(ElectionResultsFile) as file:
		reader = csv.reader(file)
		for row in reader:
			if len(row) > 1 and row[1] == state:
				#if row[29] != '':
				if row[0] == "President":
					state = row[1]
					countyName = row[4]
					if (state, countyName) in countyMap.keys():
						#countyID = int(row[29])
						countyID = countyMap.get((state, countyName))[0]
						countyObject = County(countyID, countyName)
						if row[10] != 'N/A':
							countyVotes.update({countyObject: VoteCount(int(row[10].replace(',', '')), int(row[7].replace(',', '')))})

	return countyVotes

def testaksdbalkbsgalksdbflakjdsbf():
	#existingStuff = constructExistingSet()

	#print(existingStuff)

	CountyCensusDataFilePath = "CensusDemographicProfileData2010/CountyLevel/DEC_10_DP_DPDP1/DEC_10_DP_DPDP1_with_ann.csv"
	with open(CountyCensusDataFilePath) as file:
		reader = csv.reader(file)

		state_codes = reverseStateCodes()

		outputPath = "CensusDemographicProfileData2010/CountyLevel/DEC_10_DP_DPDP1/DEC_10_DP_DPDP1_with_election_results.csv"
		with open(outputPath, mode = 'w') as output:
			writer = csv.writer(output, lineterminator="\n")
			row = next(reader, None)
			writer.writerow(row + ["DemVoteFraction", "RepVoteFraction"])
			row = next(reader, None)
			writer.writerow(row)

			currentStateID = None
			for row in reader:
				stateID = state_codes['{:02d}'.format(int(math.floor(int(row[1])/1000.0)))]
				if stateID != 'AK' and stateID != 'DC':
					stateName = state_names[stateID]
					countyName = row[2].split(" County")[0].upper()
					countyID = int(row[1]) % 1000

					if currentStateID == None or currentStateID != stateID:
						currentStateResults = constructExistingSet(stateName)
						currentStateID = stateID
					#if County(countyID, countyName) not in existingStuff.keys():
					#print(countyName)
					countyObject = County(countyID, countyName)
					countyResults = currentStateResults.get(countyObject, VoteCount())
					newrow = []
					for cell in row:
						newcell = cell.split('(')[0]
						if newcell == ' ':
							newcell = '0'
						newrow.append(newcell)

					writer.writerow(newrow + [countyResults.getDemSplit(), countyResults.getRepSplit()])

def checkCountyLinks():
	FilePath2016 = "CQElectionData/President_CountyDetail_2016.csv"
	BaseFilePath = "CQElectionData/President_CountyDetail_"
	Years = ["2012", "2008", "2004", "2000"]

	CountyMap = {}
	with open(FilePath2016) as file:
		reader = csv.reader(file)
		for row in reader:
			if row[0] == "President" and row[29] != '':
				state = row[1]
				county = row[4]
				countyID = int(row[29])
				countyName = row[30]
				CountyMap.update({(state, county): (countyID, countyName)})
	#print(CountyMap)

	#for year in Years:
	#	with open(BaseFilePath+year+".csv") as file:
	#		reader = csv.reader(file)
	#		for row in reader:
	#			if row[0] == "President":
	#				state = row[1]
	#				county = row[4]
	#				if (state, county) not in CountyMap.keys():
	#					print(year + str((state, county)))


	state_codes = reverseStateCodes()
	outputPath = "CensusDemographicProfileData2010/CountyLevel/DEC_10_DP_DPDP1/DEC_10_DP_DPDP1_with_election_results.csv"
	with open(outputPath, mode = 'w') as output:
		writer = csv.writer(output, lineterminator="\n")

		CountyCensusDataFilePath = "CensusDemographicProfileData2010/CountyLevel/DEC_10_DP_DPDP1/DEC_10_DP_DPDP1_with_ann.csv"
		with open(CountyCensusDataFilePath) as file:
			reader = csv.reader(file)
			row = next(reader, None)
			writer.writerow(row + ["DemVoteFraction", "RepVoteFraction"])
			row = next(reader, None)
			writer.writerow(row)

		for year in ["2016", "2012", "2008", "2004", "2000"]:
			print(year)
			CountyCensusDataFilePath = "CensusDemographicProfileData2010/CountyLevel/DEC_10_DP_DPDP1/DEC_10_DP_DPDP1_with_ann.csv"
			with open(CountyCensusDataFilePath) as file:
				reader = csv.reader(file)
				next(reader, None)
				next(reader, None)

				currentStateID = None
				for row in reader:
					stateID = state_codes['{:02d}'.format(int(math.floor(int(row[1])/1000.0)))]
					if stateID != 'AK' and stateID != 'DC':
						stateName = state_names[stateID]
						countyName = row[2].split(" County")[0].upper()
						countyID = int(row[1]) % 1000

						if currentStateID == None or currentStateID != stateID:
							currentStateResults = constructExistingSet(stateName, year, CountyMap)
							currentStateID = stateID
						#if County(countyID, countyName) not in existingStuff.keys():
						#print(countyName)
						countyObject = County(countyID, countyName)
						if countyObject not in currentStateResults.keys():
							print(countyObject)
						countyResults = currentStateResults.get(countyObject, VoteCount())
						newrow = []
						for cell in row:
							newcell = cell.split('(')[0]
							if newcell == ' ':
								newcell = '0'
							newrow.append(newcell)

						writer.writerow(newrow + [countyResults.getDemSplit(), countyResults.getRepSplit()])

				

def cleanAndDumpCountyData():
	FilePath = "DEC_10_DP_DPDP1/DEC_10_DP_DPDP1_with_ann.csv"
	with open(FilePath) as file:
		reader = csv.reader(file)

		outputPath = "DEC_10_DP_DPDP1/clean_county_census_data.csv"
		with open(outputPath, mode = 'w') as output:
			writer = csv.writer(output, lineterminator="\n")
			row = next(reader, None)
			writer.writerow(constructWriteRow(row) + ["DemSplit", "RepSplit"])
			row = next(reader, None)
			writer.writerow(constructWriteRow(row) + ["DemSplit", "RepSplit"])

			state_codes = reverseStateCodes()

			currentStateID = None
			for row in reader:
				stateID = state_codes['{:02d}'.format(int(math.floor(int(row[1])/1000.0)))]
				if stateID != 'AK':
					countyID = int(row[1]) % 1000
					countyName = row[2]
					countyObject = County(countyID, countyName)
					if currentStateID == None or currentStateID != stateID:
						currentStateResults = getCountyVotes(stateID, "2016")
					#if countyObject not in currentStateResults.keys():
					#	print(countyObject)
					countyResults = currentStateResults.get(countyObject, VoteCount())
					writer.writerow(constructWriteRow(row) + [countyResults.getDemSplit(), countyResults.getRepSplit()])


def cleanAndDumpStateCensusTractData(state):
	df = pd.read_csv("DEC_10_DP_DPDP1/clean_county_census_data.csv", skiprows=[1], usecols=range(2, 19))
	target = pd.read_csv("DEC_10_DP_DPDP1/clean_county_census_data.csv", skiprows=[1], usecols=[19,20])
	
	X = df[["HD02_S078", "HD02_S079"]]
	yDem = target["DemSplit"]
	modelDem = sm.OLS(yDem, X).fit()
	print(modelDem.summary())
	
	yRep = target["RepSplit"]
	modelRep = sm.OLS(yRep, X).fit()
	print(modelRep.summary())
	
	TractModel = {}
	FilePath = "TempFolderName/DEC_10_DP_DPDP1/DEC_10_DP_DPDP1_with_ann.csv"
	with open(FilePath) as file:
		reader = csv.reader(file)
		
		outputPath = "TempFolderName/DEC_10_DP_DPDP1/clean_state_census_data.csv"
		with open(outputPath, mode = 'w') as output:
			writer = csv.writer(output, lineterminator="\n")
			row = next(reader, None)
			writer.writerow(constructWriteRow(row) + ["DemSplit", "RepSplit"])
			row = next(reader, None)
			writer.writerow(constructWriteRow(row) + ["DemSplit", "RepSplit"])
			
			for row in reader:
				newRow = constructWriteRow(row)
				if row[4] == "(X)":
					modelResults = [0.0, 0.0]
				else:
					XTract = [float(newRow[2]), float(newRow[3])]
					modelResults = [modelDem.predict(XTract)[0], modelRep.predict(XTract)[0]]
					#s = int(row[3].split('(')[0])
					#modelResults = [s, s]
				writer.writerow(newRow + modelResults)
				TractModel.update({int(row[1]): modelResults})

	TractFilePath = "tract_district_splits.csv"
	CountyTract = {}
	CountyDistrictTract = {}
	with open(TractFilePath) as file:
		reader = csv.reader(file)
		next(reader, None)
		for row in reader:
			if int(row[0]) == 37 and row[2] == 'current':
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
	
	outputPath = "TempFolderName/county_district_percentages.csv"
	with open(outputPath, mode = 'w') as output:
		writer = csv.writer(output, lineterminator="\n")
		writer.writerow(["stateFP", "state", "maptype", "countyFP", "county", "district", "demPercentage", "repPercentage"])
		for countydistrict in CountyDistrictTract.keys():
			countyFP = countydistrict[0]
			district = countydistrict[1]
			TractList = CountyDistrictTract[countydistrict]
			CountyTractList = CountyTract[countyFP]
			
			demCountyDistrictSum = 0
			repCountyDistrictSum = 0
			for tract in TractList:
				demCountyDistrictSum += TractModel[tract[0]][0] * tract[1]
				repCountyDistrictSum += TractModel[tract[0]][1] * tract[1]
				
			demCountySum = 0
			repCountySum = 0
			for tract in CountyTractList:
				demCountySum += TractModel[tract[0]][0] * tract[1]
				repCountySum += TractModel[tract[0]][1] * tract[1]
				
			demPercentage = float(demCountyDistrictSum)/demCountySum
			repPercentage = float(repCountyDistrictSum)/repCountySum
			
			writer.writerow([37, "NC", "current", countyFP, "...", district, demPercentage, repPercentage])


def runRegression():
	df = pd.read_csv("DEC_10_DP_DPDP1/clean_county_census_data.csv", skiprows=[1], usecols=range(2, 19))
	target = pd.read_csv("DEC_10_DP_DPDP1/clean_county_census_data.csv", skiprows=[1], usecols=[19,20])
	
	X = df[["HD02_S078", "HD02_S079"]]
	#X = df[["HD02_S078", "HD02_S079", "HD02_S080", "HD02_S081", "HD02_S082", "HD02_S083", "HD02_S084", "HD02_S085", "HD02_S086", "HD02_S087", "HD02_S088", "HD02_S089", "HD02_S090", "HD02_S091", "HD02_S092", "HD02_S093", "HD02_S094"]]
	y = target["DemSplit"]

	#Linear Regression in Statsmodels
	#X = sm.add_constant(X)
	model = sm.OLS(y, X).fit()
	predictions = model.predict(X)
	print(model.summary())

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
	checkCountyLinks()
	#cleanAndDumpStateCensusTractData("")
	#testaksdbalkbsgalksdbflakjdsbf()
	#print(constructExistingSet())

	#with open("sample.csv", mode = 'w') as output:
	#	writer = csv.writer(output, lineterminator="\n")
	#	with open("CQElectionData/House_DistrictDetail_2012_2016.csv") as file:
	#		reader = csv.reader(file)
	#		for row in reader:
	#			if len(row) > 10:
	#				if row[3] == "2016":
	#					writer.writerow([reverse_state_names[row[1]], row[5], row[10], row[7], row[19]])
	#					#print(row[1] +"\t"+ row[5] + "\t" + row[10] + "\t" + row[7])

if __name__ == "__main__":
    main()