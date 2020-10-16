import os
import csv

class VoteCount(object):
	def __init__(self):
		self.dem = 0
		self.rep = 0

	def addDemVotes(self, demVotes):
		self.dem += demVotes

	def addRepVotes(self, repVotes):
		self.rep += repVotes

	def getWinner(self):
		if (self.dem > self.rep):
			return "Democrat"
		if (self.dem < self.rep):
			return "Republican"
		if (self.dem == self.rep):
			return "Tie"

	def __repr__(self):
		return "D Votes: " + str(self.dem) + \
		" R Votes: " + str(self.rep) + \
		" Winner: " + self.getWinner()

def getCountyVotes(state, ElectionDate, ElectionType):
	countyVotes = {}

	BaseFilePath = "openelections/openelections-results-"+state.lower()+"-master/raw/"
	for filename in os.listdir(BaseFilePath):
		if ElectionDate in filename:
			if "precinct" in filename:
				PrecinctFilePath = BaseFilePath+filename
				#print(PrecinctFilePath)
				with open(PrecinctFilePath) as file:
					reader = csv.reader(file)
					for row in reader:
						if (row[7] == ElectionType):
							processRow("precinct", row, countyVotes)

			if "county" in filename:
				CountyFilePath = BaseFilePath+filename
				#print(CountyFilePath)
				with open(CountyFilePath) as file:
					reader = csv.reader(file)
					for row in reader:
						if (row[7] == ElectionType):
							processRow("county", row, countyVotes)

	return countyVotes

def processRow(filetype, row, countyVotes):
	if filetype == "precinct":
		county = row[15].upper()
	if filetype == "county":
		county = row[16].upper()
	
	if (countyVotes.has_key(county)):
		countyVoteCount = countyVotes[county]
	else:
		countyVoteCount = VoteCount()
		countyVotes.update({county: countyVoteCount})

	if (row[14] == "DEM"):
		countyVoteCount.addDemVotes(int(row[18]))
	elif (row[14] == "REP"):
		countyVoteCount.addRepVotes(int(row[18]))

def main():
	State = "NC"
	ElectionDate = "20121106" #sys.argv[1]
	ElectionType = "US HOUSE OF REPRESENTATIVES" #"US PRESIDENT"

	result = getCountyVotes(State, ElectionDate, ElectionType)
	for key in result:
		print(key + ": " + str(result[key]))

if __name__ == "__main__":
    main()
