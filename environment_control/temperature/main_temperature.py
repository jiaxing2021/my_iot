import json
from temperature import temperature, temperature_web
import requests
import os
import cherrypy


if __name__ == "__main__":

    # check how many temperature services existing in catalog
    try:
        get_service_list_uri = "http://192.168.1.14:8888/getServiceList"
        response = requests.get(get_service_list_uri)
        serviceListDic = response.json()
        ServiceList = serviceListDic["e"] # return service list
        count = []
        for i in range(len(ServiceList)):
            # print(ServiceList[i]['service'][0:9])
            if ServiceList[i]['service'][0:11] == 'temperature' and len(ServiceList[i]['service']) < 13:
                count.append(ServiceList[i]['service'][11:])
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
    webport = 3000 + serviceID
    temperature_web = temperature_web()
    cherrypy.tree.mount(temperature_web, '/', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': webport})
    cherrypy.engine.stop()
    cherrypy.engine.start()

    get_broker_uri = "http://192.168.1.14:8888/getBrocker"
    res = requests.get(get_broker_uri)
    conf = res.json()

    broker = conf["test_broker"]
    port = conf["port"]
    topic_sub = conf["baseTopic"]["temperature"][0]+str(serviceID)
    topic_pub = conf["baseTopic"]["temperature"][1]+str(serviceID)
    temperature = temperature("temperature"+str(serviceID), topic_sub, topic_pub, broker, port, serviceID)
    temperature.start()

    # register service
    delete_uri = "http://192.168.1.14:8888/deleteService"
    registration_uri = "http://192.168.1.14:8888/registrationServie"
    data = {"service":"temperature" + str(serviceID), "port":webport}
    response = requests.post(registration_uri,json = data)

    while True:
        # press space to stop the service and delete it from catalog
        # if keyboard.is_pressed('space'):
        #     print('space was pressed! Service stoped!')
        #     response = requests.delete(delete_uri,json = data)
        #     break
        pass
        
