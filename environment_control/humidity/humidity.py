
import json
import time
from MyMQTT import MyMQTT
import requests
import cherrypy

class humidity_web:
    exposed = True
    def __init__(self):
        pass
    # to allow catalog check online or offline
    def GET(self,*uri):
        if len(uri)!=0:
            command = str(uri[0])
            if command == "online":
                pass

class humidity:
    def __init__(self, clientID, sub_topic, pub_topic, broker, port, count):
        self.client = MyMQTT(clientID, broker, port, self)
        self.sub_topic = sub_topic
        self.pub_topic = pub_topic
        self.count = count
        self.status = None

    def start(self):
        self.client.start()
        self.client.mySubscribe(self.sub_topic)

    def stop(self):
        self.client.stop()

    def notify(self, sub_topic, msg):
        d = json.loads(msg)
        # print(d)
        self.humid = d['humidity']

        # retrive information of the activated farm
        try:
            get_activated_farm_uri = "http://192.168.1.14:8888/getActivatedFarm"
            response = requests.get(get_activated_farm_uri)
            farmDic = response.json()
            farmList = farmDic["e"]
            this_farm = farmList[self.count]  # {'farmID': '', 'farmName': ''}

        except:
            print("Wrong!")

        # register humidity on catalog
        registration_humidity_uri = "http://192.168.1.14:8888/addHumidity"
        humidity_data = {"farmID":this_farm['farmID'],
                        "farmName":this_farm['farmName'],
                        "value":[self.humid],
                        "unit":"%"}
        res = requests.post(registration_humidity_uri, json=humidity_data)

        try:
            with open('humidity_log.json') as file:
                dic = json.load(file)
            dic['e'][0]['v'].append(self.humid)
            with open('humidity_log.json', 'w') as file:
                json.dump(dic, file)
        except:
            dic = {
                "bn":"humidity",
                "e":[
                    {
                    "v":[],
                    "u":"%"
                    }
                ]
            }
            dic['e'][0]['v'].append(self.humid)
            with open('humidity_log.json', 'w') as file:
                json.dump(dic, file)

        print(self.humid)
        # publish command
        self.publish()

    def publish(self):
        high_threshold = 70
        low_threshold = 50


        # retrive predicted humidity
        try:
            get_activated_farm_uri = "http://192.168.1.14:8888/getHumidityPred"
            response = requests.get(get_activated_farm_uri)
            farmDic = response.json()
            farmList = farmDic["e"]
            this_farm = farmList[self.count]  # {'farmID': '', 'farmName': '','value':[, , , ]}
            pred_humidity = this_farm['value'][-1]

        except:
            pred_humidity = '0'
            print("Wrong!")


        value = 0.7*eval(self.humid) + 0.3 * eval(pred_humidity)
        print(value)

        try:
            if value <= low_threshold:
                command = "on"
            elif value >= high_threshold:
                command = "off"
            else:
                command = "off"
        except:
            command = "off"
    
        self.client.myPublish(self.pub_topic,command)

        try:
            with open('humidity_command_log.json') as file:
                dic = json.load(file)
            dic["e"].append(command)
            with open('humidity_command_log.json','w') as file:
                json.dump(dic, file)
        except:
            dic = {
                "bn":"humidity_command_log",
                "e":[]
            }
            dic["e"].append(command)
            with open('humidity_command_log.json','w') as file:
                json.dump(dic, file)
                
        print(command)

        # register mechanism status
        registration_mechanism_uri = "http://192.168.1.14:8888/addMechanismStatus"
        mechanism_data = {"farmID":this_farm['farmID'],
                        "farmName":this_farm['farmName'],
                        "mechanism":"watering",
                        "status":command
                        }
        res = requests.post(registration_mechanism_uri, json=mechanism_data)
        
        time.sleep(1)

    