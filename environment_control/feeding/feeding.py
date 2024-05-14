from MyMQTT import MyMQTT
import time
import json
import requests

class feeding_web:
    exposed = True
    def __init__(self):
        pass
    # to allow catalog check online or offline
    def GET(self,*uri):
        if len(uri)!=0:
            command = str(uri[0])
            if command == "online":
                pass

# subscript command from telegram bot
class feeding:
    def __init__(self, clientID, sub_topic, pub_topic, broker, port, count):
        self.client = MyMQTT(clientID, broker, port, self)
        self.sub_topic = sub_topic
        self.pub_topic = pub_topic
        self.status = None
        self.count = count

    def start(self):
        self.client.start()
        self.client.mySubscribe(self.sub_topic)

    def stop(self):
        self.client.stop()

    def notify(self, sub_topic, msg):
        d = json.loads(msg)
        print("timer received")

        self.publish()
        print("command publisged")

    def publish(self):
        message  = "fer_on"
        self.client.myPublish(self.pub_topic,message)
        
        time.sleep(1)

                # retrive information of the activated farm
        try:
            get_activated_farm_uri = "http://0.0.0.0:8888/getActivatedFarm"
            response = requests.get(get_activated_farm_uri)
            farmDic = response.json()
            farmList = farmDic["e"]
            this_farm = farmList[self.count]  # {'farmID': '', 'farmName': ''}

        except:
            print("Wrong!")

        # register mechanism status
        registration_mechanism_uri = "http://0.0.0.0:8888/addMechanismStatus"
        mechanism_data = {"farmID":this_farm['farmID'],
                        "farmName":this_farm['farmName'],
                        "mechanism":"fertilizer",
                        "status":"fer_on"
                        }
        res = requests.post(registration_mechanism_uri, json=mechanism_data)
        
        time.sleep(1)