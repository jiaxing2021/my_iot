
import json
import time
from MyMQTT import MyMQTT
import requests
import cherrypy

class temperature_web:
    exposed = True
    def __init__(self):
        pass
    # to allow catalog check online or offline
    def GET(self,*uri):
        if len(uri)!=0:
            command = str(uri[0])
            if command == "online":
                pass

class temperature:
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
        self.temperature = d['temperature']

        try:
            get_activated_farm_uri = "http://0.0.0.0:8888/getActivatedFarm"
            response = requests.get(get_activated_farm_uri)
            farmDic = response.json()
            farmList = farmDic["e"]
            this_farm = farmList[self.count]  # {'farmID': '', 'farmName': ''}

        except:
            print("Wrong!")

        # register humidity on catalog
        registration_temperature_uri = "http://0.0.0.0:8888/addTemperature"
        temperature_data = {"farmID":this_farm['farmID'],
                        "farmName":this_farm['farmName'],
                        "value":[self.temperature],
                        "unit":"deg"}
        res = requests.post(registration_temperature_uri, json=temperature_data)

        try:
            with open('temperature_log.json') as file:
                dic = json.load(file)
            dic['e'][0]['v'].append(self.temperature)
            with open('temperature_log.json', 'w') as file:
                json.dump(dic, file)
        except:
            dic = {
                "bn":"temperature",
                "e":[
                    {
                    "v":[],
                    "u":"degree"
                    }
                ]
            }
            dic['e'][0]['v'].append(self.temperature)
            with open('temperature_log.json', 'w') as file:
                json.dump(dic, file)

        print(self.temperature)
        # publish command
        self.publish()

    def publish(self):
        high_threshold = 25
        low_threshold = 16

        # retrive predicted temperatre
        try:
            get_activated_farm_uri = "http://0.0.0.0:8888/getTemperaturePred"
            response = requests.get(get_activated_farm_uri)
            farmDic = response.json()
            farmList = farmDic["e"]
            this_farm = farmList[self.count]  # {'farmID': '', 'farmName': '','value':[, , , ]}
            pred_temperatre = this_farm['value'][-1]

        except:
            pred_temperatre = '0'
            print("Wrong!")


        value = 0.7*eval(self.temperature) + 0.3 * eval(pred_temperatre)
        print(value)


        try:
            if value <= low_threshold:
                command = ["heating on","cooling off"]
            elif value >= high_threshold:
                command = ["heating off","cooling on"]
            else:
                command = ["heating off","cooling off"]
        except:
            command = ["heating off","cooling off"]
    
        self.client.myPublish(self.pub_topic,command)

        try:
            with open('temperature_command_log.json') as file:
                dic = json.load(file)
            dic["e"].append(command)
            with open('temperature_command_log.json','w') as file:
                json.dump(dic, file)
        except:
            dic = {
                "bn":"temperature_control_com",
                "e":[]
            }
            dic["e"].append(command)
            with open('temperature_command_log.json','w') as file:
                json.dump(dic, file)

        # register mechanism status
        registration_mechanism_uri = "http://0.0.0.0:8888/addMechanismStatus"
        mechanism_data = {"farmID":this_farm['farmID'],
                        "farmName":this_farm['farmName'],
                        "mechanism":"heating and cooling",
                        "status":command
                        }
        res = requests.post(registration_mechanism_uri, json=mechanism_data)
        

        print(command)
        
        time.sleep(1)

    