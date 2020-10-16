import requests
from bs4 import BeautifulSoup
import json
import csv
from sets import Set

def scrape2016():
	path = "ListOfHouseDistricts.csv"
	districts = Set()
	with open(path) as file:
		reader = csv.reader(file)
		for row in reader:
			districts.add((row[0], row[1]))

	#with open("2016HouseLinks.csv", "w") as output:
	#	writer = csv.writer(output, lineterminator="\n")
	#	links = []
	#	for district in districts:
	#		state = district[0]
	#		number = district[1]
	#		url = 'https://www.nytimes.com/elections/2016/results/' + state.lower().replace(" ", "-")
	#		response = requests.get(url)
	#		html = response.content
	#		if number == 'At Large':
	#			number = '1'
	#		search = state.lower().replace(" ", "-") + '-house-district-' + number.lower().replace(" ", "-")
	#		a = html.find(search)
	#		s1 = 'www'
	#		b = html.rfind(s1, 0, a)
	#		c = html.find('>',a)
	#		link = html[b:c-1]
	#		if a == -1:
	#			print(district)
	#		else:
	#			print(link)
	#			links.append((district, link))
	#			writer.writerow([district[0], district[1], link])
	#
	#print(len(links))

	links = []
	with open("2016HouseLinks.csv") as file:
		reader = csv.reader(file)
		for row in reader:
			links.append(((row[0], row[1]),row[2]))

	remainingDistricts = districts.copy()
	with open("2016HouseResults.txt", "w") as text_file:
		for link in links:
			district = link[0]
			url = 'https://'+link[1]
			response = requests.get(url)
			html = response.content

			soup = BeautifulSoup(html, features="lxml")

			s1 = "eln_races ="
			s2 = "eln_forecast_feed"
			scripts = soup.find_all('script')
			for script in scripts:
				if "eln_races" in str(script):
					#print(script.string)
					print(district)
					remainingDistricts.remove(district)
					a = script.string.find(s1)
					b = script.string.find(s2)
					result = script.string[a+len(s1):b].strip()[1:-2].encode('utf-8').strip()
					text_file.write(str(result)+"\n")

		print("-----------------------------")
		for district in remainingDistricts:
			print(district)
			text_file.write(str(district)+"\n")#

def scrape2018():
	path = "ListOfHouseDistricts.csv"
	districts = Set()
	with open(path) as file:
		reader = csv.reader(file)
		for row in reader:
			districts.add((row[0], row[1]))

	remainingDistricts = districts.copy()
	with open("2018HouseResults.txt", "w") as text_file:
		for district in districts:
			#url = 'https://www.nytimes.com/elections/results/north-carolina-house-district-1'
			url = 'https://www.nytimes.com/elections/results/' + district[0].lower().replace(" ", "-") + "-house-district-" + district[1].lower().replace(" ", "-")
			response = requests.get(url)
			html = response.content
			
			soup = BeautifulSoup(html, features="lxml")
			
			s1 = "eln_races ="
			s2 = "eln_forecast_feed"
			scripts = soup.find_all('script')
			for script in scripts:
				if "eln_races" in str(script):
					#print(script.string)
					print(district)
					remainingDistricts.remove(district)
					a = script.string.find(s1)
					b = script.string.find(s2)
					result = script.string[a+len(s1):b].strip()[1:-2].encode('utf-8').strip()
					text_file.write(str(result)+"\n")
		
		print("-----------------------------")
		for district in remainingDistricts:
			print(district)
			text_file.write(str(district)+"\n")

	#d = json.loads(result)
	#print(d['race_id'])

def main():
	#scrape2016()
	scrape2018()

if __name__ == "__main__":
    main()