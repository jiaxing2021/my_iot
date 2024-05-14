import time
import json
import requests
from MyMQTT import MyMQTT

base_url = 'https://api.thingspeak.com/update?api_key=VUV0KZ2FWCBO69QY&'
t = 5 #second

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
        humidity = eval(self.humidity)
        print(humidity)
        humidity_res = requests.get(base_url+f'field2={humidity}')
        time.sleep(t)

class TS_temperature_sub(TS_humidity_sub):
    def notify(self, topic, msg):
        d = json.loads(msg)
        self.temperature = d['temperature']
        temperature = eval(self.temperature)
        print(temperature)
        temperature_res = requests.get(base_url+f'field1={temperature}')
        time.sleep(t)

class TS_humidity_pred_sub(TS_humidity_sub):
    def notify(self, topic, msg):
        d = json.loads(msg)
        humidity_pred = d['humidity_pred']
        humidity_pred = eval(humidity_pred)
        print(humidity_pred)
        humidity_pred_res = requests.get(base_url+f'field3={humidity_pred}')
        time.sleep(t)

class TS_temperature_pred_sub(TS_humidity_sub):
    def notify(self, topic, msg):
        d = json.loads(msg)
        temperature_pred = d['temperature_pred']
        temperature_pred = eval(temperature_pred)
        print(temperature_pred)
        temperature_pred_res = requests.get(base_url+f'field4={temperature_pred}')
        time.sleep(t)

