import cherrypy
import sys
import os

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
                p = sys.executable
                os.execl(p,p,*sys.argv)
                