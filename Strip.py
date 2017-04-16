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
# Sorting portion by tamentis
# API portion by hugbug

import os, xml.dom.minidom, shutil, sys, re

try:
	from xmlrpclib import ServerProxy # python 2
except ImportError:
	from xmlrpc.client import ServerProxy # python 3

# First we need to know connection info: host, port and password of NZBGet server.
# NZBGet passes all configuration options to post-processing script as
# environment variables.
host = os.environ['NZBOP_CONTROLIP'];
port = os.environ['NZBOP_CONTROLPORT'];
username = os.environ['NZBOP_CONTROLUSERNAME'];
password = os.environ['NZBOP_CONTROLPASSWORD'];

if host == '0.0.0.0': host = '127.0.0.1'

# Build an URL for XML-RPC requests
rpcUrl = 'http://%s:%s@%s:%s/xmlrpc' % (username, password, host, port);

# Create remote server object
server = ServerProxy(rpcUrl)

# Check if the NZB has already been stripped
if os.environ['NZBNP_FILENAME'][-14:] == "00single00.nzb":
	print "[NZB] NZBPR_*Unpack:=no"
	print "[NZB] NZBPR_*naming=nzb"
	quit()

# Load the XML string
fp = open(os.environ['NZBNP_FILENAME'])
xml_string = fp.read()
fp.close()

# Parse the NZB with minidom
dom = xml.dom.minidom.parseString(xml_string)

# Delete stripped from history
history = server.history()
oldname = os.environ['NZBNP_NZBNAME'][:-4] + "00single00"

for entry in history:
	match = re.search( oldname, entry['Name'])
	if match:
		server.editqueue('HistoryFinalDelete', '', entry['NZBID'])
		
# Check if it was already post-processed
fp = open(os.environ['NZBNP_FILENAME'])
s = fp.readlines()
fp.close()

for line in s:
	if "post-processed by NZBGet" in line:

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
		
		print "[NZB] NZBPR_*naming=nzb"
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