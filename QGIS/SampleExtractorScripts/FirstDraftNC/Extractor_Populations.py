import numpy as np
import os

#Choose where to save the output files with FPATH
#Choose a marker to identify the outputs. 
#   All files outputted will then be of the form MARKERxxxx.txt
SLASH = '/' #for macs, set SLASH = '/'; for windows '\\'
PPATH = '/Users/g/Projects/NC_StateLeg/'
FPATH = PPATH+'Data/ExtractedData'
DPATH = PPATH+'Data/PopulationData'

MARKERS      = ["Wake",
                "Cumberland",
                "Mecklenburg"]
electionType =  "StateSenate"
atomicUnit   =  "CensusBlocks"
popDataFileNm=  "R2011_Block.tab"
LAYER_NAMES  = [MARKER+atomicUnit+electionType for MARKER in MARKERS]

wholeCountyFIPS = [69,93,-1]

#create output directories if needed
for MARKER in MARKERS:
    directory = FPATH+SLASH+MARKER
    if not os.path.exists(directory):
        os.makedirs(directory)

for ind in range(len(LAYER_NAMES)):
    print "Working on map", MARKERS[ind]
    LAYER_NAME = LAYER_NAMES[ind]
    MARKER     = MARKERS[ind]
        
    #Set up output files 
    fgeoID     = open(FPATH+SLASH+MARKER+SLASH+MARKER+'GEOID.txt', "r")
    geoIDToInd = {l.rstrip().split("\t")[1] : int(l.split("\t")[0]) for l in fgeoID}
    fgeoID.close()
    
    fpopData = open(DPATH+SLASH+popDataFileNm,"r")
    keyLine      = fpopData.readline().rstrip().split("\t")
    totPopInd    = keyLine.index('\"PL10AA_TOT\"')  #total pop
    blackPopInd  = keyLine.index('\"PL10AA_SR_B\"') #black pop
    totRegInd    = keyLine.index('\"REG10G_TOT\"')  #total registration
    totDemRegInd = keyLine.index('\"REG10G_D\"')    #dem registration
    totRepRegInd = keyLine.index('\"REG10G_R\"')    #rep registration
    indexMap = [totPopInd,blackPopInd,totRegInd,totDemRegInd,totRepRegInd]

    totCountData = np.zeros(len(indexMap))
    countyWData  = np.zeros(len(indexMap))
    countyPData  = np.zeros(len(indexMap))
    countData    = np.zeros((len(geoIDToInd),len(indexMap)))

    for line in fpopData:
        splitline   = line.rstrip().split("\t")
        #add to totals
        for i in range(len(indexMap)):
            totCountData[i]+=int(splitline[indexMap[i]])
        #add to extract data
        geoIDAtomic = splitline[0][1:-1] # strip the quotes
        countyFIPs  = int(geoIDAtomic[0:5])
        store_huh   = False
        if (37000+wholeCountyFIPS[ind])==countyFIPs:
            #keep this county whole
            geoID     = str(countyFIPs)
            store_huh = True
            for i in range(len(indexMap)):
                countyWData[i]+=int(splitline[indexMap[i]])
        elif geoIDAtomic in geoIDToInd:
            #separate counties
            geoID     = geoIDAtomic
            store_huh = True
            for i in range(len(indexMap)):
                countyPData[i]+=int(splitline[indexMap[i]])
        if store_huh:
            fid   = geoIDToInd[geoID]-1
            for i in range(len(indexMap)):
                countData[fid,i]+=int(splitline[indexMap[i]])
    fpopData.close()
    print "State wide totals", totCountData
    print "Whole county wide totals", countyWData
    print "Partitioned county wide totals", countyPData
    
    fblack = open(FPATH+SLASH+MARKER+SLASH+MARKER+'BLACK.txt', "w")
    fpop   = open(FPATH+SLASH+MARKER+SLASH+MARKER+'POPULATION.txt', "w")
    freg10 = open(FPATH+SLASH+MARKER+SLASH+MARKER+'VOTEREGISTRATION10.txt', "w")
    for fid in range(len(geoIDToInd)):
        fblack.write('\t'.join([str(fid+1),str(countData[fid,1])])+'\n')
        fpop.write  ('\t'.join([str(fid+1),str(countData[fid,0])])+'\n')
        freg10.write('\t'.join([str(fid+1),str(countData[fid,2]),
                                           str(countData[fid,3]),
                                           str(countData[fid,4])])+'\n')    
    fblack.close()
    fpop.close()
    freg10.close()

print "Finished finding populations and registration counts (2010)"
