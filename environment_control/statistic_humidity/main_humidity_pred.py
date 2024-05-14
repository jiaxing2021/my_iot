import json
from humidity_pred import humidity_pred, TS_humidity_pub, DNN, humidity_pred_web
import requests
import time
import cherrypy
import os


if __name__ == "__main__":

    # check how many raspberry services existing in catalog
    try:
        get_service_list_uri = "http://0.0.0.0:8888/getServiceList"
        response = requests.get(get_service_list_uri)
        serviceListDic = response.json()
        ServiceList = serviceListDic["e"] # return service list
        count = []
        for i in range(len(ServiceList)):
            # print(ServiceList[i]['service'][0:9])
            if ServiceList[i]['service'][0:13] == 'humidity_pred':
                count.append(ServiceList[i]['service'][13:])
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
        print("No humidity_pred service exiting!")
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
    webport = 4000 + serviceID
    humidity_pred_web = humidity_pred_web()
    cherrypy.tree.mount(humidity_pred_web, '/', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': webport})
    cherrypy.engine.stop()
    cherrypy.engine.start()

    get_broker_uri = "http://0.0.0.0:8888/getBrocker"
    res = requests.get(get_broker_uri)
    conf = res.json()

    broker = conf["test_broker"]
    port = conf["port"]
    topic_sub = conf["baseTopic"]["statistic_humidity"][0]+str(serviceID)
    # topic_pub = conf["baseTopic"]["statistic_humidity"][1]+str(serviceID)
    # print(topic_pub)
    humidity_pred = humidity_pred("humidity_pred"+str(serviceID), topic_sub, broker, port, serviceID)
    humidity_pred.start()
    
    broker = conf["test_broker"]
    port = conf["port"]
    topic = conf["baseTopic"]["TS_adapter"][2]+str(serviceID)
    TS_humidity_pub = TS_humidity_pub("TS_temperature_pub"+str(serviceID), topic, broker, port)
    TS_humidity_pub.start()


    # register service
    delete_uri = "http://0.0.0.0:8888/deleteService"
    registration_uri = "http://0.0.0.0:8888/registrationServie"
    data = {"service":"humidity_pred" + str(serviceID), "port":webport}
    response = requests.post(registration_uri,json = data)

    while True:
        # press space to stop the service and delete it from catalog
        # if keyboard.is_pressed('space'):
        #     print('space was pressed! Service stoped!')
        #     response = requests.delete(delete_uri,json = data)
        #     break
        try:
            TS_humidity_pub.publish() # publish to statistic_temperature
            time.sleep(0.5)
        except:
            print('Error! Service stoped!')
            response = requests.delete(delete_uri,json = data)
            break
        
