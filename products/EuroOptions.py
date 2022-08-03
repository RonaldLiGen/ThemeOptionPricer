##############################################################################
###                        Euro Option Portfolio                           ###
##############################################################################

from enum import Enum

from ..finutils.FinDate import FinDate, cnday
from ..finutils.FinHelperFunctions import singleContractTimeSpecifier, labelToString
from ..finutils.FinHelperFunctions import contractAggregator, tenor_specifier, KandFlag_specifier, lot_specifier
from ..finutils.FinHelperFunctions import K_specifier, CP_specifier,Tenor_specifier
from ..finutils.FinHelperFunctions import interest_rate_dict
from ..finutils.DCEHelperFunctions import DCEexpireDate, time_specifier

from datetime import datetime
from ..finutils.FinError import FinError
from .FinVanillaOption import FinFutureVanillaOption
from ..finutils.FinOptionTypes import FinOptionTypes
from ..models.FinModelBlackScholes import gbsValue
from ..finutils.FinGlobalVariables import gDaysInYear
from ..models.EuroVolCurve import delta_call
from ..models.EuroVolCurve import getKeyVols
from ..models.EuroVolCurve import DCE_IV


from scipy import optimize
from scipy.interpolate import CubicSpline
import numpy as np
from scipy.stats import norm

N = norm.cdf
CNDEV = norm.ppf

def getKfromDeltaEuro(callPut, S, deltas, T, vols, r, b):
    Ks = []
    for i in range(len(deltas)):
        delta = deltas[i]
        v = vols[i]
        K = GStrikeFromDelta(callPut, S, T, r, b, v, delta)
        Ks.append(K)
    return Ks

def GStrikeFromDelta(callPut, S, T, r, b, v, delta):
    # if callPut == FinOptionTypes.EUROPEAN_CALL:
    GStrikeFromDelta = S * np.exp(-CNDEV(delta * np.exp((r - b) * T)) * v * np.sqrt(T) + (b + v * v / 2) * T)
    # else:
        # GStrikeFromDelta = S * np.exp(CNDEV(-delta * np.exp((r - b) * T)) * v * np.sqrt(T) + (b + v * v / 2) * T)
    return GStrikeFromDelta

class EuroFutureOptionPortfolio():
    def __init__(self, contract, S, valueDate = None, adjvol = 0.0, adjday = 0.0, 
    country = 'CN', spread = None, fixedVol = None, volMapper = None):

        self.country = country
        if valueDate is None:
            now_time = datetime.now()
            self.valueDate = FinDate(now_time.day,now_time.month,now_time.year, now_time.hour, now_time.minute, self.country)
        else:
            self.valueDate = valueDate
        
        self.adjvol = adjvol / 100
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

        self.expiryDate = time_specifier(self.optionIdentity, country)
        self.K = K_specifier(self.optionIdentity)
        self.callPut =  CP_specifier(self.optionIdentity)
        self.tenor = Tenor_specifier(self.optionIdentity)
        self.r = interest_rate_dict[country]
        self.option, self.optionDict = self.optionWriter()
        
        self.S = self.getS(S, spread)
        
        if fixedVol is not None:
            fixedVol = fixedVol/100
            self.vol = {}
            for thisid in self.optionIdentity:
                self.vol[thisid] = fixedVol + self.adjvol
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
            expiryDate = self.expiryDate[thisone]
            this_option = FinFutureVanillaOption(expiryDate, 
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
                    thisT = thisT/gDaysInYear
                    callPut = thisOption.optionType
                    keyDeltas = delta_call
                    keyVols = getKeyVols(thisT, DCE_IV)
                    keyKs = getKfromDeltaEuro(callPut, S, keyDeltas, thisT, keyVols, self.r, 0)
                    SK_vol_curve = CubicSpline(keyKs, keyVols, bc_type = 'natural')
                    vol = SK_vol_curve(thisOption.strikePrice) + self.adjvol
                    formattedMapper[thisid] = vol
            return formattedMapper, np.mean(list(volMapper.values()))

        else:
            vols = {}
            for thisid in self.optionIdentity:
                S = self.S[thisid]
                thisOption = self.optionDict[thisid]
                thisT = thisOption.expiryDate - self.valueDate
                thisT = thisT/gDaysInYear
                callPut = thisOption.optionType
                keyDeltas = delta_call
                keyVols = getKeyVols(thisT, DCE_IV)
                keyKs = getKfromDeltaEuro(callPut, S, keyDeltas, thisT, keyVols, self.r, 0)
                # print(keyKs)
                SK_vol_curve = CubicSpline(keyKs, keyVols, bc_type = 'natural')
                vol = SK_vol_curve(thisOption.strikePrice) + self.adjvol
                vols[thisid] = vol
            return vols, np.mean(list(vols.values()))

    def value(self):
        vs = []
        for thisid in self.optionIdentity:
            S = self.S[thisid]
            vol = self.vol[thisid]            
            thisPremium = self.optionDict[thisid].value(self.valueDate, S, self.r, 
                                                        vol, self.adjday)
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
                                                         vol, adjDays = self.adjday)
            thisPremium = self.positionDict[thisid] * thisPremium
            greeks = greeks + np.array(thisPremium)
        return greeks

    def delta(self):
        vs = []
        for thisid in self.optionIdentity:
            S = self.S[thisid]
            vol = self.vol[thisid]            
            thisPremium = self.optionDict[thisid].delta(self.valueDate, S, self.r,
                                                        vol, adjDays = self.adjday)
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
                                                        vol, adjDays = self.adjday)
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
                                                        vol, adjDays = self.adjday)
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
                                                        vol, adjDays = self.adjday)
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
                                                        vol, adjDays = self.adjday)
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
                                                        vol, adjDays = self.adjday)
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
                                                        vol,adjDays = self.adjday)
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
            return self.optionDict[optionid].impliedVol(self.valueDate, S, self.r, price, self.adjday)
        else:
            raise FinError("Only Support Outright")

    def addOption(self, contract, S, adjvol = 0.0, adjday = 0.0, spread = None):
        
        self.adjvol = adjvol
        self.adjday = adjday
        contract = contractAggregator(contract)
        tenor = tenor_specifier(contract)
        KandFlag = KandFlag_specifier(contract)
        lots = lot_specifier(contract)
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
        self.expiryDate = time_specifier(self.optionIdentity, self.country)
        self.K = K_specifier(self.optionIdentity)
        self.callPut =  CP_specifier(self.optionIdentity)
        self.tenor = Tenor_specifier(self.optionIdentity)
        self.option, self.optionDict = self.optionWriter()
        self._updateS(S, spread, optionIdentity)
        self.vol, self.volmean = self.getVol()
    
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

            for thisID in self.optionIdentity:
                thisTenor = thisID[0]
                self.S[thisID] = tenor_S_dict[thisTenor]

        self.vol, self.volmean = self.getVol()
   
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

euopt = EuroFutureOptionPortfolio