import numpy as np
import os

#Choose where to save the output files with FPATH
#Choose a marker to identify the outputs. 
#   All files outputted will then be of the form MARKERxxxx.txt
SLASH = '/' #for macs, set SLASH = '/'; for windows '\\'
PPATH = '/Users/g/Projects/NC_StateLeg/'
FPATH = PPATH+'Data/ExtractedData'
DPATH = PPATH+'Data/DistrictingData'

MARKERS      = ["Wake",
                "Cumberland",
                "Mecklenburg"]
electionType =  "StateSenate"
atomicUnit   =  "CensusBlocks"
popDataFileNm=  "R2011_Block.tab"
LAYER_NAMES  = [MARKER+atomicUnit+electionType for MARKER in MARKERS]

wholeCountyFIPS = [69,93,-1]
YEARS = [2011,2017]

#create output directories if needed
for MARKER in MARKERS:
    directory = FPATH+SLASH+MARKER
    if not os.path.exists(directory):
        os.makedirs(directory)

for year_ind in range(len(YEARS)):
    print "Working on year", YEARS[year_ind]   
    YEAR       = YEARS[year_ind]    
    for ind in range(len(LAYER_NAMES)):
        print "Working on map", MARKERS[ind]
        LAYER_NAME = LAYER_NAMES[ind]
        MARKER     = MARKERS[ind]
        
        #Set up output files 
        fgeoID     = open(FPATH+SLASH+MARKER+SLASH+MARKER+'GEOID.txt', "r")
        geoIDToInd = {l.rstrip().split("\t")[1] : int(l.split("\t")[0]) \
                      for l in fgeoID}
        fgeoID.close()
        
        fdistData = open(DPATH+SLASH+electionType+SLASH+str(YEAR)+
                         electionType+"DistrictBy"+atomicUnit+".csv","r")
        keyLine         = fdistData.readline() #burn the keyline
        districtData    = np.empty(len(geoIDToInd))
        districtData[:] = -1 #flag "not yet assigned" 

        for line in fdistData:
            splitline   = line.rstrip().split(",")
            #add to extract data
            geoIDAtomic = splitline[0][1:-1] # strip the quotes
            countyFIPs  = int(geoIDAtomic[0:5])
            store_huh   = False
            if (37000+wholeCountyFIPS[ind])==countyFIPs:
                #keep this county whole
                geoID     = str(countyFIPs)
                store_huh = True
            elif geoIDAtomic in geoIDToInd:
                #separate counties
                geoID     = geoIDAtomic
                store_huh = True
            if store_huh:
                fid   = geoIDToInd[geoID]-1
                oldData = districtData[fid]
                districtData[fid]=int(splitline[1][1:-1])
                if oldData!=-1 and oldData!=districtData[fid]:
                    print "error - district reassignment in whold county",
                    print f.id(), geoID, splitline
                    exit()
        fdistData.close()
    
        fdist = open( FPATH+SLASH+MARKER+SLASH+MARKER+'DIST' \
                     +electionType.upper()+str(YEAR)+'.txt', "w")
        foundDists = []
        for fid in range(len(geoIDToInd)):
            if districtData[fid]==-1:
                print "error - atomic unit was never assigned to a district",
                print fid, geoID
                exit()
            if not districtData[fid] in foundDists:
                foundDists.append(districtData[fid])
            localInd = foundDists.index(districtData[fid])
            fdist.write('\t'.join([str(fid+1),str(localInd),
                                   str(int(districtData[fid]))])+'\n')
        fdist.close()
    
print "Finished finding populations and registration counts (2010)"
