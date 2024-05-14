from MyMQTT import MyMQTT
import time
import json
import cherrypy

class time_scheduler_web:
    exposed = True
    def __init__(self):
        pass
    # to allow catalog check online or offline
    def GET(self,*uri):
        if len(uri)!=0:
            command = str(uri[0])
            if command == "online":
                pass

# subscript command from telegram bot
class time_scheduler:
	def __init__(self, clientID, topic,broker,port,t):
		self.topic=topic
		self.client=MyMQTT(clientID,broker,port,None)
		self.t = t
		
	def start (self):
		self.client.start()

	def stop (self):
		self.client.stop()

	def publish(self):
		print("on time")
		message  = {'humidity':"on time"}
		self.client.myPublish(self.topic,message)
		time.sleep(self.t)