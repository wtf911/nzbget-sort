#!/usr/bin/python 

##############################################################################
### NZBGET SCAN SCRIPT 												       ###

# Sort files inside of a NZB.
#
# This script sorts the files inside of a NZB so
# that .rar files are in order before the NZB is added to the queue.
#
# NOTE: This script requires Python to be installed on your system.

### NZBGET SCAN SCRIPT 			   									       ###
##############################################################################

# By wtf911 for use with NZBGet

import sys, os, xml.dom.minidom, shutil

if os.environ['NZBNP_FILENAME'][-14:] == "00single00.nzb":
	print "[NZB] NZBPR_*unpack:=no"
	print "test"
	quit()

# Load the XML string
fp = open(os.environ['NZBNP_FILENAME'])
xml_string = fp.read()
fp.close()

# Parse the NZB with minidom
dom = xml.dom.minidom.parseString(xml_string)

# Stop if file contains a RAR
for line in dom.getElementsByTagName("file"):
	if ".rar" in line.getAttribute("subject"):
		quit()
		
# Create a backup of the NZB
backup = os.environ['NZBNP_FILENAME'] + ".processed"

shutil.copy2(os.environ['NZBNP_FILENAME'], backup) 

# Strip all but one segment of each file
for line in dom.getElementsByTagName("segment"):
	if line.getAttribute("number") != "1":
		line.parentNode.removeChild(line)
	
fp = open(os.environ['NZBNP_FILENAME'], 'w')
	
for line in dom.toxml(encoding=dom.encoding).split('\n'):
	if not line.strip() == '':
		fp.write(line + '\n')

fp.close()

# Rename
newnzbname = os.environ['NZBNP_NZBNAME'][:-4] + "00single00" + ".nzb"
newfilename = os.environ['NZBNP_DIRECTORY'] + "\\" + newnzbname
os.rename(os.environ['NZBNP_FILENAME'], newfilename)