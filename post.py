#!/usr/bin/python 

##############################################################################
### NZBGET POST-PROCESSING SCRIPT 									       ###

# Sort files inside of a NZB.
#
# This script sorts the files inside of a NZB so
# that .rar files are in order before the NZB is added to the queue.
#
# NOTE: This script requires Python to be installed on your system.

### NZBGET POST-PROCESSING SCRIPT 			   						       ###
##############################################################################

# By wtf911 for use with NZBGet
# API portion by hugbug

import os, xml.dom.minidom, sys, re, shutil

try:
	from xmlrpclib import ServerProxy # python 2
except ImportError:
	from xmlrpc.client import ServerProxy # python 3
	
# If this is not a stripped NZB then stop
if os.environ['NZBPP_NZBNAME'][-10:] != "00single00":
	quit()

# Exit codes used by NZBGet
POSTPROCESS_SUCCESS=93
POSTPROCESS_NONE=95
POSTPROCESS_ERROR=94

# Check if the script is called from nzbget 15.0 or later
if not 'NZBOP_NZBLOG' in os.environ:
	print('*** NZBGet post-processing script ***')
	print('This script is supposed to be called from nzbget (15.0 or later).')
	sys.exit(POSTPROCESS_ERROR)

if not os.path.exists(os.environ['NZBPP_DIRECTORY']):
	print('Destination directory doesn\'t exist, exiting')
	sys.exit(POSTPROCESS_NONE)

# To get the item log we connect to NZBGet via XML-RPC and call
# method "loadlog", which returns the log for a given nzb item.
# For more info visit http://nzbget.net/RPC_API_reference

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

# Call remote method 'loadlog'
nzbid = int(os.environ['NZBPP_NZBID'])
log = server.loadlog(nzbid, 0, 10000)

# Now iterate through entries and save them to the output file
if len(log) > 0:
	f = open('%s/nzblog.txt' % os.environ['NZBPP_DIRECTORY'], 'w')
	for entry in log:
		f.write(entry['Text'] + '\n')
	f.close()

# Prepare the log for use
f = open('%s/nzblog.txt' % os.environ['NZBPP_DIRECTORY'])
s = f.readlines()
f.close()

# Load the XML string
backup = os.environ['NZBOP_MAINDIR'] + "\\nzb\\" + os.environ['NZBPP_NZBNAME'][:-10] + ".nzb.processed"
fp = open(backup)
xml_string = fp.read()
fp.close()

# Parse the NZB with minidom
dom = xml.dom.minidom.parseString(xml_string)

# Rename the files inside of the NZB
for line in s:
	match = re.match( r'Renaming (.*) to (.*)', line)
	if match:
		for line2 in dom.getElementsByTagName("file"):
			if match.group(1) in line2.getAttribute("subject"):
				line2.attributes["subject"].value = re.sub(match.group(1), match.group(2), line2.getAttribute("subject"))

# Save the modified NZB
fp = open(backup, 'w')
	
for line in dom.toxml(encoding=dom.encoding).split('\n'):
	if not line.strip() == '':
		fp.write(line + '\n')

fp.close()

# Add metadata
fp = open(backup)
contents = fp.readlines()
fp.close()

footer = '<!-- post-processed by NZBGet -->\n'
contents.insert(-2, footer)

fp = open(backup, 'w')
fp.writelines(contents)
fp.close()

# Rename
os.rename(backup, backup[:-10])

# Delete downloaded files
shutil.rmtree(os.environ['NZBPP_DIRECTORY'])

# Add it to the queue
addnzb = server.scan()

# Send exit status
sys.exit(POSTPROCESS_SUCCESS)