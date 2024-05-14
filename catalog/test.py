

import requests

def checkoffline(webport):
    baseUri = "http://0.0.0.0:"
    uri = baseUri + str(webport) + '/online'
    req = requests.get(uri)
    print(req)

# get service list
ServiceListUri = "http://0.0.0.0:8888/getServiceList"
delete_uri = "http://0.0.0.0:8888/deleteService"
req = requests.get(ServiceListUri)
serviceList = req.json()['e']
print(serviceList)
for i in serviceList:

    service = i['service']
    print(f"checking {service}")
    port = i['port']
    data = {"service":service, "port":port}
    try:
        checkoffline(port)
    except:
       print("delete")
       response = requests.delete(delete_uri,json = data)
       
       



