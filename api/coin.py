class Coin():
    def __init__(self, name, id, symbol):
        self.name = name
        self.id = id
        self.symbol = symbol
        self.current_price = None
        self.ath = None
        self.atl = None
    def getName(self):
        return self.name
    def getID(self):
        return self.id
    def getSymbol(self):
        return self.symbol
    def getPrice(self):
        return self.current_price
    def getATH(self):
        return self.ath
    def getATL(self):
        return self.atl
    def setName(self, name, id, symbol):
        self.name = name
        self.id = id
        self.symbol = symbol
    def setPrice(self, current_price, ath, atl):
        self.current_price = current_price
        self.ath = ath
        self.atl = atl

