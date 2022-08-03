from datetime import datetime
import numpy as np
# import matplotlib.pyplot as plt
import pandas as pd
from ..products.AsianOptions import opt
from ..finutils.FinDate import FinDate
from ..finutils.FinError import FinError

emptyTable = {
    2201 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2202 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2203 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2204 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2205 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2206 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2207 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2208 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2209 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2210 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2211 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2212 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2301 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2302 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2303 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2304 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2305 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2306 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2307 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2308 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2309 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2310 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2311 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2312 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2401 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2402 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2403 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2404 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2405 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2406 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2407 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2408 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2409 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2410 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2411 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2412 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2501 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2502 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2503 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2504 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2505 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2506 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2507 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2508 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2509 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2510 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2511 : [np.nan, np.nan, np.nan, np.nan, np.nan],
    2512 : [np.nan, np.nan, np.nan, np.nan, np.nan]
}
emptyTable = pd.DataFrame(emptyTable).T
emptyTable.columns = ['10DP', '25DP', 'ATM', '25DC', '10DC']
now_time = datetime.now()
year = now_time.year
month = [
    'JAN',
    'FEB',
    'MAR',
    'APR',
    'MAY',
    'JUN',
    'JUL',
    'AUG',
    'SEP',
    'OCT',
    'NOV',
    'DEC'][now_time.month - 1]
filename_prefix = str(year) + month
       
def intDatetoDate(x):
    if type(x) == int:
        x = str(x)
    mon = int(x[2:])
    monDict = {1: "Jan", 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun',
                7: "Jul", 8:'Aug', 9:'Sep', 10: 'Oct', 11:'Nov', 12: 'Dec'}
    return monDict[mon] + x[:2]
    
def _translateToWords(shop, contract, price, iv, S, lots, cp):
    now_time = datetime.now()
    s = '[' + FinDate(now_time.day, now_time.month,now_time.year).datetime.strftime('%Y-%m-%d') + '] '
    s += shop +  ", "
    s += intDatetoDate(contract[0]) + ", " +str(contract[1]).upper()
    s += '\u00D7' + str(S)
    s += ', '
    s += str(price[0]) + '/' + str(price[1])
    s += ', '
    s += volTranswithNone(iv[0]) + '/' + volTranswithNone(iv[1])
    if lots != (None, None) and lots != (0, 0):
        s += ', in '
        s += str(lots[0]) + '/' + str(lots[1])
    if cp != (None, None):
        s += ", from " + str(cp[0]) + '/' + str(cp[1])
    
    return s

def _doneToWords(shop, contract, price, iv, S, lots, cp):
    now_time = datetime.now()
    s = '[' + FinDate(now_time.day, now_time.month,now_time.year).datetime.strftime('%Y-%m-%d') + '] Done: '
    s += shop +  ", "
    s += intDatetoDate(contract[0]) + ", " +str(contract[1]).upper()
    s += '\u00D7' + str(S)
    s += ', '
    s += str(price)
    s += ', '
    s += str(np.around(iv*100, 4)) + '%'
    if lots != None:
        s += ', in '
        s += str(lots) 
    if cp != None:
        s += ", from " + str(cp)
    
    return s

def writeTable(x):
        if np.isnan(x):
            return '    '
        else:
            return str((np.around(x*100, 2))) + '%'

def volTranswithNone(x, dig = 4):
    if x == None:
        return 'None'
    else:
        return str(np.around(x* 100, dig) ) + '%'

def deltaClassifier(delta):
    if delta > 0:
        if delta < 0.175:
            col = '10DC'
        elif delta < 0.375:
            col = '25DC'
        elif delta < 0.625:
            col = 'ATM'
        elif delta < 0.825:
            col = '25DP'
        else:
            col = '10DP'
    else:
        if delta < - 0.825:
            col = '10DC'
        elif delta < - 0.625:
            col = '25DC'
        elif delta < - 0.375:
            col = 'ATM'
        elif delta < - 0.175:
            col = '25DP'
        else:
            col = '10DP'
    return col


class volTables():
    
    def __init__(self):
        try:
            bestBidRel = pd.read_excel(filename_prefix + 'IV_recorder.xlsx', sheet_name="BidRel", index_col = 0)
        except: 
            bestBidRel = emptyTable.copy()
            
        try:
            bestBidAbs = pd.read_excel(filename_prefix + 'IV_recorder.xlsx', sheet_name="BidAbs", index_col = 0)
        except:
            bestBidAbs = emptyTable.copy()
            
        try:
            bestAskRel = pd.read_excel(filename_prefix + 'IV_recorder.xlsx', sheet_name="AskRel", index_col = 0)
        except:
            bestAskRel = emptyTable.copy()

        try:
            bestAskAbs = pd.read_excel(filename_prefix + 'IV_recorder.xlsx', sheet_name="AskAbs", index_col = 0)
        except:
            bestAskAbs = emptyTable.copy()
            
        try:
            traded = pd.read_excel(filename_prefix + 'IV_recorder.xlsx', sheet_name="Traded", index_col = 0)
        except:
            traded = emptyTable.copy()

        try:
            bestBidRelLocator = pd.read_excel(filename_prefix + 'IV_recorder.xlsx', sheet_name="BidRelLoc", index_col = 0)
        except:
            bestBidRelLocator = emptyTable.copy()

        try:
            bestBidAbsLocator = pd.read_excel(filename_prefix + 'IV_recorder.xlsx', sheet_name="BidAbsLoc", index_col = 0)
        except:
            bestBidAbsLocator = emptyTable.copy()
            
        try:
            bestAskRelLocator = pd.read_excel(filename_prefix + 'IV_recorder.xlsx', sheet_name="AskRelLoc", index_col = 0)
        except:
            bestAskRelLocator = emptyTable.copy()

        try:
            bestAskAbsLocator = pd.read_excel(filename_prefix + 'IV_recorder.xlsx', sheet_name="AskAbsLoc", index_col = 0)
        except:
            bestAskAbsLocator = emptyTable.copy()
            
        try:
            tradedLocator = pd.read_excel(filename_prefix + 'IV_recorder.xlsx', sheet_name="TradedLoc", index_col = 0)
        except:
            tradedLocator = emptyTable.copy()

        try:
            textRecorder = pd.read_excel(filename_prefix + 'IV_recorder.xlsx', sheet_name="Text", index_col = 0)
        except:
            textRecorder = pd.DataFrame(columns = ['Text'])
            textRecorder.index.name = 'ID'
            textRecorder
    
        self.bestBidAbs = bestBidAbs
        self.bestAskAbs = bestAskAbs
        self.bestBidRelative = bestBidRel
        self.bestAskRelative = bestAskRel
        self.traded = traded
        self.bestBidAbsLocator = bestBidAbsLocator
        self.bestAskAbsLocator = bestAskAbsLocator
        self.bestBidRelativeLocator = bestBidRelLocator
        self.bestAskRelativeLocator = bestAskRelLocator
        self.tradedLocator = tradedLocator
        
        self.textRecorder = textRecorder
        self.logTable = self.bestBidRelative.applymap(lambda x: str(x) + ' / ') + self.bestAskRelative.applymap(lambda x: str(x))
        
    def new(self, contract, S, price, SA = None, spread = None, country = 'SG', 
            shop = 'Unknown', lots = (None, None), cp = (None, None), ID = None):

        option = opt(contract, S, SA = SA, spread = spread, country=country)
        delta = option.delta()
        deltaClass = deltaClassifier(delta)
        if ID == None:
            ID = int(datetime.timestamp(datetime.now()))
        elif ID in self.textRecorder:
            print("ID occupied!")
            while ID in self.textRecorder.index:
                ID = input('Enter a new ID: ')
        fairVol = option.volmean

        if price[0] != None:
            impliedVolBid = option.impliedvol(price[0])
            relativeBidVol = impliedVolBid - fairVol
            impliedVolBid = np.around(impliedVolBid, 4)
            relativeBidVol = np.around(relativeBidVol, 4)
            if np.isnan(self.bestBidRelative.loc[contract[0], deltaClass]):
                self.bestBidRelative.loc[contract[0], deltaClass] = relativeBidVol
                self.bestBidAbs.loc[contract[0], deltaClass] = impliedVolBid
                self.bestBidAbsLocator.loc[contract[0], deltaClass] = ID
                self.bestBidRelativeLocator.loc[contract[0], deltaClass] = ID

            elif self.bestBidRelative.loc[contract[0], deltaClass] < relativeBidVol:
                self.bestBidRelative.loc[contract[0], deltaClass]  = relativeBidVol
                self.bestBidAbs.loc[contract[0], deltaClass] = impliedVolBid
                self.bestBidAbsLocator.loc[contract[0], deltaClass] = ID
                self.bestBidRelativeLocator.loc[contract[0], deltaClass] = ID
                    
        else:
            impliedVolBid = None
            relativeBidVol = None
        
        if price[1] != None:
            impliedVolAsk = option.impliedvol(price[1])
            relativeAskVol = impliedVolAsk - fairVol
            impliedVolAsk = np.around(impliedVolAsk, 4)
            relativeAskVol = np.around(relativeAskVol, 4)
            if np.isnan(self.bestAskRelative.loc[contract[0], deltaClass]):
                self.bestAskRelative.loc[contract[0], deltaClass] = relativeAskVol
                self.bestAskAbs.loc[contract[0], deltaClass] = impliedVolAsk
                self.bestAskAbsLocator.loc[contract[0], deltaClass] = ID
                self.bestAskRelativeLocator.loc[contract[0], deltaClass] = ID
                
            elif self.bestAskRelative.loc[contract[0], deltaClass] > relativeAskVol:
                self.bestAskRelative.loc[contract[0], deltaClass]  = relativeAskVol
                self.bestAskAbs.loc[contract[0], deltaClass] = impliedVolAsk
                self.bestAskAbsLocator.loc[contract[0], deltaClass] = ID
                self.bestAskRelativeLocator.loc[contract[0], deltaClass] = ID
            
        else:
            impliedVolAsk = None
            relativeAskVol = None
        
        self.logTable = self.bestBidRelative.applymap(writeTable) + ' / ' +self.bestAskRelative.applymap(writeTable)
        iv = (impliedVolBid, impliedVolAsk)
        words = _translateToWords(shop, contract, price, iv, S, lots, cp)
        
        print(self.logTable)
        print(words)

        self.textRecorder.at[ID, 'Text'] = words
        with pd.ExcelWriter(filename_prefix + 'IV_recorder.xlsx') as writer:
            self.bestBidRelative.to_excel(writer, sheet_name="BidRel")
            self.bestBidAbs.to_excel(writer, sheet_name="BidAbs")
            self.bestAskRelative.to_excel(writer, sheet_name="AskRel")
            self.bestAskAbs.to_excel(writer, sheet_name="AskAbs")
            self.traded.to_excel(writer, sheet_name="Traded")
            self.textRecorder.to_excel(writer, sheet_name="Text")
            self.bestBidAbsLocator.to_excel(writer, sheet_name="BidAbsLoc")
            self.bestAskAbsLocator.to_excel(writer, sheet_name="AskAbsLoc")
            self.bestBidRelativeLocator.to_excel(writer, sheet_name="BidRelLoc")
            self.bestAskRelativeLocator.to_excel(writer, sheet_name="AskRelLoc")
            self.tradedLocator.to_excel(writer, sheet_name="TradedLoc")
            
    def update(self, contract, deltaRange, volTuple):
        if volTuple[0] != None:
            self.bestBidRelative.at[contract, deltaRange] = volTuple[0]/100
            self.bestBidAbs.at[contract, deltaRange] = np.nan
            
        if volTuple[1] != None:
            self.bestAskRelative.at[contract, deltaRange] = volTuple[1]/100
            self.bestAskAbs.at[contract, deltaRange] = np.nan
            
        with pd.ExcelWriter(filename_prefix + 'IV_recorder.xlsx') as writer:
            self.bestBidRelative.to_excel(writer, sheet_name="BidRel")
            self.bestBidAbs.to_excel(writer, sheet_name="BidAbs")
            self.bestAskRelative.to_excel(writer, sheet_name="AskRel")
            self.bestAskAbs.to_excel(writer, sheet_name="AskAbs")
            self.traded.to_excel(writer, sheet_name="Traded")
            self.textRecorder.to_excel(writer, sheet_name="Text")
            self.bestBidAbsLocator.to_excel(writer, sheet_name="BidAbsLoc")
            self.bestAskAbsLocator.to_excel(writer, sheet_name="AskAbsLoc")
            self.bestBidRelativeLocator.to_excel(writer, sheet_name="BidRelLoc")
            self.bestAskRelativeLocator.to_excel(writer, sheet_name="AskRelLoc")
            self.tradedLocator.to_excel(writer, sheet_name="TradedLoc")
        self.logTable.at[contract, deltaRange] = writeTable(self.bestBidRelative.at[contract, deltaRange]) + ' / ' +  writeTable(self.bestAskRelative.at[contract, deltaRange])
        print(self.logTable) 

    def init(self, side = 'both'):
        if side.lower() == 'bid':
            self.bestBidRelative = self.bestBidRelative.applymap(lambda x: np.nan)
           
        elif side.lower() == 'ask':
            self.bestAskRelative = self.bestAskRelative.applymap(lambda x: np.nan)
            
        else:
            self.bestBidRelative = self.bestBidRelative.applymap(lambda x: np.nan)
            self.bestAskRelative = self.bestAskRelative.applymap(lambda x: np.nan)

        with pd.ExcelWriter(filename_prefix + 'IV_recorder.xlsx') as writer:
            self.bestBidRelative.to_excel(writer, sheet_name="BidRel")
            self.bestBidAbs.to_excel(writer, sheet_name="BidAbs")
            self.bestAskRelative.to_excel(writer, sheet_name="AskRel")
            self.bestAskAbs.to_excel(writer, sheet_name="AskAbs")
            self.traded.to_excel(writer, sheet_name="Traded")
            self.textRecorder.to_excel(writer, sheet_name="Text")
            self.bestBidAbsLocator.to_excel(writer, sheet_name="BidAbsLoc")
            self.bestAskAbsLocator.to_excel(writer, sheet_name="AskAbsLoc")
            self.bestBidRelativeLocator.to_excel(writer, sheet_name="BidRelLoc")
            self.bestAskRelativeLocator.to_excel(writer, sheet_name="AskRelLoc")
            self.tradedLocator.to_excel(writer, sheet_name="TradedLoc")
        self.logTable = self.bestBidRelative.applymap(writeTable) + ' / ' +self.bestAskRelative.applymap(writeTable)
        print('Done!')
    
    def trade(self, contract, S, price, SA = None, spread = None, country = 'SG', 
              shop = 'Unknown', lots = None, cp = None):
        
        option = opt(contract, S, SA = SA, spread = spread, country=country)
        if len(option.optionIdentity) != 1:
            raise FinError("Only Support Outright")
        delta = option.delta()
        deltaClass = deltaClassifier(delta)
        impliedVoTraded = option.impliedvol(price)
        impliedVoTraded = np.around(impliedVoTraded, 4)

        # if np.isnan(self.traded.loc[contract[0], deltaClass]):
        #     self.traded.loc[contract[0], deltaClass] = relativeVol
        # elif self.traded.loc[contract[0], deltaClass] < relativeVol:
        #     self.traded.loc[contract[0], deltaClass]  = relativeVol

        self.traded.loc[contract[0], deltaClass] = impliedVoTraded
        def _demon(x):
            if np.isnan(x):
                return '   /   '
            else:
                return str(np.around(x*100, 4)) + '%'
        demo = self.traded.applymap(_demon)
        print(demo)
        words = _doneToWords(shop, contract, price, impliedVoTraded, S, lots, cp)
        ID = int(datetime.timestamp(datetime.now()))
        self.tradedLocator.loc[contract[0], deltaClass] = ID
        print(words)
        self.textRecorder.at[ID, 'Text'] = words

        with pd.ExcelWriter(filename_prefix + 'IV_recorder.xlsx') as writer:
            self.bestBidRelative.to_excel(writer, sheet_name="BidRel")
            self.bestBidAbs.to_excel(writer, sheet_name="BidAbs")
            self.bestAskRelative.to_excel(writer, sheet_name="AskRel")
            self.bestAskAbs.to_excel(writer, sheet_name="AskAbs")
            self.traded.to_excel(writer, sheet_name="Traded")
            self.textRecorder.to_excel(writer, sheet_name="Text")
            self.bestBidAbsLocator.to_excel(writer, sheet_name="BidAbsLoc")
            self.bestAskAbsLocator.to_excel(writer, sheet_name="AskAbsLoc")
            self.bestBidRelativeLocator.to_excel(writer, sheet_name="BidRelLoc")
            self.bestAskRelativeLocator.to_excel(writer, sheet_name="AskRelLoc")
            self.tradedLocator.to_excel(writer, sheet_name="TradedLoc")
                

quote = volTables()
