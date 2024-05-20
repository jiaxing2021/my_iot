import json
from humidity import humidity, humidity_web
import requests
import cherrypy
import os


if __name__ == "__main__":

    # check how many humidity services existing in catalog
    try:
        get_service_list_uri = "http://192.168.1.14:8888/getServiceList"
        response = requests.get(get_service_list_uri)
        serviceListDic = response.json()
        ServiceList = serviceListDic["e"] # return service list
        count = []
        for i in range(len(ServiceList)):
            # print(ServiceList[i]['service'][0:9])
            if ServiceList[i]['service'][0:8] == 'humidity':
                count.append(ServiceList[i]['service'][8:])
        flag = True
        try:
            for j in range(len(count)):
                if str(j) != count[j]:
                    serviceID = j
                    flag = False
                else:
                    continue
            if flag:
                serviceID = j + 1
        except:
            serviceID = 0

        print(serviceID)

    except:
        print("No humidity service exiting!")
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
    webport = 2000 + serviceID
    humidity_web = humidity_web()
    cherrypy.tree.mount(humidity_web, '/', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': webport})
    cherrypy.engine.stop()
    cherrypy.engine.start()

    get_broker_uri = "http://192.168.1.14:8888/getBrocker"
    res = requests.get(get_broker_uri)
    conf = res.json()

    broker = conf["test_broker"]
    port = conf["port"]
    topic_sub = conf["baseTopic"]["humidity"][0]+str(serviceID)
    topic_pub = conf["baseTopic"]["humidity"][1]+str(serviceID)
    humidity = humidity("humidity_sub"+str(serviceID), topic_sub, topic_pub, broker, port, serviceID)
    humidity.start()

    # register service
    delete_uri = "http://192.168.1.14:8888/deleteService"
    registration_uri = "http://192.168.1.14:8888/registrationServie"
    data = {"service":"humidity"+str(serviceID), "port":webport}
    response = requests.post(registration_uri,json = data)

    while True:
        # press space to stop the service and delete it from catalog
        # if keyboard.is_pressed('space'):
        #     print('space was pressed! Service stoped!')
        #     response = requests.delete(delete_uri,json = data)
        #     break
        pass
        
