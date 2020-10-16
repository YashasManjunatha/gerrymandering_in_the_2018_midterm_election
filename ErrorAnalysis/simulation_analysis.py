import csv
import os 

class Election(object):
	def __init__(self, demVotes, repVotes):
		self.demVotes = demVotes
		self.repVotes = repVotes
		self.uncontested = False

	def setUncontested(self, unc):
		self.uncontested = unc

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}

abbrev = {v: k for k, v in us_state_abbrev.items()}

years = ["2012", "2016"]
simulationResults = dict()
simulationPath = "DistancesResults/election_simulation_results.csv"
with open(simulationPath, "r") as file:
	reader = csv.reader(file)
	next(reader, None)
	for row in reader:
		if row[1] in years and row[2] == "current":
			if row[0] not in simulationResults:
				simulationResults[row[0]] = dict()
			if len(row[3]) == 1:
				district = "0" + row[3]
			else:
				district = row[3]
			simulationResults[row[0]][district+row[1]] = Election(float(row[4]), float(row[5]))

actualResults = dict()
for year in years:
	actualPath = year + "_elections_margins.csv"
	with open(actualPath, "r") as file:
		reader = csv.reader(file)
		next(reader, None)
		for row in reader: 
			if "At-Large" in row[0]:
				index = row[0].find("At-Large")
				state =  us_state_abbrev[row[0][:index-1]]
			elif "At-large" in row[0]:
				index = row[0].find("At-large")
				state =  us_state_abbrev[row[0][:index-1]]
			else:
				state = us_state_abbrev[row[0]]
			district = row[1]
			margin = float(row[3])/100
			winner = row[2]
			if row[4] == "N/A":
				votes = 1.0
			else:
				votes = float(row[4])
			high = votes * (0.5 + (margin/2))
			low = votes * (0.5 - (margin/2))
			if winner == "Democratic":
				if state not in actualResults:
					actualResults[state] = dict()
				actualResults[state][district+year] = Election(high, low)
			else:
				if state not in actualResults:
					actualResults[state] = dict()
				actualResults[state][district+year] = Election(low, high)
			if row[5] == "Unopposed":
				actualResults[state][district+year].setUncontested(True)

outputRows2012 = []
outputRows2016 = []
for state in simulationResults:
	for dist in simulationResults[state]:
		simulation = simulationResults[state][dist]
		actual = actualResults[state][dist]
		district = dist[:2]
		year = dist[2:]
		correct = False
		simulationMargin = (simulation.demVotes - simulation.repVotes) / (simulation.demVotes + simulation.repVotes)
		actualMargin = (actual.demVotes - actual.repVotes) / (actual.demVotes +actual.repVotes)
		if (simulationMargin > 0 and actualMargin > 0) or (simulationMargin < 0 and actualMargin < 0):
			correct = True
		error = simulationMargin - actualMargin
		row = [state, district, simulation.demVotes, simulation.repVotes, actual.demVotes, actual.repVotes, correct, error, actual.uncontested]
		if year == "2012":
			outputRows2012.append(row)
		else:
			outputRows2016.append(row)

with open("2012_simulation_analysis", "w") as file:
	writer = csv.writer(file, lineterminator = "\n")
	writer.writerow(["State", "District", "SimulationDem", "SimulaionRep", "ActualDem", "ActualRep", "Correct", "Error", "Uncontested"])
	for row in outputRows2012:
		writer.writerow(row)

with open("2016_simulation_analysis", "w") as file:
	writer = csv.writer(file, lineterminator = "\n")
	writer.writerow(["State", "District", "SimulationDem", "SimulaionRep", "ActualDem", "ActualRep", "Correct", "Error", "Uncontested"])
	for row in outputRows2016:
		writer.writerow(row)
