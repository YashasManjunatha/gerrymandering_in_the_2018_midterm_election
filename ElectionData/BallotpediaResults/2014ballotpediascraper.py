from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv

page = "https://ballotpedia.org/United_States_House_of_Representatives_elections,_2014"

driver = webdriver.Chrome('C:/Users/Mitra Kiciman/Documents/Downloads/chromedriver_win32/chromedriver.exe')
driver.implicitly_wait(30)
driver.get(page)

show_button = driver.find_element_by_id("collapseButton0")
show_button.click()

soup = BeautifulSoup(driver.page_source, 'lxml')
results = soup.find(id="collapsibleTable0")
output = []
outFile = 'C:/Users/Mitra Kiciman/Documents/gerrymanderingimpact/2014_elections_margins.csv'
#table = pd.read_html(str(results), header=0)[0]
#table.to_csv('C:/Users/Mitra Kiciman/Documents/gerrymanderingimpact/2016_elections_margins.csv')
for row in results.find('tbody').find_all("tr"):
	cols = row.find_all("td")
	if "at-large" in cols[0].get_text().lower():
		apostrophe = cols[0].get_text().find('\'')
		state = cols[0].get_text()[1:apostrophe]
		district = "01"
	else:
		index = cols[0].get_text().find('District')
		state = cols[0].get_text()[1:index-1]
		district = cols[0].get_text()[index+9:]
		district = district.strip()
		if len(district) > 2:
			district = district[0:2].strip()
		if len(district) == 1:
			district = "0" + district
			print(district)
	link = cols[1].find("a")['href']
	party = link[1:link.find("_")]
	margin = cols[2].get_text().replace("%", "").strip()
	votes = cols[3].get_text().strip().replace(",", "")
	if cols[4].find("a") != None:
		opponent = cols[4].find("a").get_text().strip()
	else:
		opponent = cols[4].get_text().strip()
	output.append([state, district, party, margin, votes, opponent])

driver.quit()

with open(outFile, mode='w') as file:
	writer = csv.writer(file, lineterminator="\n")
	writer.writerow(['state', 'district', 'winning party', 'margin', 'votes', 'opponent'])
	for row in output:
		writer.writerow(row)