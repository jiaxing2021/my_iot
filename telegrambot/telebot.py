import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import time
import requests

class RESTBot:
    exposed=True
    def __init__(self, token):
       
        self.tokenBot = token
        self.bot = telepot.Bot(self.tokenBot)
        MessageLoop(self.bot, {'chat': self.on_chat_message, 
                               'callback_query':self.on_callback_query}).run_as_thread()

        # retrive information about current farm
        currentFarmUri = "http://192.168.1.14:8888/getCurrentFarm"
        req = requests.get(currentFarmUri)
        currentFarmJson = req.json()
        self.currentFarmID = currentFarmJson['CurrentFarm'][0]['farmID']
        self.currentFarmName = currentFarmJson['CurrentFarm'][0]['farmName']

        ActivatedFarmUri = "http://192.168.1.14:8888/getActivatedFarm"
        req = requests.get(ActivatedFarmUri)
        ActivatedFarmList = req.json()['e']

        for i in range(len(ActivatedFarmList)):
            if ActivatedFarmList[i]['farmID'] == self.currentFarmID:
                self.serviceID = i
                break

        # regster suggested culture in catalog
        getSuggestCultureUri = "http://192.168.1.14:8888/getSuggestedCulture"
        req = requests.get(getSuggestCultureUri)
        SuggestCultureJson = req.json()
        self.cultureList = SuggestCultureJson['coltures']
        self.nameList = []
        for i in self.cultureList:
            self.nameList.append(i['Name'])

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        
        # regster chatID in catalog
        registrationChatID_uri = "http://192.168.1.14:8888/addChatID"
        chatIDData = {'chatID':chat_ID}
        response = requests.post(registrationChatID_uri,json = chatIDData)

        message = msg['text']

        if message == '/start':
            
            currentFarmUri = "http://192.168.1.14:8888/getCurrentFarm"
            req = requests.get(currentFarmUri)
            currentFarmJson = req.json()
            self.currentFarmID = currentFarmJson['CurrentFarm'][0]['farmID']
            self.currentFarmName = currentFarmJson['CurrentFarm'][0]['farmName']

            farmInfo = "The current farmID is " + str(self.currentFarmID) + " and the farm name is " + str(self.currentFarmName)

            buttons = [
                    [InlineKeyboardButton(text=f'Watering ON 🟡', callback_data=f'Wateron'), 
                    InlineKeyboardButton(text=f'Watering OFF ⚪', callback_data=f'Wateroff')],
                    [InlineKeyboardButton(text=f'Heating ON 🟡', callback_data=f' Heaton'), 
                    InlineKeyboardButton(text=f'Cooling ON ⚪', callback_data=f' Coolon')],
                    [InlineKeyboardButton(text=f'Fertilier ON 🟡', callback_data=f'Fertilieron'), 
                    InlineKeyboardButton(text=f'Fertilier OFF ⚪', callback_data=f'Fertilieroff')],
                    [InlineKeyboardButton(text=f'Get Information 🟡', callback_data=f'getinfo')],
                    [InlineKeyboardButton(text=f'Get Service List 🟡', callback_data=f'getService')],
                    [InlineKeyboardButton(text=f'Get activated Farm List 🟡', callback_data=f'getFarmList')],
                    [InlineKeyboardButton(text=f'Get suggestion 🟡', callback_data=f'getSuggestion')]
                    ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text=farmInfo, reply_markup=keyboard)

    def on_callback_query(self, msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')

        if query_data == "getinfo":
            # retrive temperature
            temperatureUri = "http://192.168.1.14:8888/getTemperature"
            req = requests.get(temperatureUri)
            temperatureList = req.json()['e']
            for i in temperatureList:
                if i['farmID'] == self.currentFarmID:
                    temperature = i['value'][-1]
                    break

            # retrive humidity
            humidityUri = "http://192.168.1.14:8888/getHumidity"
            req = requests.get(humidityUri)
            humidityList = req.json()['e']
            for i in humidityList:
                if i['farmID'] == self.currentFarmID:
                    humidity = i['value'][-1]
                    break

            # retrive predicted temperature
            temperaturePredUri = "http://192.168.1.14:8888/getTemperaturePred"
            req = requests.get(temperaturePredUri)
            temperaturePredList = req.json()['e']
            for i in temperaturePredList:
                if i['farmID'] == self.currentFarmID:
                    temperaturePred = i['value'][-1]
                    break

            # retrive predicted humidity
            humidityPredUri = "http://192.168.1.14:8888/getHumidityPred"
            req = requests.get(humidityPredUri)
            humidityPredList = req.json()['e']
            for i in humidityPredList:
                if i['farmID'] == self.currentFarmID:
                    humidityPred = i['value'][-1]
                    break

            # retrive mechanism status
            statusUri = "http://192.168.1.14:8888/getMechanismStatus"
            req = requests.get(statusUri)
            statusList = req.json()['e']
            statusList = statusList[::-1]

            for i in statusList:
                if i["farmID"] == self.currentFarmID:
                    if i["mechanism"] == "watering":
                        wateringStatus = i["status"]
                        break

            for i in statusList:
                if i["farmID"] == self.currentFarmID:
                    if i["mechanism"] == "heating and cooling":
                        HeatingCoolingStatus = i["status"]
                        break

            
            infoText = "The current temperature is " + str(temperature) + " degree and the current humidity is " + str(humidity) + "% and the predicted temperature is " + str(temperaturePred) + " degree and the predicted humidity is " + str(humidityPred) + "% \n"
            statusText = f"Watering mechanism is {wateringStatus} and {HeatingCoolingStatus[0]} and {HeatingCoolingStatus[1]}"
            text = infoText + statusText
            self.bot.sendMessage(chat_ID, text=text)
        
        elif query_data == "getFarmList":
            # retrive activated farm list
            FarmListUri = "http://192.168.1.14:8888/getActivatedFarm"
            req = requests.get(FarmListUri)
            FarmList = req.json()['e']
            numFarm = len(FarmList)

            text = f"There are {numFarm} activated farms. \n"
            string = ''
            for i in range(numFarm):
                string = string + f"FarmID is {FarmList[i]['farmID']} and farm name is {FarmList[i]['farmName']} \n"
            text = text + string
            self.bot.sendMessage(chat_ID, text=text)

        elif query_data == "getService":
            # retrive service list
            ServiceListUri = "http://192.168.1.14:8888/getServiceList"
            req = requests.get(ServiceListUri)
            ServiceList = req.json()['e']
            numService = len(ServiceList)

            text = f"There are {numService} Service. \n"
            string = ''
            for i in range(numService):
                string = string + f"Service name is {ServiceList[i]['service']} \n"
            text = text + string
            self.bot.sendMessage(chat_ID, text=text)
        elif query_data == 'getSuggestion':

            suggestedButtons = []
            for i in self.nameList:
                suggestedButtons.append([InlineKeyboardButton(text=f'{i} 🟡', callback_data=f'{i}')])

            suggestedKeyboard = InlineKeyboardMarkup(inline_keyboard=suggestedButtons)
            self.bot.sendMessage(chat_ID, text = "choose one plant to get suggestion.", reply_markup=suggestedKeyboard)

        elif query_data in self.nameList:
            for i in self.cultureList:
                if i['Name'] == query_data:
                    name = i['Name']
                    period = i['Optimal Planting period']
                    temerature = i['Optimal Temperature range']
                    break

                
            periodString = f"The Optimal Planting period for {name} is {period} months. \n"
            temperatureString = f"The Optimal Temperature range for {name} is {temerature}. \n"
            text = periodString + temperatureString
            self.bot.sendMessage(chat_ID, text = text)
      
        else:
            if query_data == "Wateron":
                baseUri = "http://192.168.1.14:"
                webport = 2500 + self.serviceID
                uri = baseUri + str(webport) + '/on_wartering'
                req = requests.put(uri)
                seconds = time.time()
                timestamp = time.ctime(seconds)
                self.bot.sendMessage(chat_ID, text=f"{query_data[0:5]}ing mechanism is switched {query_data[5:]} at {timestamp}")

            elif query_data == "Wateroff":
                baseUri = "http://192.168.1.14:"
                webport = 2500 + self.serviceID
                uri = baseUri + str(webport) + '/off_wartering'
                req = requests.put(uri)
                seconds = time.time()
                timestamp = time.ctime(seconds)
                self.bot.sendMessage(chat_ID, text=f"{query_data[0:5]}ing mechanism is switched {query_data[5:]} at {timestamp}")

            elif query_data == " Heaton":
                baseUri = "http://192.168.1.14:"
                webport = 2500 + self.serviceID
                uri = baseUri + str(webport) + '/on_heating_off_cooling'
                req = requests.put(uri)
                seconds = time.time()
                timestamp = time.ctime(seconds)
                self.bot.sendMessage(chat_ID, text=f"{query_data[0:5]}ing mechanism is switched {query_data[5:]} at {timestamp}")

            elif query_data == " Coolon":
                baseUri = "http://192.168.1.14:"
                webport = 2500 + self.serviceID
                uri = baseUri + str(webport) + '/off_heating_on_cooling'
                req = requests.put(uri)
                seconds = time.time()
                timestamp = time.ctime(seconds)
                self.bot.sendMessage(chat_ID, text=f"{query_data[0:5]}ing mechanism is switched {query_data[5:]} at {timestamp}")
            elif query_data == "Fertilieron":
                baseUri = "http://192.168.1.14:"
                webport = 2500 + self.serviceID
                uri = baseUri + str(webport) + '/on_feeding'
                req = requests.put(uri)
                seconds = time.time()
                timestamp = time.ctime(seconds)
                self.bot.sendMessage(chat_ID, text=f"Fertilizer mechanism is switched on at {timestamp}")
            elif query_data == "Fertilieroff":
                baseUri = "http://192.168.1.14:"
                webport = 2500 + self.serviceID
                uri = baseUri + str(webport) + '/off_feeding'
                req = requests.put(uri)
                seconds = time.time()
                timestamp = time.ctime(seconds)
                self.bot.sendMessage(chat_ID, text=f"Fertilizer mechanism is switched off at {timestamp}")


                
            # retrieve raspberry web service uri
            # baseUri = 
            # req = requests.put()
            # seconds = time.time()
            # timestamp = time.ctime(seconds)
            # self.bot.sendMessage(chat_ID, text=f"{query_data[0:5]}ing mechanism is switched {query_data[5:]} at {timestamp}")

class botWeb:
    exposed = True
    def __init__(self):
        pass
    # to allow catalog check online or offline
    def GET(self,*uri):
        if len(uri)!=0:
            command = str(uri[0])
            if command == "online":
                pass

            
