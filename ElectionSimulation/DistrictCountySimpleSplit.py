import csv
import sys

class County(object):
	def __init__(self, cid, name, demSplit = None, repSplit = None):
		self.id = cid
		self.name = name
		self.demSplit = demSplit
		self.repSplit = repSplit

	def __eq__(self, other):
	    return (self.__class__ == other.__class__ and self.id == other.id)

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(self.id)

	def __repr__(self):
		return str(self.id) + " " + self.name + " " + str(self.demSplit) + " " + str(self.repSplit)

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
	FilePath = "../redistricting-atlas-data/county_assignments.csv"
	with open(FilePath) as file:
		reader = csv.reader(file)
		next(reader, None)
		for row in reader:
			if(state == row[1] and maptype == row[2]):
				countyID = int(row[3]) % 1000
				countyname = row[4]#.lower().replace(" county", "")
				countyObject = County(countyID, countyname)
				districts = counties.get(countyObject)
				if not (isinstance(districts, type(None))):
					districts.append(int(row[5]))					
					counties[countyObject] = districts
				else:
					counties[countyObject] = [int(row[5])]

	#for key in counties.keys():
	#	print(str(key) + ": " + str(counties[key]))

	districtToCounty = {}
	for county in counties.keys():
		numberOfDistrictsCountyLivesIn = len(counties[county])
		simpleCountySplit = 1.0/numberOfDistrictsCountyLivesIn
		county.demSplit = simpleCountySplit
		county.repSplit = simpleCountySplit
		for district in counties[county]:
			if (districtToCounty.has_key(district)):
				districts_counties = districtToCounty[district]
				districts_counties.append(county)
				districtToCounty[district] = districts_counties
			else:
				districtToCounty.update({district: [county]})

	return districtToCounty

def main():
	result = get_counties(sys.argv[1], sys.argv[2])
	for key in result.keys():
		print(str(key) + ": " + str(result[key]))

if __name__ == "__main__":
    main()