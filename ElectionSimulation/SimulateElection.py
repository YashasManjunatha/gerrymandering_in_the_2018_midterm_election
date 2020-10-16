from CountyLevelElectionResults import getPresidentialCountyVotes
from CountyLevelElectionResults import getCQPresidentialCountyVotes
from CountyLevelElectionResults import getHouseCountyVotes
from CountyLevelElectionResults import VoteCount
from DistrictCountyAdvancedSplit import get_counties
from DistrictCountySimpleSplit import County
import csv
import matplotlib.pyplot as plt

def simulateElection(state, electionDate, mapType):
	#countyVotes = getCountyVotes(state, electionDate)
	countyVotes = getHouseCountyVotes(state, electionDate)
	if len(countyVotes) == 0:
		print("Error: County Level Votes Unavailable For " + state + " " + electionDate)
	#for key in countyVotes:
	#	print(str(key) + ": " + str(countyVotes[key]))

	OneDistrictStates = ["AK", "DE", "MT", "ND", "SD", "VT", "WY"]
	if state in OneDistrictStates:
		districtVoteCount = VoteCount()
		for county in countyVotes.keys():
			countyVoteCount = countyVotes.get(county, VoteCount())
			districtVoteCount.addDemVotes(countyVoteCount.dem)
			districtVoteCount.addRepVotes(countyVoteCount.rep)
		return {1: districtVoteCount}

	districtToCounty = get_counties(state, mapType)
	if not districtToCounty:
		#print(state + mapType)
		districtToCounty = get_counties(state, "current")
	#for key in districtToCounty.keys():
	#	print(str(key) + ": " + str(districtToCounty[key]))

	outputPath = "election_simulation_county_results.csv"
	with open(outputPath, mode = 'a') as output:
		writer = csv.writer(output, lineterminator="\n")

		electionResults = {}
		for district in districtToCounty.keys():
			districtVoteCount = VoteCount()
			for county in districtToCounty[district]:
				countyVoteCount = countyVotes.get(county, VoteCount())
				districtVoteCount.addDemVotes(countyVoteCount.dem * county.demSplit)
				districtVoteCount.addRepVotes(countyVoteCount.rep * county.repSplit)

				writer.writerow([state, electionDate, mapType, district, county.id, countyVoteCount.dem * county.demSplit, countyVoteCount.rep * county.repSplit])

				#print(str(district) + " " + str(county.id) + " D: " + str(countyVoteCount.dem) + "*" + str(county.demSplit) + "=" + str(countyVoteCount.dem * county.demSplit) + " R: " + str(countyVoteCount.rep) + "*" + str(county.repSplit) + "=" + str(countyVoteCount.rep * county.repSplit) + " RTD: " + str(districtVoteCount.dem) + " RTR: " + str(districtVoteCount.rep))
			electionResults.update({district: districtVoteCount})
	return electionResults

def testSimulation():
	State = "NC"
	ElectionDate = "2016"
	MapType = "current"

	simulationResults = simulateElection(State, ElectionDate, MapType)
	for district in simulationResults.keys():
		print(str(district) + ": " + str(simulationResults[district]))

def calculateVoteMargin(state, electionDate, mapType):
	simulationResults = simulateElection(state, electionDate, mapType)
	voteMargin = []
	for district in simulationResults.keys():
		districtResults = simulationResults[district]
		if districtResults.dem + districtResults.rep == 0:
			print(electionDate + mapType + state + str(district))
			demVoteMargin = 0
		else:
			demVoteMargin = float(districtResults.dem) / (districtResults.dem + districtResults.rep)
		voteMargin.append(demVoteMargin)
		#print(str(district) + ": " + str(demVoteMargin))
	return voteMargin

def plotVoteMargin():
	State = ["AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"]
	#ElectionDate = ["2008", "2012", "2016"]
	ElectionDate = ["2016"]#, "2018"]
	MapType = ["current", "Compact", "Dem", "GOP"]

	BaseOutputPath = "SimulationResults/" + "VoteFractionPlots/"

	for electionDate in ElectionDate:
		PlotOutputPath = BaseOutputPath+electionDate+"/"
		for state in State:
			for mapType in MapType:
				voteMargin = calculateVoteMargin(state, electionDate, mapType)
				plt.plot(range(1,len(voteMargin)+1),sorted(voteMargin), marker='o', label=mapType)
			plt.axhline(y=0.5, color='r', linestyle='-')
			plt.ylabel('Democrat Vote Fraction')
			plt.xlabel('Districts')
			plt.legend()
			plt.title(state + " " + electionDate + " Presidential Votes Gerrymandering Signature Plot")
			PlotFileName = PlotOutputPath + state + electionDate + ".png"
			#plt.show()
			plt.savefig(PlotFileName)
			plt.close()

		for mapType in MapType:
			nationalVoteMargin = []
			for state in State:
				nationalVoteMargin += calculateVoteMargin(state, electionDate, mapType)
			#print(nationalVoteMargin)
			plt.plot(range(1,len(nationalVoteMargin)+1),sorted(nationalVoteMargin), label=mapType)
		plt.axhline(y=0.5, color='r', linestyle='-')
		plt.ylabel('Democrat Vote Fraction')
		plt.xlabel('Districts')
		plt.legend()
		plt.title("National" + electionDate + " Presidential Votes Gerrymandering Signature Plot")
		PlotFileName = BaseOutputPath + "National" + electionDate + ".png"
		plt.savefig(PlotFileName)
		plt.close()

def processResults(results):
	districtTally = [0, 0]
	for district in results.keys():
		if results[district].getWinner() == "Democrat":
			districtTally[0] += 1
		if results[district].getWinner() == "Republican":
			districtTally[1] += 1
	return districtTally

def runSimulation():
	State = ["AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"]
	#OpenElectionStates = ["NC", "AZ", "FL", "IA", "LA", "MD", "MO", "MS", "MT", "NV", "OR", "PA", "TX", "VA", "WI", "WV", "WY"]
	#Problem States = ["AK"]
	ElectionDate = ["2016", "2018"]#"2008", "2012", "2016"]
	#MapType = ["Compact","Competitive","Dem","GOP","MajMin","Proportional","algorithmic-compact","current"]

	MapType = ["current"]

	resultOutputPath = "SimulationResults/" + "election_simulation_results.csv"
	analysisOutputPath = "SimulationResults/" + "election_simulation_analysis.csv"
	with open(resultOutputPath, mode = 'w') as resultOutput, open(analysisOutputPath, mode = 'w') as analysisOutput:
		resultWriter = csv.writer(resultOutput, lineterminator="\n")
		analysisWriter = csv.writer(analysisOutput, lineterminator="\n")
		resultWriter.writerow(['State', 'ElectionDate', 'MapType', 'District', 'DemocratVote', 'RepublicanVote', 'Winner'])
		analysisWriter.writerow(['State', 'ElectionDate', 'MapType', 'DemocratDistricts', 'RepublicanDistricts'])

		for state in State:
			for electionDate in ElectionDate:
				for mapType in MapType:
					print("Simulating Election for " + state + " " + electionDate + " " + mapType)
					simulationResults = simulateElection(state, electionDate, mapType)
					for district in simulationResults.keys():
						districtResults = simulationResults[district]
						resultWriter.writerow([state, electionDate, mapType, district, districtResults.dem, districtResults.rep, districtResults.getWinner()])
					districtTally = processResults(simulationResults)
					analysisWriter.writerow([state, electionDate, mapType, districtTally[0], districtTally[1]])

def runNationalAnalysis():
	State = ["AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"]
	#ElectionDate = ["2008", "2012", "2016"]
	ElectionDate = ["2016"]#, "2018"]
	#MapType = ["Compact","Competitive","Dem","GOP","MajMin","Proportional","algorithmic-compact","current"]
	MapType = ["current"]
	
	outputPath = "SimulationResults/" + "election_simulation_national_analysis.csv"
	with open(outputPath, mode = 'w') as output:
		writer = csv.writer(output, lineterminator="\n")
		writer.writerow(['ElectionDate', 'MapType', 'DemocratDistricts', 'RepublicanDistricts'])
		for electionDate in ElectionDate:
			for mapType in MapType:
				countryTally = [0, 0]
				for state in State:
					simulationResults = simulateElection(state, electionDate, mapType)
					districtTally = processResults(simulationResults)
					countryTally[0] += districtTally[0]
					countryTally[1] += districtTally[1]
				print(electionDate + " " + mapType + " " + str(countryTally) + " " + str(countryTally[0]+countryTally[1]))
				writer.writerow([electionDate, mapType, countryTally[0], countryTally[1]])

def main():
	#results = simulateElection("NC", "2018", "current")
	#for district in results.keys():
	#	print(str(district) + ": " + str(results[district]))
	#runSimulation()
	runNationalAnalysis()
	#plotVoteMargin()

if __name__ == "__main__":
    main()