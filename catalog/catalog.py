import cherrypy
import json
import requests

    
class catalog:

    _cp_config = {"request.methods_with_bodies": ('POST', 'PUT', 'DELETE')}
    exposed = True
    def __init__(self):
        pass
    ## retrive information
    def GET(self,*uri):
        if len(uri) != 0:
            command = uri[0]
            # retrieve temp
            if command == "getTemperature":
                with open('temperature_log.json') as file:
                    dic = json.load(file)
                return json.dumps(dic)
            # retrieve humidity
            if command == "getHumidity":
                with open('humidity_log.json') as file:
                    dic = json.load(file)
                return json.dumps(dic)
            # retrieve predicted temperature
            if command == "getTemperaturePred":
                with open('temperature_pred_log.json') as file:
                    dic = json.load(file)
                return json.dumps(dic)
            # retrieve predicted temperature
            if command == "getHumidityPred":
                with open('humidity_pred_log.json') as file:
                    dic = json.load(file)
                return json.dumps(dic)
            # retrieve telegram bot token
            if command == 'getToken':
                with open('token.json') as file:
                    dic = json.load(file)
                return json.dumps(dic)
            # retrieve sensor setting
            if command == 'getSensor':
                with open('sensors.json') as file:
                    dic = json.load(file)
                return json.dumps(dic)
            # retrieve current farm for Thing Speak
            if command == 'getCurrentFarm':
                with open('currentFarm.json') as file:
                    dic = json.load(file)
                return json.dumps(dic)
            # retrieve farm list
            if command == 'getFarmList':
                with open('farmList.json') as file:
                    dic = json.load(file)
                return json.dumps(dic)
            # retrieve service list (contains activated service)
            if command == 'getServiceList':
                with open('serviceList.json') as file:
                    dic = json.load(file)
                return json.dumps(dic)
            # retrieve message broker setting
            # merging broker and port and topic
            # everything related to message broker is here
            if command == 'getBrocker':
                with open('message_brocker_settings.json') as file:
                    dic = json.load(file)
                return json.dumps(dic)
            # retrieve information of activated farm list
            if command == 'getActivatedFarm':
                with open('activatedFarmID.json') as file:
                    dic = json.load(file)
                return json.dumps(dic)
            # retrieve time for timer schedular
            if command == "getChatID":  
                with open('chatIDList.json') as files:
                    dic = json.load(files)
                return json.dumps(dic)
            # get time for time schedular
            if command == "getTime":
                with open('Timer.json') as file:
                    dic = json.load(file)
                return json.dumps(dic)
            # retrieve mechanism status
            if command == "getMechanismStatus":
                with open('MechanismStatus_log.json') as file:
                    dic = json.load(file)
                return json.dumps(dic)
            # retrieve suggested culture
            if command == "getSuggestedCulture":
                with open('suggestedCulture.json') as file:
                    dic = json.load(file)
                return json.dumps(dic)
                
        else:
            # return "wrong"
            return open("my_index.html")
    # unpdata setting
    def PUT(self,*uri):
        if len(uri) != 0:
            command = str(uri[0])
            # change current farm
            if command == 'change':
                updateFlag = False
                farm_dic = json.loads(cherrypy.request.body.read()) 
                currentID = farm_dic["currentFarmID"]
                with open("farmList.json") as farmListDic:
                    farmListDic = json.load(farmListDic)
                    farmList = farmListDic["e"]
                for i in farmList:
                    if i["farmID"] == currentID:
                        updateFlag = True
                        break
                if updateFlag:
                    dic = {"CurrentFarm":[]}
                    dic["CurrentFarm"].append(i)
                    with open('currentFarm.json','w') as file:
                        json.dump(dic, file)
                        # restart TS_adapter
                        TS_uri = "http://192.168.1.14:8080/restart"
                        res = requests.put(TS_uri)
            # change token
            if command == 'token':
                token = json.loads(cherrypy.request.body.read()) 
                dic = {"token":[]}
                dic["token"].append(token)
                with open("token.json",'w') as file:
                    json.dump(dic, file)
            # change sensor settings 
            if command == 'sensor':
                addSettingFlat = True
                # dic = {"sensors": [{"ID":"","Tnum":"", "Tport":[]}]}
                sensors = json.loads(cherrypy.request.body.read()) 
                ID = sensors['ID']
                SensorPortList = sensors['SensorPort'].split()
                
                dic_sensor = {"sensors": {"ID":"","SensorNum":"", "SensorPort":[]}}
                dic_sensor["sensors"]["ID"] = sensors['ID']
                dic_sensor["sensors"]["SensorNum"] = eval(sensors['SensorNum'])
                dic_sensor["sensors"]["SensorPort"] = SensorPortList
                if eval(sensors['SensorNum']) == len(SensorPortList):
                    try:
                        with open("sensors.json") as file:
                            dic = json.load(file)
                        for i in range(len(dic["sensors"])):
                            if ID == dic["sensors"][i]["ID"]:
                                dic["sensors"][i]["SensorNum"] = eval(sensors['SensorNum'])
                                dic["sensors"][i]["SensorPort"] = SensorPortList
                                print(dic)
                                with open("sensors.json",'w') as file:
                                    json.dump(dic, file)
                                addSettingFlat = False
                                break
                        if addSettingFlat:
                            # dic = {"sensors": [{"ID":"","Tnum":"", "Tport":[], "Hnum":"", "Hport": []}]}
                            dic["sensors"].append(dic_sensor["sensors"])
                            with open("sensors.json",'w') as file:
                                json.dump(dic, file)

                    except:
                        dic = {"sensors":[]}
                        dic["sensors"].append(dic_sensor["sensors"])
                        with open("sensors.json",'w') as file:
                            json.dump(dic, file)     
            # change activated farm
            if command == 'activatedFarm':
                ID_list = []
                dic = {
                    "bn":"activatedFarmID",
                    "e":[]
                }
                farm_dic = json.loads(cherrypy.request.body.read()) 
                print(farm_dic)
                activatesID = farm_dic["activatedFarmID"]
                with open("farmList.json") as farmListDic:
                    farmListDic = json.load(farmListDic)
                    farmList = farmListDic["e"]
                for i in farmList:
                    for j in activatesID:
                        if i["farmID"] == j:
                            ID_list.append(i)
                            break
                print(ID_list)
                for a in ID_list:
                    dic["e"].append(a)
                    with open('activatedFarmID.json','w') as file:
                        json.dump(dic, file)
            # set for timer schedular
            if command == 'timer':
                token = json.loads(cherrypy.request.body.read()) 
                dic = {"Timer":[]}
                dic["Timer"].append(token)
                with open("Timer.json",'w') as file:
                    json.dump(dic, file)  
    # add elements
    def POST(self,*uri):
        if len(uri) != 0:
            command = str(uri[0])
            # add temperature
            if command == 'addTemperature':
                body = json.loads(cherrypy.request.body.read())
                add_temperature_flag = True
                try: 
                    with open('temperature_log.json') as files:
                        dic = json.load(files)
                        for i in range(len(dic['e'])):
                            if dic['e'][i]['farmID'] == body['farmID']:
                                dic['e'][i]['value'].append(body['value'][0])
                                add_temperature_flag = False
                                with open('temperature_log.json','w') as file:
                                    json.dump(dic, file)
                                break
                        if add_temperature_flag:
                            dic['e'].append(body)
                            with open('temperature_log.json','w') as file:
                                json.dump(dic, file)
                except:
                    dic = {
                        "bn":"temperature_log",
                        "e":[]
                    }
                    dic["e"].append(body)
                    with open('temperature_log.json','w') as file:
                        json.dump(dic, file)
            # add humidity
            elif command == 'addHumidity':
                body = json.loads(cherrypy.request.body.read())
                add_humidity_flag = True
                try:
                    with open('humidity_log.json') as files:
                        dic = json.load(files)
                        for i in range(len(dic['e'])):
                            if dic['e'][i]['farmID'] == body['farmID']:
                                dic['e'][i]['value'].append(body["value"][0])
                                add_humidity_flag = False
                                with open('humidity_log.json','w') as file:
                                    json.dump(dic, file)
                                break
                        if add_humidity_flag:
                            dic['e'].append(body)
                            with open('humidity_log.json','w') as file:
                                json.dump(dic, file)
                except:
                    dic = {
                        "bn":"humidity_log",
                        "e":[]
                    }
                    dic["e"].append(body)
                    with open('humidity_log.json','w') as file:
                        json.dump(dic, file)
            # add temperature predicted
            elif command == 'addTemperaturePredicted':
                body = json.loads(cherrypy.request.body.read())
                add_temperature_flag = True
                try:
                    with open('temperature_pred_log.json') as files:
                        dic = json.load(files)
                        for i in range(len(dic['e'])):
                            if dic['e'][i]['farmID'] == body['farmID']:
                                dic['e'][i]['value'].append(body["value"][0])
                                add_temperature_flag = False
                                with open('temperature_pred_log.json','w') as file:
                                    json.dump(dic, file)
                                break
                        if add_temperature_flag:
                            dic['e'].append(body)
                            with open('temperature_pred_log.json','w') as file:
                                json.dump(dic, file)
                except:
                    dic = {
                        "bn":"temperature_pred_log",
                        "e":[]
                    }
                    dic["e"].append(body)
                    with open('temperature_pred_log.json','w') as file:
                        json.dump(dic, file)
            # add humidity predicted
            elif command == 'addHumidityPredicted':
                body = json.loads(cherrypy.request.body.read())
                add_humidity_flag = True
                try:
                    with open('humidity_pred_log.json') as files:
                        dic = json.load(files)
                        for i in range(len(dic['e'])):
                            if dic['e'][i]['farmID'] == body['farmID']:
                                dic['e'][i]['value'].append(body["value"][0])
                                add_humidity_flag = False
                                with open('humidity_pred_log.json','w') as file:
                                    json.dump(dic, file)
                                break
                        if add_humidity_flag:
                            dic['e'].append(body)
                            with open('humidity_pred_log.json','w') as file:
                                json.dump(dic, file)
                except:
                    dic = {
                        "bn":"humidity_pred_log",
                        "e":[]
                    }
                    dic["e"].append(body)
                    with open('humidity_pred_log.json','w') as file:
                        json.dump(dic, file)
            # register service 
            elif command == 'registrationServie':
                body = json.loads(cherrypy.request.body.read())
                try:
                    with open('serviceList.json') as files:
                        dic = json.load(files)
                        dic["e"].append(body)
                        with open('serviceList.json','w') as file:
                            json.dump(dic, file)
                except:
                    dic = {
                        "bn":"ServiceList",
                        "e":[]
                    }
                    dic["e"].append(body)
                    with open('serviceList.json','w') as file:
                        json.dump(dic, file)
            # register farm
            elif command == 'addFarm':
                # print(cherrypy.request.body.read())
                addFlag = True
                farm_dic = json.loads(cherrypy.request.body.read())  
                try:
                    with open('farmList.json') as file:
                        dic = json.load(file)
                    for i in dic["e"]:
                        if i["farmID"] == farm_dic["farmID"]:
                            addFlag = False
                            break
                    if addFlag:
                        dic["e"].append(farm_dic)
                        with open('farmList.json', 'w') as file:
                            json.dump(dic, file)
                except:
                    dic = {
                        "bn":"farmList",
                        "e":[]
                    }
                    dic["e"].append(farm_dic)
                    with open('farmList.json', 'w') as file:
                        json.dump(dic, file)
            # register charID
            elif command == "addChatID":
                body = json.loads(cherrypy.request.body.read())
                try:
                    with open('chatIDList.json') as files:
                        dic = json.load(files)
                        if body['chatID'] not in dic['e'][0]['v']:
                            dic['e'][0]['v'].append(body['chatID'])
                        with open('chatIDList.json','w') as file:
                            json.dump(dic, file)
                except:
                    dic = {'bn':'chatIDList',
                           'e':[
                               {
                                   'n':'chatID',
                                   'v':[]
                               }
                           ]
                           }
                    dic['e'][0]['v'].append(body['chatID'])
                    with open('chatIDList.json','w') as file:
                        json.dump(dic, file)
            # register mechanism status
            elif command == "addMechanismStatus":    

                body = json.loads(cherrypy.request.body.read())
                try: 
                    with open('MechanismStatus_log.json') as files:
                        dic = json.load(files)
                        dic["e"].append(body)
                    with open('MechanismStatus_log.json','w') as file:
                        json.dump(dic, file)
                        
                except:
                    dic = {
                        "bn":"MechanismStatus log",
                        "e":[]
                    }
                    dic["e"].append(body)
                    with open('MechanismStatus_log.json','w') as file:
                        json.dump(dic, file)
                
            # registed token for client
            elif command == "addToken":
                body = json.loads(cherrypy.request.body.read())
                try:
                    with open('TokenList.json') as files:
                        dic = json.load(files)
                        dic['e'][0]['v'].append(body)
                        with open('TokenList.json','w') as file:
                            json.dump(dic, file)
                except:
                    dic = {'bn':'TokenList',
                           'e':[
                               {
                                   'n':'Token',
                                   'v':[]
                               }
                           ]
                           }
                    dic['e'][0]['v'].append(body)
                    with open('TokenList.json','w') as file:
                        json.dump(dic, file)
                # develop together with telegarm bot
                pass
            else:
                return "cammand wrong"
        else:
            return "wrong"
    # delete elements
    def DELETE(self, *uri):
        if len(uri) != 0:
            command = str(uri[0])
            # delete farm
            if command == 'deleteFarm':
                dic = json.loads(cherrypy.request.body.read())
                deteledID = dic['deletedID']
                print(deteledID)
                with open("farmList.json") as farmListDic:
                    farmListDic = json.load(farmListDic)
                    farmList = farmListDic["e"]  # list
                with open("sensors.json") as sensorsListDic:
                    sensorsListDic = json.load(sensorsListDic)
                    sensorsList = sensorsListDic["sensors"]  # list

                for i in range(len(farmList)):
                    if farmList[i]["farmID"] == deteledID:
                        farmList.pop(i) # new list
                        break
                farmListDic["e"] = farmList
                with open('farmList.json','w') as file:
                    json.dump(farmListDic, file)

                for i in range(len(sensorsList)):
                    if sensorsList[i]["ID"] == deteledID:
                        sensorsList.pop(i) # new list
                        break
                sensorsListDic["sensors"] = sensorsList
                with open('sensors.json','w') as file:
                    json.dump(sensorsListDic, file)
            # delete service stoped
            if command == 'deleteService':
                dic = json.loads(cherrypy.request.body.read())
                deteledService = dic['service']
                with open("serviceList.json") as serviceListDic:
                    serviceListDic = json.load(serviceListDic)
                    ServiceList = serviceListDic["e"]  # list ["service":raspberry]

                for i in range(len(ServiceList)):
                    if ServiceList[i]["service"] == deteledService:
                        ServiceList.pop(i) # new list
                        break
                serviceListDic["e"] = ServiceList
                with open('serviceList.json','w') as file:
                    json.dump(serviceListDic, file)
            else:
                return "wrong"
        else:
            return "wrong"
        