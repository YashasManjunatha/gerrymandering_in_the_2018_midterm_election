import csv

def get_counties(state, maptype):
	"""
	Returns a dictionary that maps each county to a list of districts
	that it is split into

	Parameters:
	state: 2 letter capital abbreviation for the
		   state for which to get the counties
	maptype: the type of districting plan
	-"Compact": compact districts that follow county borders
	-"Dem": Democratic Gerrymander
	-"GOP": Republican Gerrymander
	-"current": current enacted map
	"""
	CountyPath = "redistricting-atlas-data/county_assignments.csv"
	counties = dict()
	with open(CountyPath) as file:
		reader = csv.reader(file)
		next(reader, None)
		for row in reader:
			if(state == row[1] and maptype == row[2]):
				countyname = row[4].lower().replace(" county", "")
				districts = counties.get(countyname)
				if not (isinstance(districts, type(None))):
					districts.append(int(row[5]))					
					counties[countyname] = districts
				else:
					counties[countyname] = [int(row[5])]

	return counties

def getCountyVotes():
	ElectionType = "US HOUSE OF REPRESENTATIVES"
	PrecinctFilePath = "openelections-results-nc/raw/20161108__nc__general__precinct__raw.csv"
	CountyFilePath = "openelections-results-nc/raw/20161108__nc__general__county__raw.csv"

	countyVotes = dict()
	with open(PrecinctFilePath) as file:
		reader = csv.reader(file)
		for row in reader:
			if (row[7] == ElectionType):
				if (countyVotes.has_key(row[15])):
					if (row[14] == "DEM"):
						countyVotes[row[15]]["DEM"] += int(row[18])
					elif (row[14] == "REP"):
						countyVotes[row[15]]["REP"] += int(row[18])
				else:
					if (row[14] == "DEM"):
						countyVotes.update({row[15]: {"DEM": int(row[18]), "REP": 0}})
					elif (row[14] == "REP"):
						countyVotes.update({row[15]: {"DEM": 0, "REP": int(row[18])}})
	
	with open(CountyFilePath) as file:
		reader = csv.reader(file)
		for row in reader:
			if (row[7] == ElectionType):
				if (countyVotes.has_key(row[16])):
					if (row[14] == "DEM"):
						countyVotes[row[16]]["DEM"] += int(row[18])
					elif (row[14] == "REP"):
						countyVotes[row[16]]["REP"] += int(row[18])
				else:
					if (row[14] == "DEM"):
						countyVotes.update({row[16]: {"DEM": int(row[18]), "REP": 0}})
					elif (row[14] == "REP"):
						countyVotes.update({row[16]: {"DEM": 0, "REP": int(row[18])}})

	return countyVotes

districtToCounty = {}
countyMap = get_counties("NC", "current")
for county in countyMap.keys():
	numberOfDistrictsCountyLivesIn = len(countyMap[county])
	countySplit = 1.0/numberOfDistrictsCountyLivesIn
	for district in countyMap[county]:
		if (districtToCounty.has_key(district)):
			current_counties = districtToCounty[district]
			current_counties.append({county: countySplit})
			districtToCounty[district] = current_counties
		else:
			districtToCounty.update({district: [{county: countySplit}]})

for key in districtToCounty.keys():
	print(str(key) + ": " + str(districtToCounty[key]))

countyResults = getCountyVotes()
electionResults = {}
for district in districtToCounty.keys():
	districtResult = {"DEM": 0, "REP": 0}
	for county in districtToCounty[district]:
		districtResult["DEM"] += countyResults[county.keys()[0].upper()]["DEM"]*county[county.keys()[0]]
		districtResult["REP"] += countyResults[county.keys()[0].upper()]["REP"]*county[county.keys()[0]]
	electionResults.update({district: districtResult})

for key in electionResults.keys():
	print(str(key) + ": " + str(electionResults[key]))