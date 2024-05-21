import time
import json
import requests
from MyMQTT import MyMQTT

# base_url = 'https://api.thingspeak.com/update?api_key=VUV0KZ2FWCBO69QY&'
# t = 5 #second

# subscript information from raspberry
class TS_humidity_sub:
    def __init__(self, clientID, topic, broker, port):
        self.client = MyMQTT(clientID, broker, port, self)
        self.topic = topic
        self.status = None
    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)
    def stop(self):
        self.client.stop()
    def notify(self, topic, msg):
        d = json.loads(msg)
        self.humidity = d['humidity']
        dic = {
                "bn":"humidity_log",
                "e":[]
            }
        dic["e"].append(self.humidity)
        with open('humidity.json','w') as file:
            json.dump(dic, file)

        # humidity = eval(self.humidity)
        # humidity_res = requests.get(base_url+f'field2={humidity}')
        # print(f"humidity is {humidity} and {humidity_res}")
        # time.sleep(t)

class TS_temperature_sub(TS_humidity_sub):
    def notify(self, topic, msg):
        d = json.loads(msg)
        self.temperature = d['temperature']

        dic = {
                "bn":"temperature_log",
                "e":[]
            }
        dic["e"].append(self.temperature)
        with open('temperature.json','w') as file:
            json.dump(dic, file)

        # temperature = eval(self.temperature)
        # temperature_res = requests.get(base_url+f'field1={temperature}')
        # print(f"temperature is {temperature} and {temperature_res}")
        # time.sleep(t)

class TS_humidity_pred_sub(TS_humidity_sub):
    def notify(self, topic, msg):
        d = json.loads(msg)
        self.humidity_pred = d['humidity_pred']

        dic = {
                "bn":"humidity_pred_log",
                "e":[]
            }
        dic["e"].append(self.humidity_pred)
        with open('humidity_pred.json','w') as file:
            json.dump(dic, file)
        # humidity_pred = eval(humidity_pred)
        # humidity_pred_res = requests.get(base_url+f'field4={humidity_pred}')
        # print(f"humidity_pred is {humidity_pred} and {humidity_pred_res}")
        # time.sleep(t)

class TS_temperature_pred_sub(TS_humidity_sub):
    def notify(self, topic, msg):
        d = json.loads(msg)
        self.temperature_pred = d['temperature_pred']
        dic = {
                "bn":"temperature_pred_log",
                "e":[]
            }
        dic["e"].append(self.temperature_pred)
        with open('temperature_pred.json','w') as file:
            json.dump(dic, file)

        # temperature_pred = eval(temperature_pred)
        # temperature_pred_res = requests.get(base_url+f'field3={temperature_pred}')
        # print(f"temperature_pred is {temperature_pred} and {temperature_pred_res}")
        # time.sleep(t)

