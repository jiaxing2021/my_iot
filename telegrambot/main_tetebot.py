
from telebot import RESTBot, botWeb
import requests
import time
import cherrypy
import os


# # retrive token from catalog
# getTokenUri = "http://0.0.0.0:8888/getToken"
# req = requests.get(getTokenUri)
# tokeJson = req.json()
# token = tokeJson['token'][0]['Token']

# bot = RESTBot(token)

# while True:
#     time.sleep(1)

# retrive token from catalog
getTokenUri = "http://0.0.0.0:8888/getToken"
req = requests.get(getTokenUri)
tokeJson = req.json()
token = tokeJson['token'][0]['Token']

bot = RESTBot(token)

conf = {
'/': {
    'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    'tools.staticdir.root': os.path.abspath(os.getcwd()),
    'tools.sessions.on': True
    },
}
webport = 8000
botweb = botWeb()
cherrypy.tree.mount(botweb, '/', conf)
cherrypy.config.update({'server.socket_host': '0.0.0.0'})
cherrypy.config.update({'server.socket_port': webport})
cherrypy.engine.start()

# service register uri and service delete uri
registration_uri = "http://0.0.0.0:8888/registrationServie"
# service information
data = {"service":"telegrambot", "port":webport}
# register service
response = requests.post(registration_uri,json = data)

while True:
    time.sleep(1)
cherrypy.engine.stop()
