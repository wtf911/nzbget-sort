#!/usr/bin/python 

##############################################################################
### NZBGET SCAN SCRIPT 												       ###

# Sort files inside of the NZB.
#
# This script sorts the files inside of a NZB
# so that .rar files are in order.
#
# NOTE: This script requires Python to be installed on your system.

### NZBGET SCAN SCRIPT 			   									       ###
##############################################################################

# Originally by Bertrand Janin
# https://github.com/tamentis/nzbsort
# Modified by wtf911 for use with NZBGet

import sys, os, xml.dom.minidom

# Load the XML string
fp = open(os.environ['NZBNP_FILENAME'])
xml_string = fp.read()
fp.close()

# Parse the NZB with minidom
dom = xml.dom.minidom.parseString(xml_string)

# Get a sorted list of XML elements to push back to the NZB
nzb = dom.getElementsByTagName("nzb")[0]
files = dom.getElementsByTagName("file")

def get_filename(f):
	subject = f.getAttribute("subject")
	if '"' in subject:
		tokens = subject.split('"')
		if len(tokens) == 3:
			subject = tokens[1]
	return subject

sorted_files = sorted(files, key=get_filename)

# If we have one rar file in the mix, keep it for later so we can
# push it to the top, if we have more than one, do nothing
rar_file = None
for f in sorted_files:
	if ".rar" in f.getAttribute("subject"):
		if rar_file is not None:
			rar_file = None
			break
		rar_file = f

# Push the elements one by one to the end, putting them in order
first_file = None
while sorted_files:
	f = sorted_files.pop(0)
	if first_file is None:
		first_file = f
	nzb.insertBefore(f, None)

if rar_file is not None:
	nzb.insertBefore(rar_file, first_file)
	
fp = open(os.environ['NZBNP_FILENAME'], 'w')
	
for line in dom.toxml(encoding=dom.encoding).split('\n'):
	if not line.strip() == '':
		fp.write(line + '\n')

fp.close()