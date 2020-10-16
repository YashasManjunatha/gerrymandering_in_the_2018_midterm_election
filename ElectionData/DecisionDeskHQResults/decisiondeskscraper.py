from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv

def login(driver):
	driver.find_element_by_css_selector('div.signup-box.first > button').click()
	driver.find_element_by_css_selector('div.login-actions > span > a').click()
	driver.find_element_by_css_selector('input[aria-label="Email"]').send_keys("mitra.kiciman@gmail.com")
	driver.find_element_by_css_selector('input[aria-label="Password"]').send_keys("Hersheys123")
	driver.find_element_by_css_selector('form[novalidate="novalidate"] > button').click()

def generateCountyDistrictMap(abbrev):
	map = dict()
	with open("C:/Users/Mitra Kiciman/Documents/gerrymanderingimpact/redistricting-atlas-data/county_assignments.csv", "r") as file:
		reader = csv.reader(file)
		next(reader, None)
		for row in reader:
			if row[2] == "current":
				if abbrev[row[1]].lower() not in map:
					map[abbrev[row[1]].lower()] = dict()
					curr = map[abbrev[row[1]].lower()]
				district = row[5]
				if len(district) == 1:
					district = "0" + district
				if district not in curr:
					curr[district] = []
				curr[district].append(row[4])

	return map

page = "https://results.decisiondeskhq.com/"

driver = webdriver.Chrome('C:/Users/Mitra Kiciman/Documents/Downloads/chromedriver_win32/chromedriver.exe')
driver.implicitly_wait(15)
driver.get(page)

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

countyDistrictMap = generateCountyDistrictMap(abbrev)
urls = []
for state in us_state_abbrev:
	s = state.lower()
	if s not in countyDistrictMap:
		urls.append("https://results.decisiondeskhq.com/general/" + s.replace(" ", "_") + "/house_" + "00")
		print(urls[len(urls)-1])
	else:
		for dist in countyDistrictMap[s]:
			urls.append("https://results.decisiondeskhq.com/general/" + s.replace(" ", "_") + "/house_" + dist)
			print(urls[len(urls)-1])

print(len(urls))

outputRows = []
for url in urls:
	driver.get(url)
	if len(driver.find_elements_by_css_selector("div.signup-container")) > 0:
		login(driver)
	url = url.split("/")
	district = url[-1].split("_")[1]
	state = url[-2].replace("_", " ")
	if district == "00":
		district = "01"
	print(state, district)
	table = driver.find_elements_by_tag_name("table")
	if state in countyDistrictMap and len(countyDistrictMap[state][district]) == 1:
		demVotes = 0
		repVotes = 0
		otherVotes = 0
		for row in table[0].find_elements_by_css_selector("tbody > tr"):
			cols = row.find_elements_by_tag_name("td")
			party = cols[0].find_element_by_tag_name("i").get_attribute("style")
			print(party)
			votes = cols[2].get_attribute('innerHTML').replace(",", "")
			if party == "color: rgb(250, 49, 56); font-size: 1.2em;":
				repVotes += int(votes)
			elif party == "color: rgb(87, 174, 166); font-size: 1.2em;":
				otherVotes += int(votes)
			elif party == "color: rgb(102, 171, 207); font-size: 1.2em;": 
				demVotes += int(votes)
		county = countyDistrictMap[state][district][0].replace(" County", "")
		print(county, demVotes, repVotes, otherVotes)
		outputRows.append([state, county, district, demVotes, repVotes, otherVotes])	
	else:
		try:
			demIndex = False
			repIndex = False
			otherIndex = False
			header = table[1].find_elements_by_css_selector("thead > tr > th")
			for i in range(len(header)):
				#print(header[i].get_attribute("aria-label"))
				party = header[i].get_attribute("aria-label")
				if party:
					party = party.find("(")
				else:
					party = -1
				if party != -1:
					if header[i].get_attribute("aria-label")[party+1:party+2] == "D":
						if not demIndex:
							demIndex = []
						demIndex.append(i)
					elif header[i].get_attribute("aria-label")[party+1:party+2] == "R":
						if not repIndex:
							repIndex = []
						repIndex.append(i)
				if header[i].get_attribute("aria-label") and header[i].get_attribute("aria-label").find("Other") != -1:
					if not otherIndex:
						otherIndex = []
					otherIndex.append(i)
				print(demIndex, repIndex, otherIndex)

			
			for row in table[1].find_elements_by_css_selector("tbody > tr"):
				demVotes = 0
				repVotes = 0
				otherVotes = 0
				cols = row.find_elements_by_tag_name("td")
				print("County: " + cols[1].get_attribute("innerHTML"))
				county = cols[1].get_attribute("innerHTML")
				print("Total Votes: " + cols[3].get_attribute("innerHTML"))
				if demIndex:
					for i in demIndex:
						demPercent = float(cols[i].get_attribute("innerHTML").split("%")[0])/100
						#print("DemVotes: " + str(round(demPercent*int(cols[3].get_attribute("innerHTML").replace(",", "")))))
						demVotes += round(demPercent*int(cols[3].get_attribute("innerHTML").replace(",", "")))
				if repIndex: 
					for i in repIndex:
						repPercent = float(cols[i].get_attribute("innerHTML").split("%")[0])/100
						#print("RepVotes: " + str(round(repPercent*int(cols[3].get_attribute("innerHTML").replace(",", "")))))
						repVotes += round(repPercent*int(cols[3].get_attribute("innerHTML").replace(",", "")))
				if otherIndex:
					for i in otherIndex:
						otherPercent = float(cols[i].get_attribute("innerHTML").split("%")[0])/100
						#print("OtherVotes: " + str(round(otherPercent*int(cols[3].get_attribute("innerHTML").replace(",", "")))))
						otherVotes += round(otherPercent*int(cols[3].get_attribute("innerHTML").replace(",", "")))
				print(demVotes, repVotes, otherVotes)
				outputRows.append([state, county, district, demVotes, repVotes, otherVotes])	
		except:
			print("error")
			outputRows.append([state, "error", district, "error", "error", "error"])
		
driver.quit()

outFile = "C:/Users/Mitra Kiciman/Documents/gerrymanderingimpact/2018electionresults.csv"
with open(outFile, mode = "w") as file:
	writer = csv.writer(file, lineterminator="\n")
	writer.writerow(["State", "County", "District", "DemVotes", "RepVotes", "OtherVotes"])
	for row in outputRows:
		writer.writerow(row)