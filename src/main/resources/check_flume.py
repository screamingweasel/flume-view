###################################################################################################
# Simple example of how to call Ambari rest-api (non-kerberized)
###################################################################################################
import traceback
import time
import requests
import json
import sys
import syslog
import smtplib
from email.mime.text import MIMEText
from pprint import pprint
from datetime import date
from datetime import datetime

STATUS_ERROR="ERROR"
STATUS_OK="OK"
max_trys = 3 # Number of trys to reach a flume agent before assuming dead
sleep_sec = 5 # Seconds to sleep between trys
user = 'ambari'
passwd = 'ambari@123'	
out_file = "/tmp/agents.json"
agent_file = "./check_flume.json"

# Mail Related constants
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "email@gmail.com"
SMTP_PASSWORD = "yourpassword"

EMAIL_TO = ["ms683k@att.com", "jbarnett@hortonworks.com"]
EMAIL_FROM = "ms683k@att.com"
EMAIL_SUBJECT = "Flume Agent Alerts"
DATE_FORMAT = "%d/%m/%Y"
EMAIL_SPACE = ", "

dttm=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

##################################################################################################
# Function to load agent metadata 
##################################################################################################
def getAgents():

	try:
		print "Loading agents from " + agent_file 
		agents = json.loads(open(agent_file).read())
	except:
		print "Error opening agent configuration file: " + str(sys.exc_info()[0])
		sys.exit()
	
	return agents
	
##################################################################################################
# Function to load agent metadata 
##################################################################################################
def sendEmail(msg):
	print "Sending alert email..."

	try:
		msg = MIMEText(msg)
		msg['Subject'] = EMAIL_SUBJECT
		msg['To'] = EMAIL_SPACE.join(EMAIL_TO)
		msg['From'] = EMAIL_FROM
		mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
		#mail.starttls()
		mail.login(SMTP_USERNAME, SMTP_PASSWORD)
		mail.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
		mail.quit()
	except:
		print "Error sending email: " + str(sys.exc_info()[0])
	finally:
		return
	
##################################################################################################
# Function to check results and send alerts
##################################################################################################
def checkAgents(agents):
	msg = ""
	
	for key, value in agents.iteritems():
		print (key, str(value['status']))
		if (str(value['status']) == STATUS_ERROR):
			errMsg = "Unable to reach agent " + str(key) + " at " + str(value['host'])
			syslog.syslog(syslog.LOG_ERR, errMsg)
			msg = msg + errMsg + "\n"

	if (msg != ""):
		print "Errors found in Flume Agents"
		print msg	
		sendEmail(msg)
		
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
	print str(sys.argv[0]) + " starting at " + dttm
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

	with open(out_file, "w") as outfile:
		json.dump(agents, outfile)
		
	dttm=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print str(sys.argv[0]) + " completed at " + dttm