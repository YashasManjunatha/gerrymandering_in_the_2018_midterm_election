import json
import csv
from sklearn.metrics import mean_squared_error
import numpy as np

def formatresults():
	results = []
	with open("2018HouseResultsFormatted.csv", "w") as output:
		writer = csv.writer(output, lineterminator="\n")
		with open("2018HouseResults.txt", "r") as text_file:
			lines = text_file.readlines()
			for row in lines:
				d = json.loads(row)
				rep = []
				dem = []
				for candidate in d['candidates']:
					if candidate['party_id'] == "republican":
						rep.append(str(candidate['candidate_key']))
					if candidate['party_id'] == "democrat":
						dem.append(str(candidate['candidate_key']))
				for county in d['counties']:
					demvote = 0
					for demcandidate in dem:
						demvote += county['results'][demcandidate]
					repvote = 0
					for repcandidate in rep:
						repvote += county['results'][repcandidate]
					#print(d['path'] + " " + str(county['fips']) + " " + str(county['votes']) + " " + county['name'] + " " + str(demvote) + " " + str(repvote))
					writer.writerow([d['state_id'], d['race_name'], d['seat'], county['fips'], county['name'], demvote, repvote])
				#print(d['race_id'])
				#writer.writerow()


def aggregate():
	everything = []
	with open("2018HouseResultsAggregated.csv", "w") as output:
		writer = csv.writer(output, lineterminator="\n")
		with open("2018HouseResultsFormatted.csv", "r") as file:
			reader = csv.reader(file)
			for row in reader:
				everything.append(row)
			donefips = []
			for row in everything:
				if row[3] not in donefips:
					cumdemvotes = 0
					cumrepvotes = 0
					for i in everything:
						if row[3] == i[3]:
							cumdemvotes += int(i[5])
							cumrepvotes += int(i[6])
					writer.writerow([row[0], row[3], row[4], cumdemvotes, cumrepvotes])
					donefips.append(row[3])
			
				
def checkcounty():
	with open("2016HouseResultsCountyCheck.csv", "w") as output:
		writer = csv.writer(output, lineterminator="\n")

		countyresults = []
		with open("election_simulation_county_results.csv", "r") as file:
			reader = csv.reader(file)
			for row in reader:
				countyresults.append(row)

		with open("2016HouseResultsFormatted.csv", "r") as file:
			reader = csv.reader(file)
			for row in reader:
				for cr in countyresults:
					if row[0] == cr[0] and cr[1] == "2016" and row[2] == cr[3] and int(row[3])%1000 == int(cr[4]):
						writer.writerow([row[0], cr[0], row[1], row[2], cr[3], row[3], cr[4], row[4], row[5], cr[5], row[6], cr[6]])

def districtresults():
	with open("2018HouseDistrictResults.csv", "w") as output:
		writer = csv.writer(output, lineterminator="\n")
		with open("2018HouseResults.txt", "r") as text_file:
			lines = text_file.readlines()
			for row in lines:
				row = row[2:-2]
				print(row)
				d = json.loads(row)
				rep = []
				dem = []
				for candidate in d['candidates']:
					if candidate['party_id'] == "republican":
						rep.append(str(candidate['candidate_key']))
					if candidate['party_id'] == "democrat":
						dem.append(str(candidate['candidate_key']))
				demvote = 0
				repvote = 0
				for county in d['counties']:
					for demcandidate in dem:
						demvote += county['results'][demcandidate]
					for repcandidate in rep:
						repvote += county['results'][repcandidate]
					#print(d['path'] + " " + str(county['fips']) + " " + str(county['votes']) + " " + county['name'] + " " + str(demvote) + " " + str(repvote))
				writer.writerow([d['state_id'], d['race_name'], d['seat'], demvote, repvote])


def get_change(current, previous):
    if current == previous:
        return 100.0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 0

def get_votefrac(first, seccond):
	try:
		return first / (first + seccond)
	except ZeroDivisionError:
		return 0

def runcountystats():
	dem_true = []
	dem_frac_true = []
	dem_predict = []
	dem_frac_predict = []
	dem_pdiff = []
	rep_true = []
	rep_frac_true = []
	rep_predict = []
	rep_frac_predict = []
	rep_pdiff = []

	with open("2016HouseResultsCountyCheck.csv", "r") as file:
		reader = csv.reader(file)
		for row in reader:
			dtrue = float(row[8])
			dpredict = float(row[9])
			rtrue = float(row[10])
			rpredict = float(row[11])

			dem_frac_true.append(get_votefrac(dtrue, rtrue))
			dem_frac_predict.append(get_votefrac(dpredict, rpredict))
			rep_frac_true.append(get_votefrac(rtrue, dtrue))
			rep_frac_predict.append(get_votefrac(rpredict, dpredict))

			dem_true.append(dtrue)
			dem_predict.append(dpredict)
			dem_pdiff.append(get_change(dtrue, dpredict))
			rep_true.append(rtrue)
			rep_predict.append(rpredict)
			rep_pdiff.append(get_change(rtrue,rpredict))

	print("D MSE:" + str(mean_squared_error(dem_true, dem_predict)))
	print("R MSE:" + str(mean_squared_error(rep_true, rep_predict)))

	print("D MSE:" + str(mean_squared_error(dem_frac_true, dem_frac_predict)))
	print("R MSE:" + str(mean_squared_error(rep_frac_true, rep_frac_predict)))

	print("D Average % Difference:" + str(np.mean(dem_pdiff)))
	print("R Average % Difference:" + str(np.mean(rep_pdiff)))

def rundistrictstats():
	districtresults = []
	with open("election_simulation_results.csv", "r") as file:
		reader = csv.reader(file)
		for row in reader:
			districtresults.append(row)

	with open("2018HouseDistrictResults.csv", "r") as file:
		reader = csv.reader(file)
		for row in reader:
			for d in districtresults:
				if row[0] == d[0] and d[1] == "2018" and row[2] == d[3]:
					if float(row[3]) > float(row[4]) and float(d[4]) > float(d[5]):
						ok = 1
					elif float(row[3]) < float(row[4]) and float(d[4]) < float(d[5]):
						ok = 1
					else:
						print(row[0] + row[2] + " " + row[3] + " " + d[4] + " " + row[4] + " " + d[5])


def main():
	#formatresults()
	#aggregate()
	#checkcounty()
	#runcountystats()
	districtresults()
	#rundistrictstats()

if __name__ == "__main__":
    main()