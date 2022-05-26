from urllib import response
import requests
import json
import hashlib
import hmac
from datetime import datetime
import time

endpoint_public = "https://api.coin.z.com/public"
endpoint_ws_api = "wss://api.coin.z.com/ws/public"
private_api = "https://api.coin.z.com/private"
private_ws_api = "wss://api.coin.z.com/ws/private"
path = "/v1/order"
method = "POST"

statusPath = "/v1/status"
rateAll = "/v1/ticker"
book = "/v1/orderbooks?symbol=XRP_JPY"
tradelist = "/v1/trades?symbol=XRP_JPY&page=1&count=20"

def get_price():
    responce = requests.get(endpoint_public + book)
    toread = responce.json()
    ask = toread["data"]["asks"][0]["price"]
    bid = toread["data"]["bids"][0]["price"]
    return ask, bid

def get_ayumi():
    response = requests.get(endpoint_public + tradelist)
    toread = response.json()
    buycount = 0

    for i in range(0,20,2):
        #print(toread["data"]["list"][i])
        if toread["data"]["list"][i]["side"] == "BUY":
            buycount += 1
    return buycount

while True:

    ask, bid = get_price()
    """
    print("ask " + ask)
    print("bid " + bid)
    print("spread " + str(float(ask) - float(bid)))
    print("end")

    buycount = get_ayumi()
    print("count: " + str(buycount))
    if buycount < 4:
        print("Sell!!!")
    elif buycount > 6:
        print("Buy!!!")
    """
    time.sleep(2)