from MyMQTT import MyMQTT
import time
import json
import RPi.GPIO as GPIO

class humidity_pub:
	def __init__(self, clientID, topic,broker,port):
		self.topic=topic
		self.client=MyMQTT(clientID,broker,port,None)
		
	def start (self):
		self.client.start()

	def stop (self):
		self.client.stop()

	def publish(self,humid):
    

		message  = {'humidity':[]}
		message['humidity']=str(humid)
		self.client.myPublish(self.topic,message)
		time.sleep(1)

class humidity_control_sub:
    def __init__(self, clientID, topic, broker, port, mechanism):
        self.client = MyMQTT(clientID, broker, port, self)
        self.topic = topic
        self.status = None
        self.mechanism = mechanism

    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)

    def stop(self):
        self.client.stop()

    def notify(self, topic, msg):
        d = json.loads(msg)
        # print(d)
        # self.command = d["humidity_control_com"]
        self.command = d
        
        print(self.command)

        if self.command == "on":
            GPIO.output(self.mechanism, GPIO.HIGH)
        else:
            GPIO.output(self.mechanism, GPIO.LOW)
             
        """
        code for raspberry control
        """
        try:
            with open('humidity_command_log.json') as file:
                dic = json.load(file)
            dic["humidity_control_com"].append(self.command)
            with open('humidity_command_log.json','w') as file:
                json.dump(dic, file)
        except:
            dic = {"humidity_control_com":[]}
            dic["humidity_control_com"].append(self.command)
            with open('humidity_command_log.json','w') as file:
                json.dump(dic, file)

class temperature_pub(humidity_pub):
    def publish(self,temperature):
        
        message  = {'temperature':[]}
        message['temperature']=str(temperature)
        self.client.myPublish(self.topic,message)
        time.sleep(1)
        
class temperature_control_sub():

    def __init__(self, clientID, topic, broker, port, mechanism1, mechanism2):
        self.client = MyMQTT(clientID, broker, port, self)
        self.topic = topic
        self.status = None
        self.mechanism1 = mechanism1
        self.mechanism2 = mechanism2

    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)

    def stop(self):
        self.client.stop()
    def notify(self, topic, msg):
        d = json.loads(msg)
        self.command = d
        print(self.command)
        print(self.command[0])

        if self.command == ['heating on','cooling off']:
            GPIO.output(self.mechanism1, GPIO.HIGH)
            GPIO.output(self.mechanism2, GPIO.LOW)
        else:
            GPIO.output(self.mechanism2, GPIO.HIGH)
            GPIO.output(self.mechanism1, GPIO.LOW)
        """
        code for raspberry control
        """
        try:
            with open('temperature_command_log.json') as file:
                dic = json.load(file)
            dic["temperature_control_com"].append(self.command)
            with open('temperature_command_log.json','w') as file:
                json.dump(dic, file)
        except:
            dic = {"temperature_control_com":[]}
            dic["temperature_control_com"].append(self.command)
            with open('temperature_command_log.json','w') as file:
                json.dump(dic, file)

class fertilizer_control_sub():

    def __init__(self, clientID, topic, broker, port, mechanism):
        self.client = MyMQTT(clientID, broker, port, self)
        self.topic = topic
        self.status = None
        self.mechanism = mechanism

    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)

    def stop(self):
        self.client.stop()
    def notify(self, topic, msg):
        d = json.loads(msg)
        self.command = d
        print(self.command)
        print(self.command[0])

        if self.command == "fer_on":
            GPIO.output(self.mechanism, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(self.mechanism, GPIO.LOW)

        try:
            with open('fertilizer_command_log.json') as file:
                dic = json.load(file)
            dic["fertilizer_command"].append(self.command)
            with open('fertilizer_command_log.json','w') as file:
                json.dump(dic, file)
        except:
            dic = {"fertilizer_command":[]}
            dic["fertilizer_command"].append(self.command)
            with open('fertilizer_command_log.json','w') as file:
                json.dump(dic, file)
     
class TS_humidity_pub(humidity_pub):
    pass

class TS_temperature_pub(temperature_pub):
    pass

class statistic_humidity_pub(humidity_pub):
    pass

class statistic_temperature_pub(temperature_pub):
    pass

