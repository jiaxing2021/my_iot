

import requests


get_activated_farm_uri = "http://0.0.0.0:8888/getHumidityPred"
response = requests.get(get_activated_farm_uri)
farmDic = response.json()
print(farmDic)
farmList = farmDic["e"]
print(farmList)
this_farm = farmList[1]  # {'farmID': '', 'farmName': '','value':[, , , ]}
print(this_farm)
pred_humidity = this_farm['value'][-1]
print(pred_humidity)