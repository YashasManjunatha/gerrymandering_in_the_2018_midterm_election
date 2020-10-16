import requests
from bs4 import BeautifulSoup
import json
import csv

path = "ListOfHouseDistricts.csv"
districts = set()
with open(path) as file:
	reader = csv.reader(file)
	for row in reader:
		districts.add((row[0], row[1]))

remainingDistricts = districts.copy()
with open("2018HouseResults.txt", "w") as text_file:
	#for district in districts:
	url = 'https://www.nytimes.com/elections/results/north-carolina-house-district-1'
	#url = 'https://www.nytimes.com/elections/results/' + district[0].lower().replace(" ", "-") + "-house-district-" + district[1].lower().replace(" ", "-")
	response = requests.get(url)
	html = response.content
	
	soup = BeautifulSoup(html, features="lxml")
	
	s1 = '<span class="eln-party-display">'
	s2 = "eln_forecast_feed"
	
	a = soup.get_text().find(s1)
	b = soup.get_text().find(s2)

	print(soup.get_text()[a:50])
	print(soup.get_text()[b:50])

		#scripts = soup.find_all('script')
		#for script in scripts:
		#	if "eln_races" in str(script):
		#		#print(script.string)
		#		print(district)
		#		remainingDistricts.remove(district)
		#		a = script.string.find(s1)
		#		b = script.string.find(s2)
		#		result = script.string[a+len(s1):b].strip()[1:-2].encode('utf-8').strip()
		#		text_file.write(str(result)+"\n")
	
	#print("-----------------------------")
	#for district in remainingDistricts:
	#	print(district)
	#	text_file.write(str(district)+"\n")