###################################################################################################
# Simple example of how to call Ambari rest-api (non-kerberized)
###################################################################################################
import traceback
import time
import requests
import json
import sys
from pprint import pprint
from datetime import datetime

STATUS_ERROR="ERROR"
STATUS_OK="OK"
max_trys = 3 # Number of trys to reach a flume agent before assuming dead
sleep_sec = 5 # Seconds to sleep between trys
user = 'admin'
passwd = 'admin'	
host = "sandbox.hortonworks.com:34546"
out_file = "/tmp/agents.json"
#dttm="{:%Y-%m-%d %H:%M:%S}".format(datetime.now())
dttm=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print (dttm)

##################################################################################################
# Function to load agent metadata 
##################################################################################################
def getAgents():
	# TODO: read from file
	agents = {
		'Agent1': {'host':'sandbox.hortonworks.com:35455','date':'','status':'', 'metrics':{}}, 
		'Agent2': {'host':'sandbox.hortonworks.com:34546','date':'','status':'', 'metrics':{}},
                'Agent3': {'host':'sandbox.hortonworks.com:34547','date':'','status':'', 'metrics':{}}
		}
	return agents
	
##################################################################################################
# Function to check results and send alerts
##################################################################################################
def checkAgents(agents):
	msg = ""
	
	for key, value in agents.iteritems():
		print (key, str(value['status']))
		if (str(value['status']) == STATUS_ERROR):
			msg = msg + "Unable to reach agent " + str(key) + " at " + str(value['host']) + "\n"

	if (msg != ""):
		print "Errors found in Flume Agents"
		print msg	
		# TODO: Email
		
	return

##################################################################################################
# Function to check whether a flume agent can be contacted using the json rest api
##################################################################################################
def checkFlumeAgent(user, passwd, host):
	api_url = 'http://' + host + '/metrics'
	session = requests.Session()
	session.auth = (user,passwd)
	session.headers.update({'X-Requested-By': user})
	
	r = None
	trys = 0
	success = False
	
	# Try to connect several times if needed with sleep in between
	while (trys < max_trys and success == False):
		trys = trys+1
		
		try:
			print 'Connecting to ' + api_url + ' (attempt ' + str(trys) + ')'
			r = session.get(api_url, verify=False)
			success = True
			print 'Successfully connected to ' + api_url
		except Exception as e:
			print 'Error connecting to ' + api_url
			#print traceback.format_exc()
			print 'Sleeping for ' + str(sleep_sec) + ' seconds...'
			time.sleep(sleep_sec)

	if (success == False):
		print 'Unable to connect to ' + api_url + ' max trys exceeded.'
		return None
	else:	
		return r.json()
	
##################################################################################################
# Main - Create a list of Agents to be monitored, check them, and print results
##################################################################################################
if __name__ == "__main__":
	requests.packages.urllib3.disable_warnings()
	
	agents = getAgents()

	metrics = None
	for key, value in agents.items():
		metrics = checkFlumeAgent(user, passwd, str(value['host']))
		agents[key]['date'] = dttm
		if metrics is None:
			agents[key]['status'] = STATUS_ERROR
		else:	
			agents[key]['metrics'] = metrics
			agents[key]['status'] = STATUS_OK
			
	checkAgents(agents)

	pprint(agents)
	
	with open(out_file, "w") as outfile:
		json.dump(agents, outfile)
