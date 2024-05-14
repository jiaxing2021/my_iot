

import requests

base_uri = "http://0.0.0.0:8888"

get_current_farm_uri = base_uri + "/getCurrentFarm"
res = requests.get(get_current_farm_uri)
currentFarm = res.json()
currentFarmID = currentFarm["CurrentFarm"][0]['farmID']


get_activated_farm_uri = "http://0.0.0.0:8888/getActivatedFarm"
response = requests.get(get_activated_farm_uri)
farmDic = response.json()
farmList = farmDic["activatedFarmID"]
count = 0
for i in range(len(farmList)):
    if farmList[i]['farmID'] == currentFarmID:
        break
    else:
        count += 1

print(count)
