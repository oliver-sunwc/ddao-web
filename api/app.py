from pkg_resources import require
import redis
import requests
import json
import copy
from api.helpers import changeGPUPrice
import helpers
from coin import Coin
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from gpu import GPU
from datetime import datetime, timedelta
from flask import Flask, jsonify, redirect, render_template, url_for

nvidia3070ti = 'https://whattomine.com/coins.json?eth=true&factor%5Beth_hr%5D=80.0&factor%5Beth_p%5D=200.0&e4g=true&factor%5Be4g_hr%5D=80.0&factor%5Be4g_p%5D=200.0&zh=true&factor%5Bzh_hr%5D=110.0&factor%5Bzh_p%5D=180.0&cnh=true&factor%5Bcnh_hr%5D=0.0&factor%5Bcnh_p%5D=0.0&cng=true&factor%5Bcng_hr%5D=3200.0&factor%5Bcng_p%5D=210.0&cnf=true&factor%5Bcnf_hr%5D=0.0&factor%5Bcnf_p%5D=0.0&cx=true&factor%5Bcx_hr%5D=0.0&factor%5Bcx_p%5D=0.0&eqa=true&factor%5Beqa_hr%5D=0.0&factor%5Beqa_p%5D=0.0&cc=true&factor%5Bcc_hr%5D=9.6&factor%5Bcc_p%5D=210.0&cr29=true&factor%5Bcr29_hr%5D=0.0&factor%5Bcr29_p%5D=0.0&ct31=true&factor%5Bct31_hr%5D=0.0&factor%5Bct31_p%5D=0.0&ct32=true&factor%5Bct32_hr%5D=0.6&factor%5Bct32_p%5D=180.0&eqb=true&factor%5Beqb_hr%5D=35.0&factor%5Beqb_p%5D=180.0&rmx=true&factor%5Brmx_hr%5D=0.0&factor%5Brmx_p%5D=0.0&ns=true&factor%5Bns_hr%5D=0.0&factor%5Bns_p%5D=0.0&al=true&factor%5Bal_hr%5D=170.0&factor%5Bal_p%5D=150.0&ops=true&factor%5Bops_hr%5D=69.0&factor%5Bops_p%5D=210.0&eqz=true&factor%5Beqz_hr%5D=0.0&factor%5Beqz_p%5D=0.0&zlh=true&factor%5Bzlh_hr%5D=61.0&factor%5Bzlh_p%5D=180.0&kpw=true&factor%5Bkpw_hr%5D=39.5&factor%5Bkpw_p%5D=250.0&ppw=true&factor%5Bppw_hr%5D=34.5&factor%5Bppw_p%5D=210.0&x25x=true&factor%5Bx25x_hr%5D=0.0&factor%5Bx25x_p%5D=0.0&fpw=true&factor%5Bfpw_hr%5D=30.5&factor%5Bfpw_p%5D=220.0&vh=true&factor%5Bvh_hr%5D=0.0&factor%5Bvh_p%5D=0.0&factor%5Bcost%5D=0.1&factor%5Bcost_currency%5D=USD&sort=Profitability24&volume=0&revenue=24h&factor%5Bexchanges%5D%5B%5D=&factor%5Bexchanges%5D%5B%5D=binance&factor%5Bexchanges%5D%5B%5D=bitfinex&factor%5Bexchanges%5D%5B%5D=bitforex&factor%5Bexchanges%5D%5B%5D=bittrex&factor%5Bexchanges%5D%5B%5D=coinex&factor%5Bexchanges%5D%5B%5D=dove&factor%5Bexchanges%5D%5B%5D=exmo&factor%5Bexchanges%5D%5B%5D=gate&factor%5Bexchanges%5D%5B%5D=graviex&factor%5Bexchanges%5D%5B%5D=hitbtc&factor%5Bexchanges%5D%5B%5D=hotbit&factor%5Bexchanges%5D%5B%5D=ogre&factor%5Bexchanges%5D%5B%5D=poloniex&factor%5Bexchanges%5D%5B%5D=stex&dataset=Main'
nvidia3070 = 'https://whattomine.com/coins.json?eth=true&factor%5Beth_hr%5D=60.0&factor%5Beth_p%5D=130.0&e4g=true&factor%5Be4g_hr%5D=60.0&factor%5Be4g_p%5D=130.0&zh=true&factor%5Bzh_hr%5D=100.0&factor%5Bzh_p%5D=180.0&cnh=true&factor%5Bcnh_hr%5D=1750.0&factor%5Bcnh_p%5D=180.0&cng=true&factor%5Bcng_hr%5D=2900.0&factor%5Bcng_p%5D=180.0&cnf=true&factor%5Bcnf_hr%5D=3400.0&factor%5Bcnf_p%5D=170.0&cx=true&factor%5Bcx_hr%5D=0.0&factor%5Bcx_p%5D=0.0&eqa=true&factor%5Beqa_hr%5D=390.0&factor%5Beqa_p%5D=180.0&cc=true&factor%5Bcc_hr%5D=10.2&factor%5Bcc_p%5D=180.0&cr29=true&factor%5Bcr29_hr%5D=10.3&factor%5Bcr29_p%5D=180.0&ct31=true&factor%5Bct31_hr%5D=0.0&factor%5Bct31_p%5D=0.0&ct32=true&factor%5Bct32_hr%5D=0.5&factor%5Bct32_p%5D=180.0&eqb=true&factor%5Beqb_hr%5D=34.0&factor%5Beqb_p%5D=180.0&rmx=true&factor%5Brmx_hr%5D=1030.0&factor%5Brmx_p%5D=160.0&ns=true&factor%5Bns_hr%5D=0.0&factor%5Bns_p%5D=0.0&al=true&factor%5Bal_hr%5D=160.0&factor%5Bal_p%5D=130.0&ops=true&factor%5Bops_hr%5D=52.7&factor%5Bops_p%5D=180.0&eqz=true&factor%5Beqz_hr%5D=55.0&factor%5Beqz_p%5D=180.0&zlh=true&factor%5Bzlh_hr%5D=61.0&factor%5Bzlh_p%5D=180.0&kpw=true&factor%5Bkpw_hr%5D=27.6&factor%5Bkpw_p%5D=180.0&ppw=true&factor%5Bppw_hr%5D=27.4&factor%5Bppw_p%5D=180.0&x25x=true&factor%5Bx25x_hr%5D=8.0&factor%5Bx25x_p%5D=180.0&fpw=true&factor%5Bfpw_hr%5D=25.0&factor%5Bfpw_p%5D=150.0&vh=true&factor%5Bvh_hr%5D=1.19&factor%5Bvh_p%5D=140.0&factor%5Bcost%5D=0.1&factor%5Bcost_currency%5D=USD&sort=Profitability24&volume=0&revenue=24h&factor%5Bexchanges%5D%5B%5D=&factor%5Bexchanges%5D%5B%5D=binance&factor%5Bexchanges%5D%5B%5D=bitfinex&factor%5Bexchanges%5D%5B%5D=bitforex&factor%5Bexchanges%5D%5B%5D=bittrex&factor%5Bexchanges%5D%5B%5D=coinex&factor%5Bexchanges%5D%5B%5D=dove&factor%5Bexchanges%5D%5B%5D=exmo&factor%5Bexchanges%5D%5B%5D=gate&factor%5Bexchanges%5D%5B%5D=graviex&factor%5Bexchanges%5D%5B%5D=hitbtc&factor%5Bexchanges%5D%5B%5D=hotbit&factor%5Bexchanges%5D%5B%5D=ogre&factor%5Bexchanges%5D%5B%5D=poloniex&factor%5Bexchanges%5D%5B%5D=stex&dataset=Main'
nvidia3060ti = 'https://whattomine.com/coins.json?eth=true&factor%5Beth_hr%5D=60.0&factor%5Beth_p%5D=140.0&e4g=true&factor%5Be4g_hr%5D=60.0&factor%5Be4g_p%5D=140.0&zh=true&factor%5Bzh_hr%5D=0.0&factor%5Bzh_p%5D=0.0&cnh=true&factor%5Bcnh_hr%5D=0.0&factor%5Bcnh_p%5D=0.0&cng=true&factor%5Bcng_hr%5D=2850.0&factor%5Bcng_p%5D=190.0&cnf=true&factor%5Bcnf_hr%5D=0.0&factor%5Bcnf_p%5D=0.0&cx=true&factor%5Bcx_hr%5D=0.0&factor%5Bcx_p%5D=0.0&eqa=true&factor%5Beqa_hr%5D=370.0&factor%5Beqa_p%5D=190.0&cc=true&factor%5Bcc_hr%5D=9.8&factor%5Bcc_p%5D=190.0&cr29=true&factor%5Bcr29_hr%5D=9.7&factor%5Bcr29_p%5D=190.0&ct31=true&factor%5Bct31_hr%5D=0.55&factor%5Bct31_p%5D=190.0&ct32=true&factor%5Bct32_hr%5D=0.5&factor%5Bct32_p%5D=190.0&eqb=true&factor%5Beqb_hr%5D=32.5&factor%5Beqb_p%5D=190.0&rmx=true&factor%5Brmx_hr%5D=0.0&factor%5Brmx_p%5D=0.0&ns=true&factor%5Bns_hr%5D=0.0&factor%5Bns_p%5D=0.0&al=true&factor%5Bal_hr%5D=160.0&factor%5Bal_p%5D=130.0&ops=true&factor%5Bops_hr%5D=48.0&factor%5Bops_p%5D=190.0&eqz=true&factor%5Beqz_hr%5D=0.0&factor%5Beqz_p%5D=0.0&zlh=true&factor%5Bzlh_hr%5D=54.5&factor%5Bzlh_p%5D=190.0&kpw=true&factor%5Bkpw_hr%5D=27.0&factor%5Bkpw_p%5D=190.0&ppw=true&factor%5Bppw_hr%5D=26.0&factor%5Bppw_p%5D=190.0&x25x=true&factor%5Bx25x_hr%5D=0.0&factor%5Bx25x_p%5D=0.0&fpw=true&factor%5Bfpw_hr%5D=25.0&factor%5Bfpw_p%5D=150.0&vh=true&factor%5Bvh_hr%5D=1.19&factor%5Bvh_p%5D=140.0&factor%5Bcost%5D=0.1&factor%5Bcost_currency%5D=USD&sort=Profitability24&volume=0&revenue=24h&factor%5Bexchanges%5D%5B%5D=&factor%5Bexchanges%5D%5B%5D=binance&factor%5Bexchanges%5D%5B%5D=bitfinex&factor%5Bexchanges%5D%5B%5D=bitforex&factor%5Bexchanges%5D%5B%5D=bittrex&factor%5Bexchanges%5D%5B%5D=coinex&factor%5Bexchanges%5D%5B%5D=dove&factor%5Bexchanges%5D%5B%5D=exmo&factor%5Bexchanges%5D%5B%5D=gate&factor%5Bexchanges%5D%5B%5D=graviex&factor%5Bexchanges%5D%5B%5D=hitbtc&factor%5Bexchanges%5D%5B%5D=hotbit&factor%5Bexchanges%5D%5B%5D=ogre&factor%5Bexchanges%5D%5B%5D=poloniex&factor%5Bexchanges%5D%5B%5D=stex&dataset=Main'
nvidia3060 = 'https://whattomine.com/coins.json?eth=true&factor%5Beth_hr%5D=41.0&factor%5Beth_p%5D=110.0&e4g=true&factor%5Be4g_hr%5D=41.0&factor%5Be4g_p%5D=110.0&zh=true&factor%5Bzh_hr%5D=0.0&factor%5Bzh_p%5D=0.0&cnh=true&factor%5Bcnh_hr%5D=0.0&factor%5Bcnh_p%5D=0.0&cng=true&factor%5Bcng_hr%5D=0.0&factor%5Bcng_p%5D=0.0&cnf=true&factor%5Bcnf_hr%5D=0.0&factor%5Bcnf_p%5D=0.0&cx=true&factor%5Bcx_hr%5D=2.3&factor%5Bcx_p%5D=120.0&eqa=true&factor%5Beqa_hr%5D=250.0&factor%5Beqa_p%5D=140.0&cc=true&factor%5Bcc_hr%5D=7.0&factor%5Bcc_p%5D=140.0&cr29=true&factor%5Bcr29_hr%5D=0.0&factor%5Bcr29_p%5D=0.0&ct31=true&factor%5Bct31_hr%5D=1.2&factor%5Bct31_p%5D=140.0&ct32=true&factor%5Bct32_hr%5D=0.45&factor%5Bct32_p%5D=140.0&eqb=true&factor%5Beqb_hr%5D=22.0&factor%5Beqb_p%5D=140.0&rmx=true&factor%5Brmx_hr%5D=0.0&factor%5Brmx_p%5D=0.0&ns=true&factor%5Bns_hr%5D=0.0&factor%5Bns_p%5D=0.0&al=true&factor%5Bal_hr%5D=115.0&factor%5Bal_p%5D=110.0&ops=true&factor%5Bops_hr%5D=42.0&factor%5Bops_p%5D=140.0&eqz=true&factor%5Beqz_hr%5D=0.0&factor%5Beqz_p%5D=0.0&zlh=true&factor%5Bzlh_hr%5D=36.0&factor%5Bzlh_p%5D=140.0&kpw=true&factor%5Bkpw_hr%5D=22.0&factor%5Bkpw_p%5D=140.0&ppw=true&factor%5Bppw_hr%5D=21.5&factor%5Bppw_p%5D=140.0&x25x=true&factor%5Bx25x_hr%5D=0.0&factor%5Bx25x_p%5D=0.0&fpw=true&factor%5Bfpw_hr%5D=20.5&factor%5Bfpw_p%5D=140.0&vh=true&factor%5Bvh_hr%5D=0.37&factor%5Bvh_p%5D=130.0&factor%5Bcost%5D=0.1&factor%5Bcost_currency%5D=USD&sort=Profitability24&volume=0&revenue=24h&factor%5Bexchanges%5D%5B%5D=&factor%5Bexchanges%5D%5B%5D=binance&factor%5Bexchanges%5D%5B%5D=bitfinex&factor%5Bexchanges%5D%5B%5D=bitforex&factor%5Bexchanges%5D%5B%5D=bittrex&factor%5Bexchanges%5D%5B%5D=coinex&factor%5Bexchanges%5D%5B%5D=dove&factor%5Bexchanges%5D%5B%5D=exmo&factor%5Bexchanges%5D%5B%5D=gate&factor%5Bexchanges%5D%5B%5D=graviex&factor%5Bexchanges%5D%5B%5D=hitbtc&factor%5Bexchanges%5D%5B%5D=hotbit&factor%5Bexchanges%5D%5B%5D=ogre&factor%5Bexchanges%5D%5B%5D=poloniex&factor%5Bexchanges%5D%5B%5D=stex&dataset=Main'

app = Flask(__name__)

redis_client = redis.Redis(host='localhost', port=6379, db=0)

coinIndex = {}
gpuIndex = {}
gpuIndex["3070Ti"] = GPU("3070Ti", nvidia3070ti)
gpuIndex["3070"] = GPU("3070", nvidia3070)
gpuIndex["3060Ti"] = GPU("3060Ti", nvidia3060ti)
gpuIndex["3060"] = GPU("3060", nvidia3060)

coinJSON = []
gpuJSON = []
rigJSON = []

##get from redis/update redis

def updateData(coinIndex, gpuIndex):
    check = redis_client.scan(0)[1]
    if len(check) == 0:
        print("Not in cache, grabbing from API")
        helpers.createIndex(coinIndex)
        for gpu in gpuIndex:
            gpuIndex[gpu].pullData()
        for coin in coinIndex:
            redis_client.hset(coinIndex[coin].getName(), 'id', coinIndex[coin].getID())
            redis_client.hset(coinIndex[coin].getName(), 'symbol', coinIndex[coin].getSymbol())
            redis_client.hset(coinIndex[coin].getName(), 'current_price', coinIndex[coin].getPrice())
            redis_client.hset(coinIndex[coin].getName(), 'ath', coinIndex[coin].getATH())
            redis_client.hset(coinIndex[coin].getName(), 'atl', coinIndex[coin].getATL())
            redis_client.expire(coinIndex[coin].getName(), timedelta(seconds=30))
            if coin != 'Bitcoin':
                for gpu in gpuIndex:
                    gpuIndex[gpu].pullRewardData(coin)
                    data = gpuIndex[gpu].getReward24(coin)
                    btcdata = gpuIndex[gpu].getBTC24(coin)
                    gpuIndex[gpu].setUSDData(coin, float(data)*float(coinIndex[coin].getPrice()))
                    usdData = gpuIndex[gpu].getUSD24(coin)
                    coin24 = coin + '_reward24'
                    btc24 = coin + '_btc24'
                    usd24 = coin + '_usd24'
                    redis_client.hset(gpu, coin24, data)
                    redis_client.hset(gpu, btc24, btcdata)
                    redis_client.hset(gpu, usd24, usdData)
                    redis_client.expire(gpu, timedelta(seconds=30))
    else:
        print("Cache found, serving from redis")
        for x in check:
            c = x.decode('utf-8')
            if redis_client.hexists(c, 'isCoin'):
                coinIndex[c] = Coin(c, redis_client.hget(c, 'id').decode('utf-8'), redis_client.hget(c, 'symbol').decode('utf-8'))
                coinIndex[c].setPrice(redis_client.hget(c, 'current_price').decode('utf-8'), redis_client.hget(c, 'ath').decode('utf-8'), redis_client.hget(c, 'atl').decode('utf-8'))
                for gpu in gpuIndex:
                    if(c != "Bitcoin"):
                        c24 = c + '_reward24'
                        b24 = c + '_btc24'
                        u24 = c + '_usd24'
                        gpuIndex[gpu].setRewardData(c, redis_client.hget(gpu, c24).decode('utf-8'))
                        gpuIndex[gpu].setBTCData(c, redis_client.hget(gpu, b24).decode('utf-8'))
                        gpuIndex[gpu].setUSDData(c, redis_client.hget(gpu, u24).decode('utf-8'))

##create rig json

def createJSON(rigJSON, gpuJSON, coinJSON, coinIndex, gpuIndex):
    rigRows = [
        "Annual Income in Crypto",
        "Annual Income ($)",
        "Annual Electricity Cost ($)",
        "Annual Gross Margin ($)",
        "Annual Gross ROI",
        "Amortization (5Y)",
        "Support and Management Fee (5%)",
        "Annual Net Income",
        "Annual Net ROI",
        "5Y Net Income",
        "5Y Net ROI",
        "Shutdown Price Threshold",
        "Breakeven Price Threshold"
    ]

    for header in rigRows:
        rigJSON.append({"Header": header, "gpu" : {}})

    for gpu in gpuIndex:
        gpuJSON.append({"Data": {}, "Name" : gpu})
    for coin in coinIndex:
        new = {'Name' : coin , 'Symbol' : coinIndex[coin].getSymbol(), 'Price' : coinIndex[coin].getPrice(), 'ATH' : coinIndex[coin].getATH(), 'ATL' : coinIndex[coin].getATL()}
        coinJSON.append(new)
        for gpu in gpuIndex:
            new = {coin: {'24h' : gpuIndex[gpu].getReward24(coin), '24hBTC' : gpuIndex[gpu].getBTC24(coin), '24hUSD' : gpuIndex[gpu].getUSD24(coin)}}
            if(gpu == "3070Ti"):
                init = gpuJSON[0]["Data"]
                gpuJSON[0]["Data"] = init | new
            if(gpu == "3070"):
                init = gpuJSON[1]["Data"]
                gpuJSON[1]["Data"] = init | new
            if(gpu == "3060Ti"):
                init = gpuJSON[2]["Data"]
                gpuJSON[2]["Data"] = init | new
            if(gpu == "3060"):
                init = gpuJSON[3]["Data"]
                gpuJSON[3]["Data"] = init | new
                
    for header in rigJSON:
        for gpu in gpuJSON:
            init = header["gpu"]
            
            header["gpu"] = init | {gpu["Name"] : {}}

    helpers.setGPUPrices(gpuJSON)

    for gpu in gpuJSON:
        max = -999999
        for coin in coinJSON:
            rigJSON[0]["gpu"][gpu["Name"]][coin["Name"]] = float(gpu["Data"][coin["Name"]]["24h"])*8*365
            rigJSON[1]["gpu"][gpu["Name"]][coin["Name"]] = float(gpu["Data"][coin["Name"]]["24hUSD"])*8*365
            rigJSON[2]["gpu"][gpu["Name"]][coin["Name"]] = (float(gpu["Data"][coin["Name"]]["Power"])*8+300)/1000*24*0.1*365
            rigJSON[3]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[1]["gpu"][gpu["Name"]][coin["Name"]] - rigJSON[2]["gpu"][gpu["Name"]][coin["Name"]]
            rigJSON[4]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[3]["gpu"][gpu["Name"]][coin['Name']]/(gpu["Price"]*8 + gpu["Server Price"])
            rigJSON[5]["gpu"][gpu["Name"]][coin['Name']] = (gpu["Price"]*8 + gpu["Server Price"])/5
            rigJSON[6]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[1]["gpu"][gpu["Name"]][coin['Name']]*0.05
            rigJSON[7]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[3]["gpu"][gpu["Name"]][coin['Name']] - rigJSON[5]["gpu"][gpu["Name"]][coin['Name']] - rigJSON[6]["gpu"][gpu["Name"]][coin['Name']]
            rigJSON[8]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[7]["gpu"][gpu["Name"]][coin['Name']]/(gpu["Price"]*8 + gpu["Server Price"])
            if(rigJSON[8]["gpu"][gpu["Name"]][coin['Name']] > max):
                max = rigJSON[8]["gpu"][gpu["Name"]][coin['Name']]
                rigJSON[8]["gpu"][gpu["Name"]]["best"] = coin["Name"]
            rigJSON[9]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[7]["gpu"][gpu["Name"]][coin['Name']]*5
            rigJSON[10]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[8]["gpu"][gpu["Name"]][coin['Name']]*5
            if(rigJSON[0]["gpu"][gpu["Name"]][coin['Name']] != 0):
                rigJSON[11]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[2]["gpu"][gpu["Name"]][coin['Name']]/rigJSON[0]["gpu"][gpu["Name"]][coin['Name']]
                rigJSON[12]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[11]["gpu"][gpu["Name"]][coin['Name']]+(rigJSON[5]["gpu"][gpu["Name"]][coin['Name']]+rigJSON[6]["gpu"][gpu["Name"]][coin['Name']])/5
                rigJSON[11]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[11]["gpu"][gpu["Name"]][coin['Name']])
                rigJSON[12]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[12]["gpu"][gpu["Name"]][coin['Name']])
            else:
                rigJSON[11]["gpu"][gpu["Name"]][coin['Name']] = "N/A"
                rigJSON[12]["gpu"][gpu["Name"]][coin['Name']] = "N/A"

            rigJSON[0]["gpu"][gpu["Name"]][coin["Name"]] = str(rigJSON[0]["gpu"][gpu["Name"]][coin["Name"]]) + " " + coin['Symbol'].upper()
            rigJSON[1]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[1]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[2]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[2]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[3]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[3]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[4]["gpu"][gpu["Name"]][coin['Name']] = helpers.toPercent(rigJSON[4]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[5]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[5]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[6]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[6]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[7]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[7]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[8]["gpu"][gpu["Name"]][coin['Name']] = helpers.toPercent(rigJSON[8]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[9]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[9]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[10]["gpu"][gpu["Name"]][coin['Name']] = helpers.toPercent(rigJSON[10]["gpu"][gpu["Name"]][coin['Name']])

def recalcGPU(rigJSON, gpuJSON, coinJSON, gpu0=599.0, gpu1=499.0, gpu2=499.0, gpu3= 329.0):

    helpers.setGPUPrices(gpuJSON, gpu0, gpu1, gpu2, gpu3)

    for gpu in gpuJSON:
        max = -999999
        for coin in coinJSON:
            rigJSON[0]["gpu"][gpu["Name"]][coin["Name"]] = float(gpu["Data"][coin["Name"]]["24h"])*8*365
            rigJSON[1]["gpu"][gpu["Name"]][coin["Name"]] = float(gpu["Data"][coin["Name"]]["24hUSD"])*8*365
            rigJSON[2]["gpu"][gpu["Name"]][coin["Name"]] = (float(gpu["Data"][coin["Name"]]["Power"])*8+300)/1000*24*0.1*365
            rigJSON[3]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[1]["gpu"][gpu["Name"]][coin["Name"]] - rigJSON[2]["gpu"][gpu["Name"]][coin["Name"]]
            rigJSON[4]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[3]["gpu"][gpu["Name"]][coin['Name']]/(gpu["Price"]*8 + gpu["Server Price"])
            rigJSON[5]["gpu"][gpu["Name"]][coin['Name']] = (gpu["Price"]*8 + gpu["Server Price"])/5
            rigJSON[6]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[1]["gpu"][gpu["Name"]][coin['Name']]*0.05
            rigJSON[7]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[3]["gpu"][gpu["Name"]][coin['Name']] - rigJSON[5]["gpu"][gpu["Name"]][coin['Name']] - rigJSON[6]["gpu"][gpu["Name"]][coin['Name']]
            rigJSON[8]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[7]["gpu"][gpu["Name"]][coin['Name']]/(gpu["Price"]*8 + gpu["Server Price"])
            if(rigJSON[8]["gpu"][gpu["Name"]][coin['Name']] > max):
                max = rigJSON[8]["gpu"][gpu["Name"]][coin['Name']]
                rigJSON[8]["gpu"][gpu["Name"]]["best"] = coin["Name"]
            rigJSON[9]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[7]["gpu"][gpu["Name"]][coin['Name']]*5
            rigJSON[10]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[8]["gpu"][gpu["Name"]][coin['Name']]*5
            if(rigJSON[0]["gpu"][gpu["Name"]][coin['Name']] != 0):
                rigJSON[11]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[2]["gpu"][gpu["Name"]][coin['Name']]/rigJSON[0]["gpu"][gpu["Name"]][coin['Name']]
                rigJSON[12]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[11]["gpu"][gpu["Name"]][coin['Name']]+(rigJSON[5]["gpu"][gpu["Name"]][coin['Name']]+rigJSON[6]["gpu"][gpu["Name"]][coin['Name']])/5
                rigJSON[11]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[11]["gpu"][gpu["Name"]][coin['Name']])
                rigJSON[12]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[12]["gpu"][gpu["Name"]][coin['Name']])
            else:
                rigJSON[11]["gpu"][gpu["Name"]][coin['Name']] = "N/A"
                rigJSON[12]["gpu"][gpu["Name"]][coin['Name']] = "N/A"

            rigJSON[0]["gpu"][gpu["Name"]][coin["Name"]] = str(rigJSON[0]["gpu"][gpu["Name"]][coin["Name"]]) + " " + coin['Symbol'].upper()
            rigJSON[1]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[1]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[2]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[2]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[3]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[3]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[4]["gpu"][gpu["Name"]][coin['Name']] = helpers.toPercent(rigJSON[4]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[5]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[5]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[6]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[6]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[7]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[7]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[8]["gpu"][gpu["Name"]][coin['Name']] = helpers.toPercent(rigJSON[8]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[9]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[9]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[10]["gpu"][gpu["Name"]][coin['Name']] = helpers.toPercent(rigJSON[10]["gpu"][gpu["Name"]][coin['Name']])

def recalc():
    for gpu in gpuJSON:
        max = -999999
        for coin in coinJSON:
            rigJSON[0]["gpu"][gpu["Name"]][coin["Name"]] = float(gpu["Data"][coin["Name"]]["24h"])*8*365
            rigJSON[1]["gpu"][gpu["Name"]][coin["Name"]] = float(gpu["Data"][coin["Name"]]["24hUSD"])*8*365
            rigJSON[2]["gpu"][gpu["Name"]][coin["Name"]] = (float(gpu["Data"][coin["Name"]]["Power"])*8+300)/1000*24*0.1*365
            rigJSON[3]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[1]["gpu"][gpu["Name"]][coin["Name"]] - rigJSON[2]["gpu"][gpu["Name"]][coin["Name"]]
            rigJSON[4]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[3]["gpu"][gpu["Name"]][coin['Name']]/(gpu["Price"]*8 + gpu["Server Price"])
            rigJSON[5]["gpu"][gpu["Name"]][coin['Name']] = (gpu["Price"]*8 + gpu["Server Price"])/5
            rigJSON[6]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[1]["gpu"][gpu["Name"]][coin['Name']]*0.05
            rigJSON[7]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[3]["gpu"][gpu["Name"]][coin['Name']] - rigJSON[5]["gpu"][gpu["Name"]][coin['Name']] - rigJSON[6]["gpu"][gpu["Name"]][coin['Name']]
            rigJSON[8]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[7]["gpu"][gpu["Name"]][coin['Name']]/(gpu["Price"]*8 + gpu["Server Price"])
            if(rigJSON[8]["gpu"][gpu["Name"]][coin['Name']] > max):
                max = rigJSON[8]["gpu"][gpu["Name"]][coin['Name']]
                rigJSON[8]["gpu"][gpu["Name"]]["best"] = coin["Name"]
            rigJSON[9]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[7]["gpu"][gpu["Name"]][coin['Name']]*5
            rigJSON[10]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[8]["gpu"][gpu["Name"]][coin['Name']]*5
            if(rigJSON[0]["gpu"][gpu["Name"]][coin['Name']] != 0):
                rigJSON[11]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[2]["gpu"][gpu["Name"]][coin['Name']]/rigJSON[0]["gpu"][gpu["Name"]][coin['Name']]
                rigJSON[12]["gpu"][gpu["Name"]][coin['Name']] = rigJSON[11]["gpu"][gpu["Name"]][coin['Name']]+(rigJSON[5]["gpu"][gpu["Name"]][coin['Name']]+rigJSON[6]["gpu"][gpu["Name"]][coin['Name']])/5
                rigJSON[11]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[11]["gpu"][gpu["Name"]][coin['Name']])
                rigJSON[12]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[12]["gpu"][gpu["Name"]][coin['Name']])
            else:
                rigJSON[11]["gpu"][gpu["Name"]][coin['Name']] = "N/A"
                rigJSON[12]["gpu"][gpu["Name"]][coin['Name']] = "N/A"

            rigJSON[0]["gpu"][gpu["Name"]][coin["Name"]] = str(rigJSON[0]["gpu"][gpu["Name"]][coin["Name"]]) + " " + coin['Symbol'].upper()
            rigJSON[1]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[1]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[2]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[2]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[3]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[3]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[4]["gpu"][gpu["Name"]][coin['Name']] = helpers.toPercent(rigJSON[4]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[5]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[5]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[6]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[6]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[7]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[7]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[8]["gpu"][gpu["Name"]][coin['Name']] = helpers.toPercent(rigJSON[8]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[9]["gpu"][gpu["Name"]][coin['Name']] = helpers.toCurrency(rigJSON[9]["gpu"][gpu["Name"]][coin['Name']])
            rigJSON[10]["gpu"][gpu["Name"]][coin['Name']] = helpers.toPercent(rigJSON[10]["gpu"][gpu["Name"]][coin['Name']])

updateData(coinIndex, gpuIndex)
createJSON(rigJSON, gpuJSON, coinJSON, coinIndex, gpuIndex)

@app.route("/api/data/coin")
def coinData():
    return jsonify(coinJSON)

@app.route("/api/data/gpu")
def gpuData():
    return jsonify(gpuJSON)

@app.route("/api/data/gpu/<string:gpuname>", methods=['GET'])
def getGPUData(gpuname):
    for gpu in gpuJSON:
        if gpu["Name"] == gpuname:
            return jsonify(gpu)
    return jsonify(gpuJSON)

@app.route("/api/data/gpu/<string:gpuname>/<string:gpuprice>", methods=['GET'])
def setGPUData(gpuname, gpuprice):
    i = 0
    gpuprice = float(gpuprice)
    for gpu in gpuJSON:
        if gpu["Name"] == gpuname:
            helpers.changeGPUPrice(i, gpuprice, gpuJSON)
            recalc()
            return jsonify(gpu)
        i+=1
    return jsonify(gpuJSON)

@app.route("/api/data/rig/<string:gpuname>/<string:rigprice>", methods=['GET'])
def setRigData(gpuname, rigprice):
    i = 0
    rigprice = float(rigprice)
    for gpu in gpuJSON:
        if gpu["Name"] == gpuname:
            helpers.setRigPrices(i, rigprice, gpuJSON)
            recalc()
            return jsonify(gpu)
        i+=1
    return jsonify(gpuJSON)

@app.route("/api/data/rig")
def rigData():
    return jsonify(rigJSON)

@app.route("/api/data/rig/best")
def best():
    bestJSON = []
    rigRows = [
        "Monthly Income in Crypto",
        "Monthly Income ($)",
        "Monthly Electricity Cost ($)",
        "Monthly Gross Margin ($)",
        "Monthly Gross ROI",
        "Rig Amortization Per Month",
        "Support and Management Fee (5%)",
        "Monthly Net Income",
        "Monthly Net ROI",
        "Electricity Per Month (kWh)"
    ]

    for header in rigRows:
        bestJSON.append({"Header": header, "gpu" : {}})

    top1 = -999999
    top2 = -999999
    no1 = ""
    no2 = ""
    p1 = 0
    p2 = 0

    for gpu in gpuJSON:
        bestJSON[0]["gpu"][gpu["Name"]] = float(gpu["Data"][rigJSON[8]["gpu"][gpu["Name"]]["best"]]["24h"])*8*365*1000/12
        bestJSON[1]["gpu"][gpu["Name"]] = float(gpu["Data"][rigJSON[8]["gpu"][gpu["Name"]]["best"]]["24hUSD"])*8*365*1000/12
        bestJSON[2]["gpu"][gpu["Name"]] = rigJSON[2]["gpu"][gpu["Name"]][rigJSON[8]["gpu"][gpu["Name"]]["best"]] = (float(gpu["Data"][rigJSON[8]["gpu"][gpu["Name"]]["best"]]["Power"])*8+300)/1000*24*0.1*365*1000/12
        bestJSON[3]["gpu"][gpu["Name"]] = bestJSON[1]["gpu"][gpu["Name"]] - bestJSON[2]["gpu"][gpu["Name"]]
        bestJSON[4]["gpu"][gpu["Name"]] = bestJSON[3]["gpu"][gpu["Name"]]/((gpu["Price"]*8 + gpu["Server Price"])*1000)
        bestJSON[5]["gpu"][gpu["Name"]] = (gpu["Price"]*8 + gpu["Server Price"])/5*1000/12
        bestJSON[6]["gpu"][gpu["Name"]] = bestJSON[1]["gpu"][gpu["Name"]]*0.05
        bestJSON[7]["gpu"][gpu["Name"]] = bestJSON[3]["gpu"][gpu["Name"]] - bestJSON[5]["gpu"][gpu["Name"]] - bestJSON[6]["gpu"][gpu["Name"]]
        bestJSON[8]["gpu"][gpu["Name"]] = bestJSON[7]["gpu"][gpu["Name"]]/((gpu["Price"]*8 + gpu["Server Price"])*1000)
        bestJSON[9]["gpu"][gpu["Name"]] = bestJSON[2]["gpu"][gpu["Name"]]/0.1

        


        sym = ""
        for coin in coinJSON:
            if rigJSON[8]["gpu"][gpu["Name"]]["best"] == coin['Name']:
                sym = coin['Symbol'].upper()

        if bestJSON[8]["gpu"][gpu["Name"]] > top1:
            top1 = bestJSON[8]["gpu"][gpu["Name"]]
            no1 = gpu["Name"]
            print("no1 " + no1)

            bestJSON[0]["no1"] = float(gpu["Data"][rigJSON[8]["gpu"][gpu["Name"]]["best"]]["24h"])*8*365*1000/12
            bestJSON[1]["no1"] = float(gpu["Data"][rigJSON[8]["gpu"][gpu["Name"]]["best"]]["24hUSD"])*8*365*1000/12
            bestJSON[2]["no1"] = rigJSON[2]["gpu"][gpu["Name"]][rigJSON[8]["gpu"][gpu["Name"]]["best"]] = (float(gpu["Data"][rigJSON[8]["gpu"][gpu["Name"]]["best"]]["Power"])*8+300)/1000*24*0.1*365*1000/12
            bestJSON[3]["no1"] = bestJSON[1]["gpu"][gpu["Name"]] - bestJSON[2]["gpu"][gpu["Name"]]
            bestJSON[4]["no1"] = bestJSON[3]["gpu"][gpu["Name"]]/((gpu["Price"]*8 + gpu["Server Price"])*1000)
            p1 = ((gpu["Price"]*8 + gpu["Server Price"])*1000)
            bestJSON[5]["no1"] = (gpu["Price"]*8 + gpu["Server Price"])/5*1000/12
            bestJSON[6]["no1"] = bestJSON[1]["gpu"][gpu["Name"]]*0.05
            bestJSON[7]["no1"] = bestJSON[3]["gpu"][gpu["Name"]] - bestJSON[5]["gpu"][gpu["Name"]] - bestJSON[6]["gpu"][gpu["Name"]]
            bestJSON[8]["no1"] = bestJSON[7]["gpu"][gpu["Name"]]/((gpu["Price"]*8 + gpu["Server Price"])*1000)
            bestJSON[9]["no1"] = bestJSON[2]["gpu"][gpu["Name"]]/0.1

            for header in bestJSON:
                header["no1name"] = no1
                header["no1coin"] = sym
        
    for gpu in gpuJSON:
        sym = ""
        for coin in coinJSON:
            if rigJSON[8]["gpu"][gpu["Name"]]["best"] == coin['Name']:
                sym = coin['Symbol'].upper()

        if bestJSON[8]["gpu"][gpu["Name"]] > top2 and bestJSON[8]["gpu"][gpu["Name"]] < top1:
            top2 = bestJSON[8]["gpu"][gpu["Name"]]
            no2 = gpu["Name"]
            print("no2 " + no2)

            bestJSON[0]["no2"] = float(gpu["Data"][rigJSON[8]["gpu"][gpu["Name"]]["best"]]["24h"])*8*365*1000/12
            bestJSON[1]["no2"] = float(gpu["Data"][rigJSON[8]["gpu"][gpu["Name"]]["best"]]["24hUSD"])*8*365*1000/12
            bestJSON[2]["no2"] = rigJSON[2]["gpu"][gpu["Name"]][rigJSON[8]["gpu"][gpu["Name"]]["best"]] = (float(gpu["Data"][rigJSON[8]["gpu"][gpu["Name"]]["best"]]["Power"])*8+300)/1000*24*0.1*365*1000/12
            bestJSON[3]["no2"] = bestJSON[1]["gpu"][gpu["Name"]] - bestJSON[2]["gpu"][gpu["Name"]]
            bestJSON[4]["no2"] = bestJSON[3]["gpu"][gpu["Name"]]/((gpu["Price"]*8 + gpu["Server Price"])*1000)
            p2 = ((gpu["Price"]*8 + gpu["Server Price"])*1000)
            bestJSON[5]["no2"] = (gpu["Price"]*8 + gpu["Server Price"])/5*1000/12
            bestJSON[6]["no2"] = bestJSON[1]["gpu"][gpu["Name"]]*0.05
            bestJSON[7]["no2"] = bestJSON[3]["gpu"][gpu["Name"]] - bestJSON[5]["gpu"][gpu["Name"]] - bestJSON[6]["gpu"][gpu["Name"]]
            bestJSON[8]["no2"] = bestJSON[7]["gpu"][gpu["Name"]]/((gpu["Price"]*8 + gpu["Server Price"])*1000)
            bestJSON[9]["no2"] = bestJSON[2]["gpu"][gpu["Name"]]/0.1

            for header in bestJSON:
                header["no2name"] = no2
                header["no2coin"] = sym
            
    bestJSON[0]["total"] = '-'
    bestJSON[1]["total"] = bestJSON[1]["no1"] + bestJSON[1]["no2"]
    bestJSON[2]["total"] = bestJSON[2]["no1"] + bestJSON[2]["no2"]
    bestJSON[3]["total"] = bestJSON[3]["no1"] + bestJSON[3]["no2"]
    bestJSON[4]["total"] = bestJSON[3]["total"]/(p1+p2)
    bestJSON[5]["total"] = bestJSON[5]["no1"] + bestJSON[5]["no2"]
    bestJSON[6]["total"] = bestJSON[6]["no1"] + bestJSON[6]["no2"]
    bestJSON[7]["total"] = bestJSON[7]["no1"] + bestJSON[7]["no2"]
    bestJSON[8]["total"] = bestJSON[7]["total"]/(p1+p2)
    bestJSON[9]["total"] = bestJSON[9]["no1"] + bestJSON[9]["no2"]


    for gpu in gpuJSON: 
        sym = ""
        for coin in coinJSON:
            if rigJSON[8]["gpu"][gpu["Name"]]["best"] == coin['Name']:
                sym = coin['Symbol'].upper()

        

        bestJSON[0]["gpu"][gpu["Name"]] = str(bestJSON[0]["gpu"][gpu["Name"]]) + " " + sym
        bestJSON[1]["gpu"][gpu["Name"]] = helpers.toCurrency(bestJSON[1]["gpu"][gpu["Name"]])
        bestJSON[2]["gpu"][gpu["Name"]] = helpers.toCurrency(bestJSON[2]["gpu"][gpu["Name"]])
        bestJSON[3]["gpu"][gpu["Name"]] = helpers.toCurrency(bestJSON[3]["gpu"][gpu["Name"]])
        bestJSON[4]["gpu"][gpu["Name"]] = helpers.toPercent(bestJSON[4]["gpu"][gpu["Name"]])
        bestJSON[5]["gpu"][gpu["Name"]] = helpers.toCurrency(bestJSON[5]["gpu"][gpu["Name"]])
        bestJSON[6]["gpu"][gpu["Name"]] = helpers.toCurrency(bestJSON[6]["gpu"][gpu["Name"]])
        bestJSON[7]["gpu"][gpu["Name"]] = helpers.toCurrency(bestJSON[7]["gpu"][gpu["Name"]])
        bestJSON[8]["gpu"][gpu["Name"]] = helpers.toPercent(bestJSON[8]["gpu"][gpu["Name"]])
        bestJSON[9]["gpu"][gpu["Name"]] = str(int(bestJSON[9]["gpu"][gpu["Name"]]))

    bestJSON[0]["no1"] = str(bestJSON[0]["no1"]) + " " + bestJSON[0]["no1coin"]
    bestJSON[1]["no1"] = helpers.toCurrency(bestJSON[1]["no1"])
    bestJSON[2]["no1"] = helpers.toCurrency(bestJSON[2]["no1"])
    bestJSON[3]["no1"] = helpers.toCurrency(bestJSON[3]["no1"])
    bestJSON[4]["no1"] = helpers.toPercent(bestJSON[4]["no1"])
    bestJSON[5]["no1"] = helpers.toCurrency(bestJSON[5]["no1"])
    bestJSON[6]["no1"] = helpers.toCurrency(bestJSON[6]["no1"])
    bestJSON[7]["no1"] = helpers.toCurrency(bestJSON[7]["no1"])
    bestJSON[8]["no1"] = helpers.toPercent(bestJSON[8]["no1"])
    bestJSON[9]["no1"] = str(int(bestJSON[9]["no1"]))

    bestJSON[0]["no2"] = str(bestJSON[0]["no2"]) + " " + bestJSON[0]["no2coin"]
    bestJSON[1]["no2"] = helpers.toCurrency(bestJSON[1]["no2"])
    bestJSON[2]["no2"] = helpers.toCurrency(bestJSON[2]["no2"])
    bestJSON[3]["no2"] = helpers.toCurrency(bestJSON[3]["no2"])
    bestJSON[4]["no2"] = helpers.toPercent(bestJSON[4]["no2"])
    bestJSON[5]["no2"] = helpers.toCurrency(bestJSON[5]["no2"])
    bestJSON[6]["no2"] = helpers.toCurrency(bestJSON[6]["no2"])
    bestJSON[7]["no2"] = helpers.toCurrency(bestJSON[7]["no2"])
    bestJSON[8]["no2"] = helpers.toPercent(bestJSON[8]["no2"])
    bestJSON[9]["no2"] = str(int(bestJSON[9]["no2"]))

    bestJSON[1]["total"] = helpers.toCurrency(bestJSON[1]["total"])
    bestJSON[2]["total"] = helpers.toCurrency(bestJSON[2]["total"])
    bestJSON[3]["total"] = helpers.toCurrency(bestJSON[3]["total"])
    bestJSON[4]["total"] = helpers.toPercent(bestJSON[4]["total"])
    bestJSON[5]["total"] = helpers.toCurrency(bestJSON[5]["total"])
    bestJSON[6]["total"] = helpers.toCurrency(bestJSON[6]["total"])
    bestJSON[7]["total"] = helpers.toCurrency(bestJSON[7]["total"])
    bestJSON[8]["total"] = helpers.toPercent(bestJSON[8]["total"])
    bestJSON[9]["total"] = str(int(bestJSON[9]["total"]))
        
        

    return jsonify(bestJSON)


@app.route("/api/refresh")
def refresh():
    gpuPrices = [gpuJSON[0]["Price"], gpuJSON[1]["Price"], gpuJSON[2]["Price"], gpuJSON[3]["Price"]]
    rigPrices = [gpuJSON[0]["Server Price"], gpuJSON[0]["Server Price"], gpuJSON[0]["Server Price"], gpuJSON[0]["Server Price"]]
    coinIndex = {}
    gpuIndex = {}
    gpuIndex["3070Ti"] = GPU("3070Ti", nvidia3070ti)
    gpuIndex["3070"] = GPU("3070", nvidia3070)
    gpuIndex["3060Ti"] = GPU("3060Ti", nvidia3060ti)
    gpuIndex["3060"] = GPU("3060", nvidia3060)
    coinJSON.clear()
    gpuJSON.clear()
    updateData(coinIndex, gpuIndex)
    for gpu in gpuIndex:
        gpuJSON.append({"Data": {}, "Name" : gpu})
    for coin in coinIndex:
        new = {'Name' : coin , 'Symbol' : coinIndex[coin].getSymbol(), 'Price' : coinIndex[coin].getPrice(), 'ATH' : coinIndex[coin].getATH(), 'ATL' : coinIndex[coin].getATL()}
        coinJSON.append(new)
        for gpu in gpuIndex:
            new = {coin: {'24h' : gpuIndex[gpu].getReward24(coin), '24hBTC' : gpuIndex[gpu].getBTC24(coin), '24hUSD' : gpuIndex[gpu].getUSD24(coin)}}
            if(gpu == "3070Ti"):
                init = gpuJSON[0]["Data"]
                gpuJSON[0]["Data"] = init | new
            if(gpu == "3070"):
                init = gpuJSON[1]["Data"]
                gpuJSON[1]["Data"] = init | new
            if(gpu == "3060Ti"):
                init = gpuJSON[2]["Data"]
                gpuJSON[2]["Data"] = init | new
            if(gpu == "3060"):
                init = gpuJSON[3]["Data"]
                gpuJSON[3]["Data"] = init | new

    helpers.setGPUPrices(gpuJSON, gpuPrices[0], gpuPrices[1], gpuPrices[2], gpuPrices[3], rigPrices[0], rigPrices[1], rigPrices[2], rigPrices[3])

    recalc()
    return jsonify(rigJSON)


app.run(host='localhost', debug=True)
