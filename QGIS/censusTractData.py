import ftplib
import os
import zipfile

try:
	ftp = ftplib.FTP('ftp2.census.gov')
	ftp.login()
	print 'Connection successful'
except ftplib.all_errors, e:
	errorcode_string = str(e).split(None, 1)[0]
	print errorcode_string

ftp.cwd('/geo/tiger/TIGER2017/TRACT/')
print 'Current dir: %s' % ftp.pwd()  

files = ftp.nlst()

directoryName = 'CensusTractData'

if not os.path.exists(directoryName):
	os.makedirs(directoryName)
fileList = os.listdir(directoryName)

directoryPath = '%s/%s' % (os.getcwd(), directoryName)
os.chdir(directoryPath)

for file in files:
	if file not in fileList:
		f = open(file, 'wb')
		try:
			ftp.retrbinary('RETR %s' % file, f.write)
			print 'Downloaded %s' % file
		except ftplib.all_errors, e:
			errorcode_string = str(e).split(None, 1)[0]
			print errorcode_string
		f.close()
		
	with zipfile.ZipFile(file) as zip:
		file = file.split(".")[0]
		extractPath = directoryPath + '/' + file
		if not os.path.exists(extractPath):
			os.makedirs(extractPath)
		zip.extractall(extractPath)

ftp.close()
