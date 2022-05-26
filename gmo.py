import requests
import json
import hashlib
import hmac
from datetime import datetime
import time
import my_function as mf
import gmo_bch as gbch

api_key = ""
api_secret = ""

endpoint_public = "https://api.coin.z.com/public"
endpoint_ws_api = "wss://api.coin.z.com/ws/public"
private_api = "https://api.coin.z.com/private"
private_ws_api = "wss://api.coin.z.com/ws/private"
path = "/v1/order"
method = "POST"
get_method = "GET"

statusPath = "/v1/status"
rateAll = "/v1/ticker"
book = "/v1/orderbooks?symbol=XRP_JPY"

activeorder_path = "/v1/activeOrders"
changeorder_path = '/v1/changeOrder'

#ポジション構築
def open_position(signal, price, flag):
    timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
    buyprice = round(float(price) + 0.01, 3)
    sellprice = round(float(price) - 0.01, 3)
        
    if signal == "buy":
        param = {
            "symbol": "XRP_JPY",
            "side": "BUY",
            "executionType": "LIMIT",
            "timeInForce": "FAS",
            "price": str(buyprice),
            "size": "100"
        }
        flag = True
    
    else:
        param = {
            "symbol": "XRP_JPY",
            "side": "SELL",
            "executionType": "LIMIT",
            "timeInForce": "FAS",
            "price": str(sellprice),
            "size": "100"
        }
        flag = True

    body = json.dumps(param)

    messeage = timestamp + method + path + body
    signature = hmac.new(bytes(api_secret.encode('ascii')), bytes(messeage.encode('ascii')), hashlib.sha256).hexdigest()

    headers = {
        "API-KEY": api_key,
        "API-TIMESTAMP": timestamp,
        "API-SIGN": signature
    }

    response = requests.post( private_api + path , data = body , headers = headers)
    print( response.status_code )
    print( response.json() )
    orderid = 0
    if response.json()["status"] == 0:
        orderid = response.json()["data"]
    else:
        print("OPEN_ERROR\n")
    return flag, orderid


#有効ポジションチェック
def check_position():
    timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
    text = timestamp + get_method + activeorder_path
    sign = hmac.new(bytes(api_secret.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
    parameters = {
        "symbol": "XRP_JPY"
    }

    headers = {
        "API-KEY": api_key,
        "API-TIMESTAMP": timestamp,
        "API-SIGN": sign
    }

    res = requests.get(private_api + activeorder_path, headers=headers, params=parameters)
    orderlist = res.json()

    if orderlist["status"] == 1:
        print("CHECK_ERROR\n")

    order = orderlist["data"]
    if order:
        flag = True
        order = orderlist["data"]["list"][0]["orderId"]
        if orderlist["data"]["list"][0]["settleType"] == "CLOSE":
            flag = False
    else:
        flag = False
        order = 0
    
    return flag, order

#注文変更
def change_order(orderid, mode, ask, bid):
    timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))

    if mode == "sell":
        price = round(float(ask) - 0.001, 3)
        #price = int(ask) - 1
        print(price)
        reqBody = {
            "orderId": orderid,
            "price": str(price)
        }
    else:
        price = round(float(bid) + 0.001, 3)
        #price = int(bid) + 1
        reqBody = {
            "orderId": orderid,
            "price": str(price)
        }

    text = timestamp + method + changeorder_path + json.dumps(reqBody)
    sign = hmac.new(bytes(api_secret.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

    headers = {
        "API-KEY": api_key,
        "API-TIMESTAMP": timestamp,
        "API-SIGN": sign
    }

    res = requests.post(private_api + changeorder_path, headers=headers, data=json.dumps(reqBody))
    print (res.json())
    flag = True
    if res.json()["status"] == 1:
        print("CHANGE_ERROR\n")
        flag = False

    return flag

#保持中のポジション要約
def get_positionsummary():
    timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
    method    = 'GET'
    endPoint  = 'https://api.coin.z.com/private'
    path      = '/v1/positionSummary'

    text = timestamp + method + path
    sign = hmac.new(bytes(api_secret.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
    parameters = {
        "symbol": "XRP_JPY"
    }

    headers = {
        "API-KEY": api_key,
        "API-TIMESTAMP": timestamp,
        "API-SIGN": sign
    }

    res = requests.get(endPoint + path, headers=headers, params=parameters)
    print (res.json())

    quantity = 0
    avelong = 0
    aveshort = 0
    sumlong = 0
    sumshort = 0
    if res.json()["data"]["list"]:
        for i in range(len(res.json()["data"]["list"])):
            quantity += float(res.json()["data"]["list"][i]["sumPositionQuantity"])
            if res.json()["data"]["list"][i]["side"] == "BUY":
                avelong = round(float(res.json()["data"]["list"][i]["averagePositionRate"]), 3)
                #avelong = int(res.json()["data"]["list"][i]["averagePositionRate"])
                sumlong = res.json()["data"]["list"][i]["sumPositionQuantity"]
            if res.json()["data"]["list"][i]["side"] == "SELL":
                aveshort = round(float(res.json()["data"]["list"][i]["averagePositionRate"]), 3)
                #aveshort = int(res.json()["data"]["list"][i]["averagePositionRate"])
                sumshort = res.json()["data"]["list"][i]["sumPositionQuantity"]
    
    return quantity, avelong, aveshort, sumlong, sumshort

#全オーダーキャンセル
def close_bulkorder(average, size, closetype):
    timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
    method    = 'POST'
    endPoint  = 'https://api.coin.z.com/private'
    path      = '/v1/closeBulkOrder'
        
    if closetype == "closelong": 
        reqBody = {
            "symbol": "XRP_JPY",
            "side": "SELL",
            "executionType": "LIMIT",
            "timeInForce": "FAS",
            "price": str(round(float(average) + 0.01, 3)),
            "size": size
        }

    if closetype == "closeshort":
        reqBody = {
            "symbol": "XRP_JPY",
            "side": "BUY",
            "executionType": "LIMIT",
            "timeInForce": "FAS",
            "price": str(round(float(aveshort) - 0.01, 3)),
            "size": size
        }

    text = timestamp + method + path + json.dumps(reqBody)
    sign = hmac.new(bytes(api_secret.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

    headers = {
        "API-KEY": api_key,
        "API-TIMESTAMP": timestamp,
        "API-SIGN": sign
    }

    res = requests.post(endPoint + path, headers=headers, data=json.dumps(reqBody))
    print (res.json())
    if res.json()["status"] == 1:
        print("close_error")


flag = False
orderid = 0
mode = "neutral"
while True:

    ask, bid, ask1, bid1 = mf.get_price()
    print(ask, bid)

    buycount = mf.get_ayumi()

    position_quantity, avelong, aveshort, longsize, shortsize = get_positionsummary()
    print(position_quantity)

    if flag:
        if float(ask) - float(bid) > 0.064:
            flag = change_order(orderid, mode, ask1, bid1)
        else:
            flag = gbch.cancel_order(orderid)
    else:
        if position_quantity > 0:
            if float(longsize) > 0:
                close_bulkorder(avelong, longsize, "closelong")
                time.sleep(30)
            
            if float(shortsize) > 0:
                close_bulkorder(aveshort, shortsize, "closeshort")
                time.sleep(30)
                
        if position_quantity < 50 and float(ask)-float(bid) > 0.08:
            if buycount < 4:
                print("Sell!!!")
                flag, orderid = open_position("sell", ask, flag)
                mode = "sell"
            elif buycount > 6:
                print("Buy!!!")
                flag, orderid = open_position("buy", bid, flag)
                mode = "buy"
            else: pass
        
    time.sleep(2)
    
    flag, order = check_position()
    print(flag, order)
