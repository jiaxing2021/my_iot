import requests

base = "http://0.0.0.0:8887"
uri = "/on_heating"


res = requests.put(base + uri)