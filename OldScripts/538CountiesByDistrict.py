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

CountyPath = "../redistricting-atlas-data/county_assignments.csv"
NCcounties = get_counties("NC", "current")
for key in NCcounties.keys():
	print(key + ": " + ", ".join(map(str, NCcounties[key])))
