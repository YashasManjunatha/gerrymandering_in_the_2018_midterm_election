from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv

page = "https://ballotpedia.org/United_States_House_of_Representatives_elections,_2012"

driver = webdriver.Chrome('C:/Users/Mitra Kiciman/Documents/Downloads/chromedriver_win32/chromedriver.exe')
driver.implicitly_wait(30)
driver.get(page)

show_button = driver.find_element_by_id("collapseButton0")
show_button.click()

soup = BeautifulSoup(driver.page_source, 'lxml')
results = soup.find(id="collapsibleTable0")
output = []
outFile = 'C:/Users/Mitra Kiciman/Documents/gerrymanderingimpact/2012_elections_margins.csv'
#table = pd.read_html(str(results), header=0)[0]
#table.to_csv('C:/Users/Mitra Kiciman/Documents/gerrymanderingimpact/2016_elections_margins.csv')
for row in results.find('tbody').find_all("tr"):
	cols = row.find_all("td")
	if len(cols) < 5:
		break
	if "at-large" in cols[0].get_text().lower():
		comma = cols[0].get_text().find(',')
		state = cols[0].get_text()[1:comma]
		district = "01"
	else:
		index = cols[0].get_text().find('District')
		state = cols[0].get_text()[1:index-2]
		district = int(cols[0].get_text()[index+9:])
		if district < 10:
			district = "0" + str(district)
			print(district)
		else:
			district = str(district)
	link = cols[1].find("a")['href']
	party = link[1:link.find("_")]
	margin = cols[2].get_text().replace("%", "").strip()
	votes = cols[3].get_text().strip().replace(",", "")
	opponent = cols[4].get_text().strip()
	output.append([state, district, party, margin, votes, opponent])

driver.quit()

with open(outFile, mode='w') as file:
	writer = csv.writer(file, lineterminator="\n")
	writer.writerow(['state', 'district', 'winning party', 'margin', 'votes', 'opponent'])
	for row in output:
		writer.writerow(row)