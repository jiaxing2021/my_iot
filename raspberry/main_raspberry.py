
from raspberry import humidity_pub, humidity_control_sub, temperature_pub, temperature_control_sub, TS_humidity_pub, TS_temperature_pub, statistic_humidity_pub, statistic_temperature_pub, fertilizer_control_sub
from raspberry_web import raspberry_web
import adafruit_dht
import board
import sys
import time
import requests
import cherrypy
import os
import RPi.GPIO as GPIO

if __name__ == "__main__":

    GPIO.setmode(GPIO.BCM)

    watering = 13
    fertilizer = 6
    cooling = 26
    heating = 19

    GPIO.setup(watering, GPIO.OUT)
    GPIO.setup(fertilizer, GPIO.OUT)
    GPIO.setup(cooling, GPIO.OUT)
    GPIO.setup(heating, GPIO.OUT)

    dht_device = []
    # check how many raspberry services existing in catalog
    try:
        get_service_list_uri = "http://0.0.0.0:8888/getServiceList"
        response = requests.get(get_service_list_uri)
        serviceListDic = response.json()
        ServiceList = serviceListDic["e"] # return service list
        count = []
        for i in range(len(ServiceList)):
            # print(ServiceList[i]['service'][0:9])
            if ServiceList[i]['service'][0:9] == 'raspberry':
                count.append(ServiceList[i]['service'][9:])
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
        print("No raspberry service exiting!")
        serviceID = 0
        print(serviceID)

    # set sensor with activated farms
    # automatical set for the "serviceID_th" activated farm
    # run another main_raspberry.py to creat another raspberry service 
    # for the next activated farm
    try:
        get_activated_farm_uri = "http://0.0.0.0:8888/getActivatedFarm"
        response = requests.get(get_activated_farm_uri)
        farmDic = response.json()
        farmList = farmDic["e"]
        this_farm = farmList[serviceID]

        get_sensor_uri = "http://0.0.0.0:8888/getSensor"
        response = requests.get(get_sensor_uri)
        sensorDic = response.json()
        sensorList = sensorDic["sensors"]

        for i in range(len(sensorList)):
            if this_farm["farmID"] == sensorList[i]["ID"]:
                sensor_setting = sensorList[i]
        

        # retrive sensor port
        get_sensor_uri = "http://0.0.0.0:8888/getSensor"
        response = requests.get(get_sensor_uri)
        sensorDic = response.json()
        sensorList = sensorDic["sensors"]
        sensorPort = []
        for i in range(sensor_setting["SensorNum"]):
            sensorPort.append("board.D" + sensor_setting['SensorPort'][i])
            print(sensorPort[i])
            print(type(sensorPort[i]))
            for a in range(40):
                if sensor_setting['SensorPort'][i] == str(a):
                    print(sensor_setting['SensorPort'][i])
                    if a == 1:
                        dht_device.append(adafruit_dht.DHT11(board.D1))
                    elif a== 2:
                        dht_device.append(adafruit_dht.DHT11(board.D2))
                    elif a== 3:
                        dht_device.append(adafruit_dht.DHT11(board.D3))
                    elif a== 4:
                        dht_device.append(adafruit_dht.DHT11(board.D4))
                    elif a == 18:
                        dht_device.append(adafruit_dht.DHT11(board.D18))

        # print(dht_device)
    except:
        print("senser wrong, try again!")
        sys.exit()
        
    # start web service to allow users to control manually
    conf = {
    '/': {
      'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
      'tools.staticdir.root': os.path.abspath(os.getcwd()),
      'tools.sessions.on': True
      },
    }
    webport = 2500 + serviceID
    raspberry_web_servce = raspberry_web(watering, heating, cooling, fertilizer)
    cherrypy.tree.mount(raspberry_web_servce, '/', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': webport})
    cherrypy.engine.stop()
    cherrypy.engine.start()


    # dht_device = adafruit_dht.DHT11(board.D18)

    # get broker settings 
    get_broker_uri = "http://0.0.0.0:8888/getBrocker"
    res = requests.get(get_broker_uri)
    conf = res.json()

    # for control part
    broker=conf["test_broker"]
    port=conf["port"]
    topic = conf["baseTopic"]["humidity"][0]+str(serviceID)
    humidity_pub = humidity_pub("humidity_pub"+str(serviceID),topic,broker,port)
    humidity_pub.client.start()

    broker=conf["test_broker"]
    port=conf["port"]
    topic = conf["baseTopic"]["temperature"][0]+str(serviceID)
    temperature_pub = temperature_pub("temperature_pub"+str(serviceID),topic,broker,port)
    temperature_pub.client.start()

    broker_sub = conf["test_broker"]
    port_sub = conf["port"]
    topic_sub = conf["baseTopic"]["humidity"][1]+str(serviceID)
    humidity_control_sub = humidity_control_sub("humidity_control_sub"+str(serviceID), topic_sub, broker_sub, port_sub, watering)
    humidity_control_sub.start() # subscript command from humidity

    broker_sub = conf["test_broker"]
    port_sub = conf["port"]
    topic_sub = conf["baseTopic"]["temperature"][1]+str(serviceID)
    temperature_control_sub = temperature_control_sub("temperature_control_sub"+str(serviceID), topic_sub, broker_sub, port_sub, heating, cooling)
    temperature_control_sub.start() # subscript command from temperature

    broker_sub = conf["test_broker"]
    port_sub = conf["port"]
    topic_sub = conf["baseTopic"]["feeding"][1]+str(serviceID)
    fertilizer_control_sub = fertilizer_control_sub("fertilizer_control_sub"+str(serviceID), topic_sub, broker_sub, port_sub, fertilizer)
    fertilizer_control_sub.start() # subscript command from temperature

    # for TS_adapter part publish
    broker=conf["test_broker"]
    port=conf["port"]
    topic = conf["baseTopic"]["TS_adapter"][0]+str(serviceID)
    TS_humidity_pub = TS_humidity_pub("TS_humidity_pub"+str(serviceID),topic,broker,port)
    TS_humidity_pub.client.start()

    broker=conf["test_broker"]
    port=conf["port"]
    topic = conf["baseTopic"]["TS_adapter"][1]+str(serviceID)
    TS_temperature_pub = TS_temperature_pub("TS_temperature_pub"+str(serviceID),topic,broker,port)
    TS_temperature_pub.client.start()

    # for statistic part publish
    broker=conf["test_broker"]
    port=conf["port"]
    topic = conf["baseTopic"]["statistic_humidity"][0]+str(serviceID)
    statistic_humidity_pub = statistic_humidity_pub("statistic_humidity_pub"+str(serviceID),topic,broker,port)
    statistic_humidity_pub.client.start()

    broker=conf["test_broker"]
    port=conf["port"]
    topic = conf["baseTopic"]["statistic_temperature"][0]+str(serviceID)
    statistic_temperature_pub = statistic_temperature_pub("statistic_temperature_pub"+str(serviceID),topic,broker,port)
    statistic_temperature_pub.client.start()
   

    # service register uri and service delete uri
    registration_uri = "http://0.0.0.0:8888/registrationServie"
    delete_uri = "http://0.0.0.0:8888/deleteService"
    # service information
    data = {"service":"raspberry" + str(serviceID), "port":webport}

    # register service
    response = requests.post(registration_uri,json = data)


    while True:
        try:
            humidity = 0
            temperature = 0
            j = 0
            for i in dht_device:
                print(i)
                humidity += i.humidity
                temperature += i.temperature
                j += 1

            humidity = humidity/j
            temperature = temperature/j

            # humidity = dht_device.humidity
            # temperature = dht_device.temperature

            humidity = float(humidity)
            temperature = float(temperature)

            # humidity = 46.0   # for test
            # temperature = 25.0  # for test

            print(humidity)
            print(temperature)
            # humidity publish
            humidity_pub.publish(humidity) # publish to humidity
            TS_humidity_pub.publish(humidity) # publish to TS_humidity
            statistic_humidity_pub.publish(humidity) # publish to statistic_humidity
            # temperature publish
            temperature_pub.publish(temperature) # publish to temperature 
            TS_temperature_pub.publish(temperature) # publish to TS_temperature 
            statistic_temperature_pub.publish(temperature) # publish to statistic_temperature
            time.sleep(3)
        except:
            pass
            # # if raise errors, delet service from catalog
            # print("wrong, try again!")
            # response = requests.delete(delete_uri,json = data)
            # break
