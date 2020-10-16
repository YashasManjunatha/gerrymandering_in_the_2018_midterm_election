import numpy as np

districtToConvert = open("../districtMap0.txt","r")
newDistID = []
for line in districtToConvert:
	newDistID.append(map(int, line.rstrip().split())[1])
districtToConvert.close()

mapNewToOld = open("../WICuratedData/SuperWardsToWards.txt","r")
WardDists = []
j = 0
for line in mapNewToOld:
	toInds = map(int, line.rstrip().split())
	dist = newDistID[j]
	j+=1
	for ind in toInds[1:]:
		while len(WardDists)<ind:
			WardDists.append(0)
		WardDists[ind-1]=dist
mapNewToOld.close()

mapOldToNew = open("../districtMapOld.txt","w")
for i in range(len(WardDists)):
	if WardDists[i]==0:
		print "error - ward district is left unassigned in conversion"
	else:
		mapOldToNew.write(str(WardDists[i]))
		mapOldToNew.write("\n")
mapOldToNew.close()