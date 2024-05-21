
import json
import time
from MyMQTT import MyMQTT
import requests
import torch
from torch import nn
import cherrypy


class temerature_pred_web:
    
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
class temperature_pred:
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
        self.temperature = d['temperature']

        try:
            with open('temperature_log.json') as file:
                dic = json.load(file)
            dic['temperature'].append(self.temperature)
            with open('temperature_log.json', 'w') as file:
                json.dump(dic, file)
        except:
            dic = {'temperature':[]}
            dic['temperature'].append(self.temperature)
            with open('temperature_log.json', 'w') as file:
                json.dump(dic, file)

 
        data = torch.tensor([0.0, 0.0, 0.0])

        try:
            with open('temperature_log.json') as file:
                dic = json.load(file)
            data = torch.tensor([eval(dic['temperature'][-3])
                                    ,(eval(dic['temperature'][-2]))
                                        ,eval(dic['temperature'][-1])])
        except:
            data = torch.tensor([0.0, 0.0, 0.0])

        DNN_temperature = torch.load("./DNN_temperature.pt")
        # data = torch.tensor(data)
        pred = DNN_temperature(data).item()
        pred_temperature = format(pred, '.2f')

        # retrive information of the activated farm
        try:
            get_activated_farm_uri = "http://192.168.1.14:8888/getActivatedFarm"
            response = requests.get(get_activated_farm_uri)
            farmDic = response.json()
            farmList = farmDic["e"]
            this_farm = farmList[self.count]  # {'farmID': '', 'farmName': ''}

        except:
            print("Wrong!")

        # register predicrion on catalog
        registration_temperature_uri = "http://192.168.1.14:8888/addTemperaturePredicted"
        predicted_temperature_data = {"farmID":this_farm['farmID'],
                        "farmName":this_farm['farmName'],
                        "value":[pred_temperature],
                        "unit":"degree"}
        res = requests.post(registration_temperature_uri, json = predicted_temperature_data)


        # store temperature predicted
        try:
            with open('temperature_pred_log.json') as file:
                dic = json.load(file)
            dic["temperature_pred"].append(pred_temperature)
            with open('temperature_pred_log.json','w') as file:
                json.dump(dic, file)
        except:
            dic = {"temperature_pred":[]}
            dic["temperature_pred"].append(pred_temperature)
            with open('temperature_pred_log.json','w') as file:
                json.dump(dic, file)

                  
        print(pred_temperature)


        
        time.sleep(1)

class TS_temperature_pub():
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
            with open('temperature_log.json') as file:
                dic = json.load(file)
            data = torch.tensor([eval(dic['temperature'][-3])
                                    ,(eval(dic['temperature'][-2]))
                                        ,eval(dic['temperature'][-1])])
        except:
            data = torch.tensor([0.0, 0.0, 0.0])

        DNN_temperature = torch.load("./DNN_temperature.pt")
        # data = torch.tensor(data)
        pred = DNN_temperature(data).item()
        pred_temperature = format(pred, '.2f')

        message  = {'temperature_pred':[]}
        message['temperature_pred']=str(pred_temperature)
        self.client.myPublish(self.topic,message)
        time.sleep(1)
    