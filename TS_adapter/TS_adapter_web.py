
import sys
import os
import requests

class TS_adapter_web:

    exposed = True
    def __init__(self):
        pass
    # to allow catalog check online or offline
    def GET(self,*uri):
        if len(uri)!=0:
            command = str(uri[0])
            if command == "online":
                pass
            
    def PUT(self,*uri):
        if len(uri) != 0:
            command = str(uri[0])
            if command == 'restart':
                delete_uri = "http://192.168.1.14:8888/deleteService"
                data = {"service":"TS_adapter", "port":8080}
                response = requests.delete(delete_uri,json = data)
                p = sys.executable
                os.execl(p,p,*sys.argv)
                