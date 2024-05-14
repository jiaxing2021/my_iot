from feeding import feeding, feeding_web
import requests
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
            if ServiceList[i]['service'][0:7] == 'feeding':
                count.append(ServiceList[i]['service'][7:])
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
        print("No feeding service exiting!")
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
    webport = 7000 + serviceID
    feeding_web = feeding_web()
    cherrypy.tree.mount(feeding_web, '/', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': webport})
    cherrypy.engine.stop()
    cherrypy.engine.start()

    get_broker_uri = "http://0.0.0.0:8888/getBrocker"
    res = requests.get(get_broker_uri)
    conf = res.json()
    broker = conf["test_broker"]
    port = conf["port"]
    topic_sub = conf["baseTopic"]["feeding"][0]+str(serviceID)
    topic_pub = conf["baseTopic"]["feeding"][1]+str(serviceID)
    feeding = feeding("feeding"+str(serviceID), topic_sub,topic_pub, broker, port, serviceID)
    feeding.start()

    delete_uri = "http://0.0.0.0:8888/deleteService"
    registration_uri = "http://0.0.0.0:8888/registrationServie"
    data = {"service":"feeding" + str(serviceID), "port":webport}
    # register service
    response = requests.post(registration_uri,json = data)

    while True:
    # press space to stop the service and delete it from catalog
        # if keyboard.is_pressed('space'):
        #     print('space was pressed! Service stoped!')
        #     response = requests.delete(delete_uri,json = data)
        #     break
        pass