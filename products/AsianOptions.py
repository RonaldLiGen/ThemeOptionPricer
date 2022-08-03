##############################################################################
###                        Asian Option Portfolio                          ###
##############################################################################

from enum import Enum

from ..finutils.FinDate import FinDate
from ..finutils.FinHelperFunctions import singleContractTimeSpecifier, labelToString
from ..finutils.FinHelperFunctions import contractAggregator, tenor_specifier, KandFlag_specifier, lot_specifier
from ..finutils.FinHelperFunctions import K_specifier, CP_specifier, Tenor_specifier
from ..finutils.FinHelperFunctions import interest_rate_dict
from ..finutils.SGXHelperFunctions import SGXexpireDate, time_specifier

from datetime import datetime
from ..finutils.FinError import FinError
from .FinAsianOption import FinAsianOption
from ..finutils.FinOptionTypes import FinOptionTypes
from ..models.FinModelBlackScholes import gbsValue
from ..finutils.FinGlobalVariables import gDaysInYear
from ..models.AsianVolCurve import delta_call
from ..models.AsianVolCurve import SGX_IV
from ..models.AsianVolCurve import getKeyVols


from scipy import optimize
from scipy.interpolate import CubicSpline
import numpy as np
from scipy.stats import norm

N = norm.cdf
CNDEV = norm.ppf



def TurnbullWakemanAsian(callPut, S, K, T, T2, sigma, r, b, SA):
    
    tau = T2 - T
    t1 = max(0, -tau)
    if b == 0:
        M1 = 0
        b_A = 0
        M2 = 2.0 * np.exp(sigma**2 * T) - 2.0 * np.exp(sigma**2 * t1) * (1.0 + sigma**2 * (T-t1))
        M2 = M2 / (sigma**4 * (T-t1)**2)

    else:
        M1 = (np.exp(b * T) - np.exp(b * t1)) / (b * (T-t1))
        M2 = 2*np.exp((2*b+sigma**2)*t1)/b/((T-t1)**2)
        M2 = M2 * ( 1/(2*b+sigma**2) - np.exp(b*(T-t1))/(b+sigma**2) )
        M2 += 2*np.exp( (2*b + sigma**2) * T) / (b + sigma**2) / (2*b + sigma**2) / ((T - t1)**2)
        b_A = np.log(M1)/T

    sigma_A = np.sqrt(np.log(M2)/T - 2*b_A)


    if tau > 0:  # we are in the averaging period
        if SA is None:
            raise FinError('errorStr')
        # we adjust the strike to account for the accrued coupon
        K = (K * T2 - SA * tau) / T
        if K < 0:
            if callPut == FinOptionTypes.EUROPEAN_CALL:
                return (SA*(T2-T)/T2 + S*T/T2) * np.exp(-r*T)
            else:
                return 0

    if tau > 0:
        if callPut == FinOptionTypes.EUROPEAN_CALL:
            v = gbsValue(S, T, K, r, b_A, sigma_A, 1) * (T / T2)
        else:
            v = gbsValue(S, T, K, r, b_A, sigma_A, -1) * (T / T2)
    else:
        if callPut == FinOptionTypes.EUROPEAN_CALL:
            v = gbsValue(S, T, K, r, b_A, sigma_A, 1)
        else:
            v = gbsValue(S, T, K, r, b_A, sigma_A, -1)

    return v

def AsianDelta(callPut, S, K, T, t2, v, r, b, SA):
    t1 = max(0, T-t2)
    tau = t2 - T

    if b == 0:
        M1 = 1
    else:
        M1 = (np.exp(b*T) - np.exp(b*t1))/(b*(T-t1))
    
    if tau >0:
        if t2 / T * K - tau / T * SA < 0:
            if callPut == FinOptionTypes.EUROPEAN_CALL:
                if SA > K:
                    return np.exp(-r * T) * M1 * T / t2
                else:
                    return 0
            else:
                return 0
    if b == 0:
        M2 = 2 * np.exp(v * v * T) / (v ** 4 * (T - t1) ** 2) - 2 * np.exp(v * v * t1) * (1 + v * v * (T - t1)) / (v ** 4 * (T - t1) ** 2)
    else:
        M2 = 2 * np.exp((2 * b + v * v) * T) / ((b + v * v) * (2 * b + v * v) * (T - t1) ** 2) + 2 * np.exp((2 * b + v * v) * t1) / (b * (T - t1) ** 2) * (1 / (2 * b + v * v) - np.exp(b * (T - t1)) / (b + v * v))
    bA = np.log(M1) / T
    vA = np.sqrt(np.log(M2) / T - 2 * bA)

    if tau > 0:
        K = t2 / T * K - tau / T * SA
        return GDelta(callPut, S, K, T, r, bA, vA) * T / t2
    else:
        return GDelta(callPut, S, K, T, r, bA, vA)

def GDelta(callPut, S, X, T, r, b, v):
    d1 = (np.log(S / X) + (b + v ** 2 / 2) * T) / (v * np.sqrt(T))
    if callPut == FinOptionTypes.EUROPEAN_CALL:
        return np.exp((b - r) * T) * N(d1)
    else:
        return -np.exp((b - r) * T) * N(-d1)

def getKfromDeltaAsian(callPut, S, deltas, T, t2, vols, r, b, SA):
    Ks = []
    for i in range(len(deltas)):
        delta = deltas[i]
        v = vols[i]
        
        t1 = max(0, T - t2)
        tau = t2 - T

        if b == 0:
            M1 = 1
        else:
            M1 = (np.exp(b * T) - np.exp(b * t1)) / (b * (T - t1))


        if b == 0:
            M2 = 2 * np.exp(v * v * T) / (v ** 4 * (T - t1) ** 2)  - 2 * np.exp(v * v * t1) * (1 + v * v * (T - t1)) / (v ** 4 * (T - t1) ** 2)
        else:
            M2 = 2 * np.exp((2 * b + v * v) * T) / ((b + v * v) * (2 * b + v * v) * (T - t1) ** 2) + 2 * np.exp((2 * b + v * v) * t1) / (b * (T - t1) ^ 2) * (1 / (2 * b + v * v) - np.exp(b * (T - t1)) / (b + v * v))

        bA = np.log(M1) / T
        vA = np.sqrt(np.log(M2) / T - 2 * bA)

        if tau > 0:
            K = GStrikeFromDelta(callPut, S, T, r, bA, vA, delta) * T / t2 + tau / t2 * SA
        else:
            K = GStrikeFromDelta(callPut, S, T, r, bA, vA, delta)
        Ks.append(K)
    return Ks

def GStrikeFromDelta(callPut, S, T, r, b, v, delta):
    # if callPut == FinOptionTypes.EUROPEAN_CALL:
    GStrikeFromDelta = S * np.exp(-CNDEV(delta * np.exp((r - b) * T)) * v * np.sqrt(T) + (b + v * v / 2) * T)
    # else:
        # GStrikeFromDelta = S * np.exp(CNDEV(-delta * np.exp((r - b) * T)) * v * np.sqrt(T) + (b + v * v / 2) * T)
    return GStrikeFromDelta

###############################################################################   

def KandFlag_specifier(contract):
    K = []
    for thisone in contract:
        K.append(thisone[1]) 
    return K

def tenor_specifier(contract):
    Tenor = []
    for thisone in contract:
        Tenor.append(thisone[0]) 
    return Tenor

def lot_specifier(contract):
    lots = []
    for thisone in contract:
        lots.append(thisone[2]) 
    return lots

def time_specifier(optionIdentity, country):
    yearMonth = []
    for thisone in optionIdentity: 
        yearMonth.append(singleContractTimeSpecifier(thisone[0]))
        
    startAveragingDates = {}
    expiry_dates = {}
    
    for i in range(len(yearMonth)):
        thisYM = yearMonth[i]
        startAveragingDate, expiryDate = SGXexpireDate(thisYM[0], thisYM[1], country)
        startAveragingDates[optionIdentity[i]] = startAveragingDate
        expiry_dates[optionIdentity[i]] = expiryDate

    return startAveragingDates, expiry_dates

# def K_specifier(optionIdentity):
#     K = {}
#     for thisone in optionIdentity:
#         K[thisone] = float(thisone[1][:-1])
#     return K

# def CP_specifier(optionIdentity):
#     CP = {}
#     for thisone in optionIdentity:
#         thisChar = thisone[1][-1]
#         if thisChar.upper() == 'C':
#             CP[thisone] = FinOptionTypes.EUROPEAN_CALL
#         else:
#             CP[thisone] = FinOptionTypes.EUROPEAN_PUT
#     return CP

# def Tenor_specifier(optionIdentity):
#     tenor = {}
#     for thisone in optionIdentity:
#         thisTenor = thisone[0]
#         tenor[thisone] = thisTenor
        
#     return tenor

interest_rate_dict = {None: 0.02, 'SG':0.02, 'CN': 0.05}

###############################################################################

class AsianOptionPortfolio():
    ###############################################################################
    def __init__(self, contract, S, valueDate = None, adjvol = 0.0, adjday = 0.0, 
    country = 'SG', SA = None, spread = None, fixedVol = None, volMapper = None):

        self.country = country
        if valueDate is None:
            now_time = datetime.now()
            self.valueDate = FinDate(now_time.day,now_time.month,now_time.year, now_time.hour, now_time.minute, self.country)
        else:
            self.valueDate =  valueDate
        
        if SA is None:
            SA = S
        self.SA = SA
        if adjvol > 1 or adjvol < -1:
            self.adjvol = adjvol/100
        self.adjday = adjday
        self.Smean = S
        contract = contractAggregator(contract)
        tenor = tenor_specifier(contract)
        KandFlag = KandFlag_specifier(contract)
        lots = lot_specifier(contract)
        optionIdentity = list(zip(tenor,KandFlag))
        option_lot_dict = {}
        for i in range(len(optionIdentity)):
            thisone = optionIdentity[i]
            if thisone in option_lot_dict:
                option_lot_dict[thisone] += lots[i]
            else:
                option_lot_dict[thisone] = lots[i]
        self.positionDict = option_lot_dict
        self.optionIdentity =  list(option_lot_dict.keys())
        self.noOfOptions = len(self.optionIdentity)

        self.startAveragingDate, self.expiryDate = time_specifier(self.optionIdentity, country)
        self.K = K_specifier(self.optionIdentity)
        self.callPut =  CP_specifier(self.optionIdentity)
        self.tenor = Tenor_specifier(self.optionIdentity)
        self.r = interest_rate_dict[country]
        self.option, self.optionDict = self.optionWriter()
        
        self.S = self.getS(S, spread)

        if fixedVol is not None:
            if fixedVol > 2:
                fixedVol = fixedVol/100
            self.vol = {}
            for thisid in self.optionIdentity:
                self.vol[thisid] = fixedVol
            self.volmean = fixedVol + self.adjvol
        elif volMapper is not None:
            self.vol, self.volmean = self.getVol(volMapper)
        else:
            self.vol, self.volmean = self.getVol()

    def optionWriter(self):
        options = []
        optionDict = {}
        for thisone in self.optionIdentity:
            K = self.K[thisone]
            callput = self.callPut[thisone]
            startAveragingDate = self.startAveragingDate[thisone]
            expiryDate = self.expiryDate[thisone]
            this_option = FinAsianOption(startAveragingDate, 
                                        expiryDate, 
                                        K, callput)
            options.append(this_option)
            optionDict[thisone] = this_option
        return options, optionDict

    def getS(self, S, spread):

        if spread is None:
            S_dict = {}
            for thisID in self.optionIdentity:
                S_dict[thisID] = S

        else:
            sum_of_Ss = S*(len(spread)+1) 
            for i in range(len(spread)):
                sum_of_Ss += spread[i] * (len(spread)-i)
            S0 = sum_of_Ss/(len(spread)+1) 
            Ss = [S0]
            for i in range(len(spread)):
                Ss.append(Ss[-1] - spread[i])  

            tenor = list(zip(*self.optionIdentity))[0]
            tenor = list(set(tenor))
            tenor.sort()

            tenor_S_dict = dict(zip(tenor, Ss))

            S_dict = {}

            for thisID in self.optionIdentity:
                thisTenor = thisID[0]
                S_dict[thisID] = tenor_S_dict[thisTenor]

        return S_dict
    
    def getVol(self, volMapper = None):
        if volMapper is not None:
            formattedMapper = {}
            transferNeeded = True
            if np.min(list(volMapper.values())) < 1:
                transferNeeded = False
            for thisOptionid in volMapper:
                thisVol = volMapper[thisOptionid]
                if len(thisOptionid) >= 3:
                    thisOptionid = thisOptionid[:2]
                if transferNeeded:
                    thisVol = thisVol / 100
                formattedMapper[thisOptionid] = thisVol
            

            for thisid in self.optionIdentity:
                if thisid not in formattedMapper:
                    S = self.S[thisid]
                    thisOption = self.optionDict[thisid]
                    thisT = thisOption.expiryDate - self.valueDate
                    thisT2 = thisOption.expiryDate - thisOption.startAveragingDate
                    thisT = thisT/gDaysInYear
                    thisT2 = thisT2/gDaysInYear
                    callPut = thisOption.optionType
                    keyDeltas = delta_call
                    keyVols = getKeyVols(thisT, SGX_IV)
                    keyKs = getKfromDeltaAsian(callPut, S, keyDeltas, thisT, thisT2, keyVols, self.r, 0, self.SA)
                    SK_vol_curve = CubicSpline(keyKs, keyVols, bc_type = 'natural')
                    vol = SK_vol_curve(thisOption.strikePrice)
                    formattedMapper[thisid] = vol

            return formattedMapper, np.mean(list(volMapper.values())) + self.adjvol
        else:
            vols = {}
            for thisid in self.optionIdentity:
                S = self.S[thisid]
                thisOption = self.optionDict[thisid]
                thisT = thisOption.expiryDate - self.valueDate
                thisT2 = thisOption.expiryDate - thisOption.startAveragingDate
                thisT = thisT/gDaysInYear
                thisT2 = thisT2/gDaysInYear
                callPut = thisOption.optionType
                keyDeltas = delta_call
                keyVols = getKeyVols(thisT, SGX_IV)
                keyKs = getKfromDeltaAsian(callPut, S, keyDeltas, thisT, thisT2, keyVols, self.r, 0, self.SA)
                SK_vol_curve = CubicSpline(keyKs, keyVols, bc_type = 'natural')
                vol = SK_vol_curve(thisOption.strikePrice)
                vols[thisid] = vol
            return vols, np.mean(list(vols.values())) + self.adjvol

    def value(self):
        vs = []
        for thisid in self.optionIdentity:
            S = self.S[thisid]
            vol = self.vol[thisid]            
            thisPremium = self.optionDict[thisid].value(self.valueDate, S, self.r,
                                                         0, vol, self.SA, self.adjday, adjvol = self.adjvol)
            thisPremium = self.positionDict[thisid] * thisPremium
            vs.append(thisPremium)
        v = np.array(vs).sum()
        return v

    def greeks(self):
        greeks = np.array([0] * 5)
        for thisid in self.optionIdentity:
            S = self.S[thisid]
            vol = self.vol[thisid]            
            thisPremium = self.optionDict[thisid].greeks(self.valueDate, S, self.r,
                                                        0, vol, self.SA,  adjDays = self.adjday, adjvol = self.adjvol)
            thisPremium = self.positionDict[thisid] * thisPremium
            greeks = greeks + np.array(thisPremium)
        return greeks

    def delta(self):
        vs = []
        for thisid in self.optionIdentity:
            S = self.S[thisid]
            vol = self.vol[thisid]            
            thisPremium = self.optionDict[thisid].delta(self.valueDate, S, self.r,
                                                        0, vol, self.SA, 
                                                        adjDays = self.adjday, adjvol = self.adjvol)
            thisPremium = self.positionDict[thisid] * thisPremium
            vs.append(thisPremium)
        v = np.array(vs).sum()
        return v

    def gamma(self):
        vs = []
        for thisid in self.optionIdentity:
            S = self.S[thisid]
            vol = self.vol[thisid]            
            thisPremium = self.optionDict[thisid].gamma(self.valueDate, S, self.r,
                                                        0, vol, self.SA, 
                                                        adjDays = self.adjday, adjvol = self.adjvol)
            thisPremium = self.positionDict[thisid] * thisPremium
            vs.append(thisPremium)
        v = np.array(vs).sum()
        return v
    
    def uppergamma(self):
        vs = []
        for thisid in self.optionIdentity:
            S = self.S[thisid]
            vol = self.vol[thisid]            
            thisPremium = self.optionDict[thisid].uppergamma(self.valueDate, S, self.r,
                                                                0, vol, self.SA, 
                                                                adjDays = self.adjday, adjvol = self.adjvol)
            thisPremium = self.positionDict[thisid] * thisPremium
            vs.append(thisPremium)
        v = np.array(vs).sum()
        return v

    def lowergamma(self):
        vs = []
        for thisid in self.optionIdentity:
            S = self.S[thisid]
            vol = self.vol[thisid]            
            thisPremium = self.optionDict[thisid].lowergamma(self.valueDate, S, self.r,
                                                                0, vol, self.SA, 
                                                                adjDays = self.adjday, adjvol = self.adjvol)
            thisPremium = self.positionDict[thisid] * thisPremium
            vs.append(thisPremium)
        v = np.array(vs).sum()
        return v
    
    def theta(self):
        vs = []
        for thisid in self.optionIdentity:
            S = self.S[thisid]
            vol = self.vol[thisid]            
            thisPremium = self.optionDict[thisid].theta(self.valueDate, S, self.r,
                                                        0, vol, self.SA, adjDays = self.adjday, 
                                                        adjvol = self.adjvol)
            thisPremium = self.positionDict[thisid] * thisPremium
            vs.append(thisPremium)
        v = np.array(vs).sum()
        return v

    def vega(self):
        vs = []
        for thisid in self.optionIdentity:
            S = self.S[thisid]
            vol = self.vol[thisid]            
            thisPremium = self.optionDict[thisid].vega(self.valueDate, S, self.r,
                                                        0, vol, self.SA, adjDays = self.adjday
                                                        , adjvol = self.adjvol)
            thisPremium = self.positionDict[thisid] * thisPremium
            vs.append(thisPremium)
        v = np.array(vs).sum()
        return v/100

    def rho(self):
        vs = []
        for thisid in self.optionIdentity:
            S = self.S[thisid]
            vol = self.vol[thisid]            
            thisPremium = self.optionDict[thisid].rho(self.valueDate, S, self.r,
                                                        0, vol,self.SA, 
                                                        adjDays = self.adjday, adjvol = self.adjvol)
            thisPremium = self.positionDict[thisid] * thisPremium
            vs.append(thisPremium)
        v = np.array(vs).sum()
        return v/100

    def __repr__(self):
        digs = 4
        s = '#' * 30 + '\n'
        
        s += labelToString("Premium", round(self.value(), 2), listFormat = True)
        s += labelToString("VOL",  round(self.volmean * 100, digs), listFormat = True)
        s += labelToString("DELTA", round(self.delta(), digs), listFormat = True)
        s += labelToString("GAMMA", round(self.gamma(), digs), listFormat = True)
        s += labelToString("UPPERGAMMA", round(self.uppergamma(), digs), listFormat = True)
        s += labelToString("LOWERGAMMA", round(self.lowergamma(), digs), listFormat = True)
        s += labelToString("THETA", round(self.theta(), digs), listFormat = True)
        s += labelToString("VEGA", round(self.vega(), digs), listFormat = True)
        s += labelToString("RHO", round(self.rho(), digs), listFormat = True)
        s += '#' * 30
        return s

    def impliedvol(self, price):
        
        if len(self.option) == 1:
            optionid = self.optionIdentity[0]
            S = self.S[optionid]
            return self.optionDict[optionid].impliedVolatility(self.valueDate, price, 0, S,self.r, 0,self.SA)
        else:
            raise FinError("Only Support Outright")

    def addOption(self, contract, S, vol = None, adjvol = 0.0, adjday = 0.0, 
                SA = None, spread = None):
        if SA is not None:
            self.SA = SA 
        if adjvol > 1 or adjvol < -1:
            self.adjvol = adjvol
        self.adjday = adjday
        NewContract = contractAggregator(contract)
        tenor = tenor_specifier(NewContract)
        KandFlag = KandFlag_specifier(NewContract)
        lots = lot_specifier(NewContract)
        optionIdentity = list(zip(tenor,KandFlag))
        option_lot_dict = self.positionDict
        for i in range(len(optionIdentity)):
            thisone = optionIdentity[i]
            if thisone in option_lot_dict:
                option_lot_dict[thisone] = option_lot_dict[thisone] + lots[i]
            else:
                option_lot_dict[thisone] = lots[i]
        self.positionDict = option_lot_dict
        self.optionIdentity =  list(option_lot_dict.keys())
        self.noOfOptions = len(self.optionIdentity)
        self.startAveragingDate, self.expiryDate = time_specifier(self.optionIdentity, self.country)
        self.K = K_specifier(self.optionIdentity)
        self.callPut =  CP_specifier(self.optionIdentity)
        self.tenor = Tenor_specifier(self.optionIdentity)
        self.option, self.optionDict = self.optionWriter()
        if spread is None:
            pass
        elif len(spread) + 1:
            pass
        else:
            self._updateS(S, spread, optionIdentity)
        if vol is None:
            self.vol, self.volmean = self.getVol()
        else:
            for i in range(len(optionIdentity)):
                thisone = optionIdentity[i]
                if thisone in option_lot_dict:
                    option_lot_dict[thisone] = option_lot_dict[thisone] + lots[i]
                else:
                    option_lot_dict[thisone] = lots[i]




    
    def _updateS(self, S, spread, optionIdentity):

        if spread is None:
            for thisone in optionIdentity:
                self.S[thisone] = S
            
            Smapper = {}
            for thisID in self.optionIdentity:
                thisTenor = thisID[0]
                Smapper[thisTenor] = self.S[thisID]
            self.Smean = np.mean(list(Smapper.values()))
                
        else:
            self.Smean = S
            sum_of_Ss = S*(len(spread)+1) 
            for i in range(len(spread)):
                sum_of_Ss += spread[i] * (len(spread)-i)
            S0 = sum_of_Ss/(len(spread)+1) 
            Ss = [S0]
            for i in range(len(spread)):
                Ss.append(Ss[-1] - spread[i])  

            tenor = list(zip(*optionIdentity))[0]
            tenor = list(set(tenor))
            tenor.sort()

            tenor_S_dict = dict(zip(tenor, Ss))
            allTenors = list(zip(*optionIdentity))[0]
            allTenors = list(set(allTenors))

            if len(tenor) == len(allTenors):
                for thisID in self.optionIdentity:
                    thisTenor = thisID[0]
                    self.S[thisID] = tenor_S_dict[thisTenor]
            else:
                for thisID in optionIdentity:
                    thisTenor = thisID[0]
                    self.S[thisID] = tenor_S_dict[thisTenor]

   
    def updateS(self, S = None, spread = None, dS = None):
        
        if S is None and dS is None and spread is None:
            print ('No Update on S')
        
        elif dS is not None:
            for thisid in self.S:
                self.S[thisid] = self.S[thisid] + dS
            self.Smean -= dS
        
        elif spread is None:
            tenor_S_dict = {}
            dS = S - self.Smean
            for thisid in self.S:
                self.S[thisid] =  self.S[thisid] + dS
            self.Smean = S
        
        else:
            if S is None:
                tenor_S_dict = {}
                for thisID in self.optionIdentity:
                    thisTenor = thisID[0]
                    tenor_S_dict[thisTenor] = self.S[thisID]
                S = np.mean(list(tenor_S_dict.values()))
            self.Smean = S
            sum_of_Ss = S*(len(spread)+1) 
            for i in range(len(spread)):
                sum_of_Ss += spread[i] * (len(spread)-i)
            S0 = sum_of_Ss/(len(spread)+1) 
            Ss = [S0]
            for i in range(len(spread)):
                Ss.append(Ss[-1] - spread[i])  

            tenor = list(zip(*self.optionIdentity))[0]
            tenor = list(set(tenor))
            tenor.sort()
            tenor_S_dict = dict(zip(tenor, Ss))

            for thisID in self.optionIdentity:
                thisTenor = thisID[0]
                self.S[thisID] = tenor_S_dict[thisTenor]

        self.vol, self.volmean = self.getVol()

    def updateVol(self, adjvol):
        self.adjvol = adjvol / 100
        self.vol, self.volmean = self.getVol()


opt = AsianOptionPortfolio