import csv
import sys
from DistrictCountySimpleSplit import County

def get_counties(state, maptype):
	counties = dict()
	districtToCounty = {}
	
	#FilePath = "../QGIS/county_district_percentages.csv"
	FilePath = "../CensusData/CensusDemographicProfileData2010/advanced_county_splits_house_2016.csv"
	#FilePath = "../CensusData/CensusDemographicProfileData2010/advanced_county_splits.csv"
	#FilePath = "../CensusData/CensusDemographicProfileData2010/advanced_county_splits_distances_2016_house.csv"
	#FilePath = "../CensusData/CensusDemographicProfileData2010/advanced_county_splits_distances.csv"

	with open(FilePath) as file:
		reader = csv.reader(file)
		next(reader, None)
		for row in reader:
			if(state == row[1] and maptype == row[2]):
				countyID = int(row[3]) % 1000
				countyname = row[4]#.lower().replace(" county", "")
				district = int(row[5])
				demSplit = float(row[6])
				repSplit = float(row[6])
				countyObject = County(countyID, countyname, demSplit, repSplit)
				if (district in districtToCounty):
					districts_counties = districtToCounty[district]
					districts_counties.append(countyObject)
					districtToCounty[district] = districts_counties
				else:
					districtToCounty.update({district: [countyObject]})
	return districtToCounty

def main():
	result = get_counties(sys.argv[1], sys.argv[2])
	for key in result.keys():
		print(str(key) + ": " + str(result[key]))

if __name__ == "__main__":
    main()