import requests

class GPU:
    def __init__(self, name, jsonurl):
        self.name = name
        self.rewards = {}
        self.btcrewards = {}
        self.usdrewards = {}
        self.data = None
        self.jsonurl = jsonurl
    def getName(self):
        return self.name
    def getReward24(self, coinname):
        return self.rewards[coinname]
    def getBTC24(self, coinname):
        return self.btcrewards[coinname]
    def getUSD24(self, coinname):
        return self.usdrewards[coinname]
    def pullData(self):
        self.data = requests.get(self.jsonurl).json()['coins']
    def pullRewardData(self, coinname):
        self.rewards[coinname] = self.data[coinname.replace(" ", "")]['estimated_rewards24']
        self.btcrewards[coinname] = self.data[coinname.replace(" ", "")]['btc_revenue24']
    def setRewardData(self, coinname, data):
        self.rewards[coinname] = data
    def setBTCData(self, coinname, data):
        self.btcrewards[coinname] = data
    def setUSDData(self, coinname, data):
        self.usdrewards[coinname] = str(data)

