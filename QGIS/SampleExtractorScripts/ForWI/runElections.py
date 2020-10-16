import numpy as np
from glob import glob

electionDataDir = "./WICuratedData/"
elections = [ "WardsVOTESWSA12-PRE12USS12USH12.txt",
              "WardsVOTESWSA14-GOV14WAG14.txt",
              #"WardsVOTESWSA14-GOV14WAG14USH14.txt",
              #"WardsVOTESGOV12.txt",
			  #"WardsVOTESGOV14.txt",
			  #"WardsVOTESPRE12.txt",
			  #"WardsVOTESPRE16.txt",
			  #"WardsVOTESSOS14.txt",
			  #"WardsVOTESTRS14.txt",
			  #"WardsVOTESUSH12.txt",
			  #"WardsVOTESUSH14.txt",
			  #"WardsVOTESUSS12.txt",
			  #"WardsVOTESUSS16.txt",
			  #"WardsVOTESWAG12.txt",
			  #"WardsVOTESWAG14.txt",
			  #"WardsVOTESWSA12-USH12.txt",
			  #"WardsVOTESWSA12-USS12.txt",
			  #"WardsVOTESWSA12-USS12USH12.txt",
			  #"WardsVOTESWSA12.txt",
			  #"WardsVOTESWSA14-GOV14USH14.txt",
			  #"WardsVOTESWSA14-GOV14WAG14.txt",
			  #"WardsVOTESWSA14-GOV14WAG14USH14.txt",
			  #"WardsVOTESWSA14-USH14.txt",
			  #"WardsVOTESWSA14-WAG14.txt",
			  #"WardsVOTESWSA14.txt",
			  "WardsVOTESWSA16-PRE16USS16.txt",
			  #"WardsVOTESWSA16-USS16.txt",
			  #"WardsVOTESWSA16.txt",
			  #"WardsVOTESWSS12.txt",
			  #"WardsVOTESWSS16.txt"
              #"WardsVOTESWSA16-PRE16USS16.txt"
            ]
#districtingDirPattern = "../out/P_iC_comp_mino/kaluza/out_p2200_idealcounty0p6_comp0p8_mino100_H20KL20K/"
#listOfDistrictDirs = glob(districtingDirPattern+"*AGGL/")
#print len(listOfDistrictDirs)


#districtingDirPattern = "./out_p2200_tsp005_idealcounty0p6_comp0p8_mino100_H20KL20K/"
districtingDirPattern = "./out_p2200_idealcounty0p6_comp0p8_mino100_H20KL20K/"
listOfDistrictDirs = glob(districtingDirPattern+"*ALLNEWAGGL/")

electionLength = 120000
skipNumberElec = 10

#count the number of wards (healed for donuts)
felec = open(electionDataDir+elections[0],"r")
noWards=0
for line in felec:
	noWards+=1
felec.close()
electionData = np.empty((len(elections),noWards,2))

print noWards

#read in the election data
elecInd = 0
for elec in elections:
	felec   = open(electionDataDir+elec,"r")
	for line in felec:
		splitline = map(int,line.split("\t"))
		ind = splitline[0]-1
		electionData[elecInd,ind,0] = splitline[1]
		electionData[elecInd,ind,1] = splitline[2]
	felec.close()
	elecInd+=1
	print elec, sum(electionData[elecInd-1,:,0]),sum(electionData[elecInd-1,:,1])

noDists = 99
votes   = np.empty((len(elections),noDists,2),dtype=float)

fmargins = []
fresults = []
for elec in elections:
	fmargins.append(open(districtingDirPattern+"MCMCElectionMargins_ALLNEW_"+elec,"w"))
	fresults.append(open(districtingDirPattern+"MCMCElectionResults_ALLNEW_"+elec,"w"))

distDirInd = 0
for districtDir in listOfDistrictDirs:
	print "Run", distDirInd, "out of", len(listOfDistrictDirs)
	distDirInd += 1
	districtMaps = glob(districtDir+"districtmaps/districtMap*.txt")
	for districtMap in districtMaps:
		#print districtDir, districtMap
		distInd      = int(districtMap[len(districtDir+"districtmaps/districtMap"):-len(".txt")])
		if distInd>electionLength*skipNumberElec:
			#run elections
			votes[:,:,:] = 0
			districtingFile = open(districtMap)
			for line in districtingFile:
				splitline = map(int,line.split("\t"))
				for elecInd in range(len(elections)):
					votes[elecInd,splitline[1]-1,0] += electionData[elecInd,splitline[0],0]
					votes[elecInd,splitline[1]-1,1] += electionData[elecInd,splitline[0],1]
			districtingFile.close()
			for elecInd in range(len(elections)):
				#print "election index", elecInd, elections[elecInd]
				noDems = 0
				for dist in range(noDists):
					margin = float(votes[elecInd,dist,0])/float(votes[elecInd,dist,0]+votes[elecInd,dist,1])
					if margin > 0.5:
						noDems += 1
					fmargins[elecInd].write("\t".join([str(dist+1),str(margin)])+"\n")
				fresults[elecInd].write(str(noDems)+"\n")

for elecInd in range(len(elections)):
	fmargins[elecInd].close()
	fresults[elecInd].close()








