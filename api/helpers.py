import requests
import redis
from coin import Coin
from datetime import datetime, timedelta
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)
url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=ethereum%2C%20zelcash%2C%20ethereum-classic%2C%20conflux-token%2C%20firo%2C%20ergo%2C%20ravencoin%2C%20bitcoin-gold&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h%2C24h%2C7d%2C14d%2C30d%2C1y"

def getPrice(coinID):
    req = requests.get(url, headers = {"accept": "application/json"})
    for coin in req.json():
        if(coin['id'] == coinID):
            return coin['current_price']

def fillPrice(coinPrices):
    req = requests.get(url, headers = {"accept": "application/json"})
    for coin in req.json():
        coinPrices[coin['name']] = [coin['current_price'], coin['ath'], coin['atl']]

def getATH(coinID):
    req = requests.get(url, headers = {"accept": "application/json"})
    for coin in req.json():
        if(coin['id'] == coinID):
            return coin['ath']

def getATL(coinID):
    req = requests.get(url, headers = {"accept": "application/json"})
    for coin in req.json():
        if(coin['id'] == coinID):
            return coin['atl']

def createIndex(coinindex):
    req = requests.get(url, headers = {"accept": "application/json"})
    for coin in req.json():
        newCoin = Coin(coin['name'], coin['id'], coin['symbol']) 
        newCoin.setPrice(coin['current_price'], coin['ath'], coin['atl'])
        coinindex[coin['name']] = newCoin
        redis_client.hset(coin['name'], 'isCoin', 'yes')

def toPercent(num):
    num = num*100
    num = round(num, 4)
    result = str(num)+'%'
    return result

def toCurrency(num):
    if num >= 0:
        return '${:,.4f}'.format(num)
    else:
        return '-${:,.4f}'.format(-num)

def setGPUPrices(gpuJSON, gpu0=599.0, gpu1=499.0, gpu2=399.0, gpu3= 329.0, rig0=500.0, rig1=400.0, rig2=450.0, rig3=400.0):
    gpuJSON[0]["Data"]["Bitcoin Gold"]["Power"] = 216
    gpuJSON[1]["Data"]["Bitcoin Gold"]["Power"] = 124
    gpuJSON[2]["Data"]["Bitcoin Gold"]["Power"] = 0
    gpuJSON[3]["Data"]["Bitcoin Gold"]["Power"] = 0
    gpuJSON[0]["Data"]["Conflux"]["Power"] = 210
    gpuJSON[1]["Data"]["Conflux"]["Power"] = 153
    gpuJSON[2]["Data"]["Conflux"]["Power"] = 163
    gpuJSON[3]["Data"]["Conflux"]["Power"] = 140
    gpuJSON[0]["Data"]["Ergo"]["Power"] = 150
    gpuJSON[1]["Data"]["Ergo"]["Power"] = 110
    gpuJSON[2]["Data"]["Ergo"]["Power"] = 120
    gpuJSON[3]["Data"]["Ergo"]["Power"] = 130
    gpuJSON[0]["Data"]["Ethereum"]["Power"] = 183
    gpuJSON[1]["Data"]["Ethereum"]["Power"] = 110
    gpuJSON[2]["Data"]["Ethereum"]["Power"] = 130
    gpuJSON[3]["Data"]["Ethereum"]["Power"] = 111
    gpuJSON[0]["Data"]["Ethereum Classic"]["Power"] = 183
    gpuJSON[1]["Data"]["Ethereum Classic"]["Power"] = 110
    gpuJSON[2]["Data"]["Ethereum Classic"]["Power"] = 159
    gpuJSON[3]["Data"]["Ethereum Classic"]["Power"] = 106
    gpuJSON[0]["Data"]["Flux"]["Power"] = 169
    gpuJSON[1]["Data"]["Flux"]["Power"] = 139
    gpuJSON[2]["Data"]["Flux"]["Power"] = 139
    gpuJSON[3]["Data"]["Flux"]["Power"] = 134
    gpuJSON[0]["Data"]["Ravencoin"]["Power"] = 226
    gpuJSON[1]["Data"]["Ravencoin"]["Power"] = 152
    gpuJSON[2]["Data"]["Ravencoin"]["Power"] = 169
    gpuJSON[3]["Data"]["Ravencoin"]["Power"] = 139

    gpuJSON[0]["Price"] = gpu0
    gpuJSON[1]["Price"] = gpu1
    gpuJSON[2]["Price"] = gpu2
    gpuJSON[3]["Price"] = gpu3
    gpuJSON[0]["Server Price"] = rig0
    gpuJSON[1]["Server Price"] = rig1
    gpuJSON[2]["Server Price"] = rig2
    gpuJSON[3]["Server Price"] = rig3

def changeGPUPrice(index, price, gpuJSON):
    gpuJSON[index]["Price"] = price

def setRigPrices(index, price, gpuJSON):
    gpuJSON[index]["Server Price"] = price