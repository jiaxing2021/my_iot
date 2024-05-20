
import cherrypy
from catalog import catalog
import os
import requests
import time
   
conf = {
'/': {
  'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
#   'tools.staticdir.root': os.path.abspath(os.getcwd()),
  'tools.sessions.on': True
  },
}
catalog_servce = catalog()
cherrypy.tree.mount(catalog_servce, '/', conf)
cherrypy.config.update({'server.socket_host': '0.0.0.0'})
cherrypy.config.update({'server.socket_port': 8888})
cherrypy.engine.start()


t = 30
def checkoffline(webport):
    baseUri = "http://192.168.1.14:"
    uri = baseUri + str(webport) + '/online'
    req = requests.get(uri)
    print(req)


while True:
    time.sleep(t)
    # get service list
    ServiceListUri = "http://0.0.0.0:8888/getServiceList"
    delete_uri = "http://0.0.0.0:8888/deleteService"
    req = requests.get(ServiceListUri)
    serviceList = req.json()['e']
    print(serviceList)
    for i in serviceList:

        service = i['service']
        print(f"checking {service}")
        port = i['port']
        data = {"service":service, "port":port}
        try:
            checkoffline(port)
        except:
            print("delete")
            response = requests.delete(delete_uri,json = data)
            
cherrypy.engine.stop()
    