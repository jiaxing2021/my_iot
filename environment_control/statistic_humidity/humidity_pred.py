
import json
import time
from MyMQTT import MyMQTT
import requests
import torch
from torch import nn
import cherrypy

class humidity_pred_web:
    exposed = True
    def __init__(self):
        pass
    # to allow catalog check online or offline
    def GET(self,*uri):
        if len(uri)!=0:
            command = str(uri[0])
            if command == "online":
                pass

class DNN(nn.Module):
    def __init__(self):
        super(DNN, self).__init__()
        self.fc1 = nn.Linear(3, 32)
        self.fc2 = nn.Linear(32, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(p=0.2)
        
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x

# subscribe humidity from rapberry and publish prediction to control part
class humidity_pred:
    def __init__(self, clientID, sub_topic, broker, port, count):
        self.client = MyMQTT(clientID, broker, port, self)
        self.sub_topic = sub_topic
        self.count = count
        self.status = None

    def start(self):
        self.client.start()
        self.client.mySubscribe(self.sub_topic)

    def stop(self):
        self.client.stop()

    def notify(self, sub_topic, msg):
        
        d = json.loads(msg)
        self.humidity = d['humidity']

        # save humidity
        try:
            with open('humidity_log.json') as file:
                dic = json.load(file)
            dic['humidity'].append(self.humidity)
            with open('humidity_log.json', 'w') as file:
                json.dump(dic, file)
        except:
            dic = {'humidity':[]}
            dic['humidity'].append(self.humidity)
            with open('humidity_log.json', 'w') as file:
                json.dump(dic, file)

        try:
            with open('humidity_log.json') as file:
                dic = json.load(file)
            data = torch.tensor([eval(dic['humidity'][-3])
                                    ,(eval(dic['humidity'][-2]))
                                        ,eval(dic['humidity'][-1])])
        except:
            data = torch.tensor([0.0, 0.0, 0.0])

        DNN_humidity = torch.load("./DNN_humidity.pt")
        # data = torch.tensor(data)
        pred = DNN_humidity(data).item()
        pred_humidity = format(pred, '.2f')

        # retrive information of the activated farm
        try:
            get_activated_farm_uri = "http://0.0.0.0:8888/getActivatedFarm"
            response = requests.get(get_activated_farm_uri)
            farmDic = response.json()
            farmList = farmDic["e"]
            this_farm = farmList[self.count]  # {'farmID': '', 'farmName': ''}

        except:
            print("Wrong!")

        # register prediction on catalog
        registration_humidity_uri = "http://0.0.0.0:8888/addHumidityPredicted"
        predicted_humidity_data = {"farmID":this_farm['farmID'],
                        "farmName":this_farm['farmName'],
                        "value":[pred_humidity],
                        "unit":"%"}
        res = requests.post(registration_humidity_uri, json = predicted_humidity_data)

        # save humidity predicted
        try:
            with open('humidity_pred_log.json') as file:
                dic = json.load(file)
            dic['e'][0]['v'].append(pred_humidity)
            with open('humidity_pred_log.json','w') as file:
                json.dump(dic, file)
        except:
            dic = {
                "bn":"humidity_pred_log",
                "e":[
                    {
                    "v":[],
                    "u":"%"
                    }
                ]
            }
            dic['e'][0]['v'].append(pred_humidity)
            with open('humidity_pred_log.json','w') as file:
                json.dump(dic, file)

                
        print(pred_humidity)

        time.sleep(1)

class TS_humidity_pub():
    def __init__(self, clientID, topic,broker,port):
        self.topic=topic
        self.client=MyMQTT(clientID,broker,port,None)
		
    def start (self):
        self.client.start()

    def stop (self):
        self.client.stop()

    def publish(self):

        data = torch.tensor([0.0, 0.0, 0.0])

        try:
            with open('humidity_log.json') as file:
                dic = json.load(file)
            data = torch.tensor([eval(dic['humidity'][-3])
                                    ,(eval(dic['humidity'][-2]))
                                        ,eval(dic['humidity'][-1])])
        except:
            data = torch.tensor([0.0, 0.0, 0.0])

        CNN_humidity = torch.load("./DNN_humidity.pt")
        # data = torch.tensor(data)
        pred = CNN_humidity(data).item()
        pred_humidity = format(pred, '.2f')

        message  = {'humidity_pred':[]}
        message['humidity_pred']=str(pred_humidity)
        self.client.myPublish(self.topic,message)
        time.sleep(1)