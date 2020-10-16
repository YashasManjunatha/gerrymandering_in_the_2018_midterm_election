import csv
import math
import sys
from DistrictCountySimpleSplit import County

class VoteCount(object):
	def __init__(self, demVotes = 0, repVotes = 0):
		self.dem = demVotes
		self.rep = repVotes

	def addDemVotes(self, demVotes):
		self.dem += demVotes

	def addRepVotes(self, repVotes):
		self.rep += repVotes

	def getDemSplit(self):
		if self.dem + self.rep == 0:
			return 0.0
		return float(self.dem) / (self.dem + self.rep)

	def getRepSplit(self):
		if self.dem + self.rep == 0:
			return 0.0
		return float(self.rep) / (self.dem + self.rep)

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

def getPresidentialCountyVotes(state, electionDate):
	countyVotes = {}

	FilePath = "../ElectionData/US_County_Level_Election_Results_08-16/US_County_Level_Presidential_Results_08-16.csv"
	with open(FilePath) as file:
		reader = csv.reader(file)
		next(reader, None)
		for row in reader:
			if math.floor(int(row[0])/1000.0) == int(state_codes[state]):
				countyID = int(row[0]) % 1000
				countyName = row[1]#.lower().replace(" county", "")
				countyObject = County(countyID, countyName)
				if electionDate == "2008":
					countyVoteCount = VoteCount(int(row[3]), int(row[4]))
				if electionDate == "2012":
					countyVoteCount = VoteCount(int(row[7]), int(row[8]))
				if electionDate == "2016":
					countyVoteCount = VoteCount(int(row[11]), int(row[12]))
				countyVotes.update({countyObject: countyVoteCount})

	return countyVotes

state_names = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'}

def getCQPresidentialCountyVotes(state, electionDate):
	state = state_names[state]

	countyVotes = {}
	ElectionResultsFile = "CQElectionData/President_CountyDetail_2016.csv"
	with open(ElectionResultsFile) as file:
		reader = csv.reader(file)
		for row in reader:
			if row[1] == state:
				if row[29] != '':
					countyID = int(row[29])
					countyName = row[4]
					countyObject = County(countyID, countyName)
					if row[10] != 'N/A':
						countyVotes.update({countyObject: VoteCount(int(row[10].replace(',', '')), int(row[7].replace(',', '')))})
	return countyVotes

def getHouseCountyVotes(state, electionDate):
	countyVotes = {}
	House2016ElectionResultsFile = "../ElectionData/NYTHouseElectionData/"+electionDate+"HouseResultsAggregated.csv"
	with open(House2016ElectionResultsFile) as file:
		reader = csv.reader(file)
		for row in reader:
			if row[0] == state:
				countyID = int(row[1])%1000
				countyName = row[2]
				countyObject = County(countyID, countyName)
				countyVoteCount = VoteCount(int(row[3]), int(row[4]))
				countyVotes.update({countyObject: countyVoteCount})
	return countyVotes

def main():
	State = sys.argv[1] #"NC"
	ElectionDate = sys.argv[2] #"2016"

	#result = getCountyVotes(State, ElectionDate)
	result = getHouseCountyVotes(State, ElectionDate)
	for key in result:
		print(str(key) + ": " + str(result[key]))

if __name__ == "__main__":
    main()
