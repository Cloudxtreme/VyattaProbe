import requests, json, commands, pickle, sys
from requests.exceptions import ConnectionError
#Config
url = "http://localhost/py/"

#Variable Defs
commandList = []
payload = []
headers = {'content-type': 'application/json'}

#Method Defs
def execute(command):
	status, output = commands.getstatusoutput(command)
	return status, output

def writeList(list):
	data = open('data','w')
	pickle.dump(list,data)
	data.close()

def readList():
	ret = []
	try:
		data = open('data','r')
		ret = pickle.load(data)
		data.close()
	except IOError:
		print("ERR: Command file does not exist.")
	except EOFError:
		print("ERR: Command file empty.")
	return ret

def generatePayload(commandList):
	payload = {}
	for commandArr in commandList:
		print("Running command " + str(commandArr[0]) + " : " + commandArr[1])
		payload['c' + str(commandArr[0])] = commandArr[1] #Save original command in payload.
		status, output = execute(command=commandArr[1])
		if commandArr[2]:
			#Send command output.
			payload['o' + str(commandArr[0])] = output
		payload['s' + str(commandArr[0])] = status
	return payload


def refreshList():
	r = requests.post(url + "getCommands.php")
	j = json.loads(r.text)
	return j

commandList = readList()

if not commandList:
	#Run refresh...
	print("Command list empty, reading new one from server:")
	try:
		commandList = refreshList()
		writeList(commandList)
	except ConnectionError:
		print("ERR: Could not connect to server.")
		sys.exit(1)
	except (AttributeError, ValueError):
		print("ERR: Could not read command list.")
		sys.exit(1)
	print("Done")

#Generate the payload.
payload = generatePayload(commandList)


try:
	r = requests.post(url + "test.php", data=json.dumps(payload),headers=headers)

	if (r.status_code == requests.codes.ok):
		#Response is good.. Check reply.
		if(r.text == "refresh"):
			#Refresh
			print("Server has updated command list.  Clearing current.")
			writeList([])
		elif(r.text == "ok"):
			#All went well.
			print("Ok")
		else:
			#Do not understand
			print("ERR: Could not read Response: " + r.text)
	else:
		#Response is bad.. couldn't contact?
		print("ERR: Server returned status code: " + r.status_code)
except ConnectionError:
	print("ERR: Could not connect to server.")