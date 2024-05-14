from TS_adapter import TS_humidity_sub, TS_temperature_sub , TS_humidity_pred_sub, TS_temperature_pred_sub
from TS_adapter_web import TS_adapter_web
import requests
import os
import cherrypy


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
delete_uri = "http://0.0.0.0:8888/deleteService"
registration_uri = "http://0.0.0.0:8888/registrationServie"
data = {"service":"TS_adapter", "port":8080}
response = requests.post(registration_uri,json = data)

# retrieve message broker
base_uri = "http://0.0.0.0:8888"
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
get_activated_farm_uri = "http://0.0.0.0:8888/getActivatedFarm"
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


while True:  
    pass  
    # if keyboard.is_pressed('space'):
    #     print('space was pressed! Service stoped!')
    #     response = requests.delete(delete_uri,json = data)
    #     break
    # else:
    #     pass
