

import time
import requests

ID = 2
ActivatedFarmUri = "http://0.0.0.0:8888/getActivatedFarm"
req = requests.get(ActivatedFarmUri)
ActivatedFarmList = req.json()['e']

serviceID = 0
for i in range(len(ActivatedFarmList)):
    if ActivatedFarmList[i]['farmID'] == ID:
        serviceID = i
        
print(serviceID)

