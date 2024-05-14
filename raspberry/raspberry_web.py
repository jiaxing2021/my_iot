import cherrypy
import RPi.GPIO as GPIO

class raspberry_web:
    exposed = True
    def __init__(self,watering, heating, cooling, fertilizer):
        self.watering = watering
        self.heating = heating
        self.cooling = cooling
        self.fertilizer = fertilizer
    # to allow catalog check online or offline
    def GET(self,*uri):
        if len(uri)!=0:
            command = str(uri[0])
            if command == "online":
                pass
    # the reason for PUT method is that
    # menual controlling to change the status 
    # is similiar with updata the resource
    def PUT(self,*uri):
        if len(uri) != 0:
            command = str(uri[0])
            if command == "on_heating_off_cooling":
                print("heating on cooling off")
                GPIO.output(self.heating, GPIO.HIGH)
                GPIO.output(self.cooling, GPIO.LOW)
                """
                code for raspberry control
                """
            elif command == "off_heating_on_cooling":
                print("heating off and cooling on")
                GPIO.output(self.heating, GPIO.LOW)
                GPIO.output(self.cooling, GPIO.HIGH)
                """
                code for raspberry control
                """
            elif command == "on_wartering":
                print("wartering on")
                GPIO.output(self.watering, GPIO.HIGH)
                """
                code for raspberry control
                """
            elif command == "off_wartering":
                print("wartering off")
                GPIO.output(self.watering, GPIO.LOW)
                """
                code for raspberry control
                """
            elif command == "on_feeding":
                print("feeding on")
                GPIO.output(self.fertilizer, GPIO.HIGH)
                """
                code for raspberry control
                """
            elif command == "off_feeding":
                print("feeding off")
                GPIO.output(self.fertilizer, GPIO.LOW)
            else:
                print("wrong")

    