#written by Bobby Vogler 
#date created: 12/15/2023
#purpose of script: to disable/enable all host monitoring at once in an environment
#how to use: schedule this script to run at selected time and edit the "monitoring" variable for enablement (true), or disablement (false)
#API token permissions required: Read entities, Write Settings, Ingest events
import requests 
import time

#variables
#############################################################################################################################
#either do true of false here
monitoring = "false"
apiToken = "dt0c01.#########"
apiToken = "API-Token "+apiToken+""
envUrl = "https://wsf#####.apps.dynatrace.com"
headers1 = {
  'Content-Type': 'application/json; charset=utf-8',
  'Accept': 'application/json; charset=utf-8',
  'Authorization': apiToken
}

#GET call with alerts
#############################################################################################################################
#making a GET request for list of host ID's in the environment within the last day
url = ""+envUrl+"/api/v2/entities?entitySelector=type%28%22HOST%22%29&from=now-1d"
r = requests.get(url, headers= headers1)

#check status code for response received
print("GET RESPONSE CODE: " + str(r) )


#if status code is not 200 create an environment wide alert stating API failed
if (r.status_code != 200):
    print ("Sending custom alert to environment")
    #get time in UTC milliseconds for posting event
    ms = time.time_ns() // 1_000_000
    ms = str(ms)
    url = ""+envUrl+"/api/v2/events/ingest"
    alertMessage = "API Call failed to retrieve list of host ID's: Failing on step 1 (GET) when enabling"
    payload = "{\r\n  \"eventType\": \"CUSTOM_ALERT\",\r\n  \"startTime\": "+ms+",\r\n  \"timeout\": 30,\r\n  \"title\": \""+alertMessage+"\"\r\n}"
    rError = requests.request("POST", url, headers=headers1, data=payload)
    #check status code for response received
    print("EVENT RESPONSE CODE: " + str(rError) )
    


#POST call with alerts
#############################################################################################################################
#making a POST API to use the lists of hosts to flip toggle switch for monitoring
url = ""+envUrl+"/api/v2/settings/objects?validateOnly=false"

#payload blank template
payload = ""

#selecting only the hostId from previous API call and building request payload
i = len(r.json()['entities'])
for x in range(i):
    #print(r.json()['entities'][x]['entityId'])
    #print("\n")
    hostId = r.json()['entities'][x]['entityId']
    payloadText = "{\"schemaId\":\"builtin:host.monitoring\",\"schemaVersion\":\"1.4\",\"scope\":\""+hostId+"\",\"value\":{\"enabled\":"+monitoring+"}}"
    payload = ""+payload+","+payloadText+""
    #print (payload)

#remove the leading , from payload
payload = payload[1:]

#add on brackets to front and back for formatting 
payload = "["+payload+"]"

#send POST request
r = requests.request("POST", url, headers=headers1, data=payload)
print("POST RESPONSE CODE: " + str(r) )

#if status code is not 200 create an environment wide alert stating API failed
if (r.status_code != 200):
    print ("Sending custom alert to environment")
    #get time in UTC milliseconds for posting event
    ms = time.time_ns() // 1_000_000
    ms = str(ms)
    url = ""+envUrl+"/api/v2/events/ingest"
    alertMessage = "API Call failed to retrieve list of host ID's: Failing on step 2 (POST) when enabling"
    payload = "{\r\n  \"eventType\": \"CUSTOM_ALERT\",\r\n  \"startTime\": "+ms+",\r\n  \"timeout\": 30,\r\n  \"title\": \""+alertMessage+"\"\r\n}"
    rError = requests.request("POST", url, headers=headers1, data=payload)
    #check status code for response received
    print("EVENT RESPONSE CODE: " + str(rError) )


