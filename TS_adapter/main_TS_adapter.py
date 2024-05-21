from TS_adapter import TS_humidity_sub, TS_temperature_sub , TS_humidity_pred_sub, TS_temperature_pred_sub
from TS_adapter_web import TS_adapter_web
import requests
import os
import cherrypy
import json
import time


# start thingspeak adapter web service
conf = {
'/': {
  'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
  'tools.staticdir.root': os.path.abspath(os.getcwd()),
  'tools.sessions.on': True
  },
}
TS_adapter_web_service = TS_adapter_web()
cherrypy.tree.mount(TS_adapter_web_service, '/', conf)
cherrypy.config.update({'server.socket_host': '0.0.0.0'})
cherrypy.config.update({'server.socket_port': 8080})
cherrypy.engine.start()


# register service
delete_uri = "http://192.168.1.14:8888/deleteService"
registration_uri = "http://192.168.1.14:8888/registrationServie"
data = {"service":"TS_adapter", "port":8080}
response = requests.post(registration_uri,json = data)

# retrieve message broker
base_uri = "http://192.168.1.14:8888"
r = "/getBrocker"
res = requests.get(base_uri + r)
conf = res.json()

# get current farm ID
get_current_farm_uri = base_uri + "/getCurrentFarm"
res = requests.get(get_current_farm_uri)
currentFarm = res.json()
currentFarmID = currentFarm["CurrentFarm"][0]['farmID']
print(currentFarmID)

# get activated farm ID
get_activated_farm_uri = "http://192.168.1.14:8888/getActivatedFarm"
response = requests.get(get_activated_farm_uri)
farmDic = response.json()
farmList = farmDic["e"]

count = 0
for i in range(len(farmList)):
    if farmList[i]['farmID'] == currentFarmID:
        count = i
        break
    else:
        continue  

pre_ID = count

broker = conf["test_broker"]
port = conf["port"]
topic = conf["baseTopic"]["TS_adapter"][0] + str(count)
TS_humidity_sub = TS_humidity_sub("TS_humidity_sub"+str(count), topic, broker, port)
TS_humidity_sub.start()

broker = conf["test_broker"]
port = conf["port"]
topic = conf["baseTopic"]["TS_adapter"][1] + str(count)
TS_temperature_sub = TS_temperature_sub("TS_temperature_sub"+str(count), topic, broker, port)
TS_temperature_sub.start()

broker = conf["test_broker"]
port = conf["port"]
topic = conf["baseTopic"]["TS_adapter"][2] + str(count)
TS_humidity_pred_sub = TS_humidity_pred_sub("TS_humidity_pred_sub"+str(count), topic, broker, port)
TS_humidity_pred_sub.start()

broker = conf["test_broker"]
port = conf["port"]
topic = conf["baseTopic"]["TS_adapter"][3] + str(count)
TS_temperature_pred_sub = TS_temperature_pred_sub("TS_temperature_pred_sub"+str(count), topic, broker, port)
TS_temperature_pred_sub.start()

base_url = 'https://api.thingspeak.com/update?api_key=VUV0KZ2FWCBO69QY&'

t = 5 #second

while True:  
    # humidity
    with open('humidity.json') as file:
        dic = json.load(file)
    humidity = eval(dic['e'][0])
    humidity_res = requests.get(base_url+f'field2={humidity}')
    print(f"humidity is {humidity} and {humidity_res}")

    time.sleep(t)

    with open('humidity_pred.json') as file:
        dic = json.load(file)
    humidity_pred = eval(dic['e'][0])
    humidity_pred_res = requests.get(base_url+f'field4={humidity_pred}')
    print(f"humidity_pred is {humidity_pred} and {humidity_pred_res}")

    time.sleep(t)

    with open('temperature.json') as file:
        dic = json.load(file)
    temperature = eval(dic['e'][0])
    temperature_res = requests.get(base_url+f'field1={temperature}')
    print(f"temperature is {temperature} and {temperature_res}")

    time.sleep(t)

    with open('temperature_pred.json') as file:
        dic = json.load(file)
    temperature_pred = eval(dic['e'][0])
    temperature_pred_res = requests.get(base_url+f'field3={temperature_pred}')
    print(f"temperature_pred is {temperature_pred} and {temperature_pred_res}")

    time.sleep(t)
    
    # if keyboard.is_pressed('space'):
    #     print('space was pressed! Service stoped!')
    #     response = requests.delete(delete_uri,json = data)
    #     break
    # else:
    #     pass
