import json
from temperature_pred import temperature_pred, TS_temperature_pub, DNN, temerature_pred_web
import requests
import time
import cherrypy
import os


if __name__ == "__main__":

    # check how many temperature predictor services existing in catalog
    try:
        get_service_list_uri = "http://0.0.0.0:8888/getServiceList"
        response = requests.get(get_service_list_uri)
        serviceListDic = response.json()
        ServiceList = serviceListDic["e"] # return service list
        count = []
        for i in range(len(ServiceList)):
            # print(ServiceList[i]['service'][0:9])
            if ServiceList[i]['service'][0:16] == 'temperature_pred':
                count.append(ServiceList[i]['service'][16:])
        flag = True
        for j in range(len(count)):
            if str(j) != count[j]:
                serviceID = j
                flag = False
            else:
                continue
        if flag:
            serviceID = j + 1

        print(serviceID)

    except:
        print("No temperature_pred service exiting!")
        serviceID = 0
        print(serviceID)

        # start web service to allow users to control manually
    conf = {
    '/': {
      'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
      'tools.staticdir.root': os.path.abspath(os.getcwd()),
      'tools.sessions.on': True
      },
    }
    webport = 5000 + serviceID
    temerature_pred_web = temerature_pred_web()
    cherrypy.tree.mount(temerature_pred_web, '/', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': webport})
    cherrypy.engine.stop()
    cherrypy.engine.start()

    get_broker_uri = "http://0.0.0.0:8888/getBrocker"
    res = requests.get(get_broker_uri)
    conf = res.json()

    broker = conf["test_broker"]
    port = conf["port"]
    topic_sub = conf["baseTopic"]["statistic_temperature"][0]+str(serviceID)
    # topic_pub = conf["baseTopic"]["statistic_temperature"][1]+str(serviceID)
    temperature_pred = temperature_pred("temperature_pred"+str(serviceID), topic_sub, broker, port, serviceID)
    temperature_pred.start()

    broker = conf["test_broker"]
    port = conf["port"]
    topic = conf["baseTopic"]["TS_adapter"][3]+str(serviceID)
    TS_temperature_pub = TS_temperature_pub("TS_temperature_pub"+str(serviceID), topic, broker, port)
    TS_temperature_pub.start()



    # register service
    delete_uri = "http://0.0.0.0:8888/deleteService"
    registration_uri = "http://0.0.0.0:8888/registrationServie"
    data = {"service":"temperature_pred"+str(serviceID),"port":webport}
    response = requests.post(registration_uri,json = data)

    while True:
        # press space to stop the service and delete it from catalog
        # if keyboard.is_pressed('space'):
        #     print('space was pressed! Service stoped!')
        #     response = requests.delete(delete_uri,json = data)
        #     break
        try:
            TS_temperature_pub.publish() # publish to statistic_temperature
            time.sleep(1)
        except:
            print('Error! Service stoped!')
            response = requests.delete(delete_uri,json = data)
            break

        
