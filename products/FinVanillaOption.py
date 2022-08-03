##############################################################################
###                          Euro Option Pricer                            ###
##############################################################################

import numpy as np

from scipy import optimize

from ..finutils.FinDate import FinDate
from ..finutils.FinMath import nprime
from ..finutils.FinGlobalVariables import gDaysInYear
from ..finutils.FinError import FinError
from ..models.FinModelBlackScholes import bsValue
from ..finutils.FinOptionTypes import FinOptionTypes
from ..finutils.FinHelperFunctions import labelToString

from scipy.stats import norm
N = norm.cdf

###############################################################################


###############################################################################

class FinFutureVanillaOption():
    ''' Class for managing plain vanilla European calls and puts on equities.
    For American calls and puts see the FinEquityAmericanOption class. '''

    def __init__(self,
                 expiryDate: FinDate,
                 strikePrice: (float, np.ndarray),
                 optionType: FinOptionTypes):
        ''' Create the Equity Vanilla option object by specifying the expiry
        date, the option strike, the option type and the number of options. '''

        if optionType != FinOptionTypes.EUROPEAN_CALL and \
           optionType != FinOptionTypes.EUROPEAN_PUT:
            raise FinError("Unknown Option Type" + str(optionType))

        self.expiryDate = expiryDate
        self.strikePrice = strikePrice
        self.optionType = optionType

    ###############################################################################
    def __repr__(self):
        s = labelToString("EXPIRY DATE", str(self.expiryDate))
        s += labelToString("STRIKE PRICE", self.strikePrice)
        s += labelToString("OPTION TYPE", self.optionType)
        return s
    
    def value(self,
              valueDate: FinDate,
              futurePrice: (np.ndarray, float),
              r: float,
              vol: float,
              adjDays: float =  0):
        ''' Option valuation using Black-Scholes model. '''

        if type(valueDate) == FinDate:
           texp = (self.expiryDate - valueDate - adjDays) / gDaysInYear
        else:
            texp = valueDate - adjDays

        if self.optionType == FinOptionTypes.FUTURES:
            return futurePrice

        if np.any(texp < 0.0):
            raise FinError("Time to expiry must be positive.")

        texp = np.maximum(texp , 1e-10)
        F = futurePrice
        K = self.strikePrice
        v = vol

        if np.any(v) < 0.0: 
            raise FinError("Volatility should not be negative.")
        d1 = np.log(F/K) + v**2*texp/2
        d1 = d1 / v/np.sqrt(texp)
        d2 = d1 - v * np.sqrt(texp)
        # print(r, texp, F, K, d1, d2)
        if self.optionType == FinOptionTypes.EUROPEAN_CALL:
            v_opt = np.exp(-r*texp)*(F*N(d1)-K*N(d2))
        elif self.optionType == FinOptionTypes.EUROPEAN_PUT:
            v_opt = np.exp(-r*texp)*(K*N(-d2)-F*N(-d1))
        else:
            raise FinError("Unknown option type")
        
        v = v_opt
        
        return v

    def impliedVol(self,
                    valueDate,
                    futurePrice: (float, list, np.ndarray),
                    r: float,
                    price, 
                    adjDays = 0):
        ''' Calculate the implied volatility of a European vanilla option. '''
        def _f_future(volatility, *args): # get implied vol: argmin BSPrice(vol) - Price => vol                                      

            self = args[0]
            valueDate = args[1]
            futurePrice = args[2]
            r = args[3]
            price = args[4]
            adjDays = args[5]
            objFn = self.value(valueDate,
                            futurePrice,
                            r,
                            volatility,
                            adjDays = adjDays)

            objFn = objFn - price

            return objFn

        def _fvega_future(volatility, *args):

            self = args[0]
            valueDate = args[1]
            futurePrice = args[2]
            r = args[3]
            price = args[4]
            adjDays = args[5]

            fprime = self.vega(valueDate,futurePrice,
                                r, volatility, adjDays = adjDays)
            return fprime

        argtuple = (self, valueDate, futurePrice, r, price, adjDays)

        sigma = optimize.newton(_f_future, x0=0.9, args=argtuple,
                                tol=1e-5, maxiter=100, fprime=_fvega_future)
        return sigma

    ###############################################################################

    def __repr__(self):
        s = labelToString("EXPIRY DATE", str(self.expiryDate))
        s += labelToString("STRIKE PRICE", self.strikePrice)
        s += labelToString("OPTION TYPE", self.optionType)
        return s

    ###############################################################################

    def _print(self):
        ''' Simple print function for backward compatibility. '''
        print(self)

    ###############################################################################

    def delta(self,
              valueDate:FinDate,
              futurePrice: float,
              r: float,
              vol:float,
              adjDays = 0):
        ''' Calculate the analytical delta of a European vanilla option. '''

        F_pos = futurePrice + 0.01
        F_neg = futurePrice - 0.01
        
        v_pos = self.value(valueDate, F_pos, r, vol, adjDays=adjDays)
        v_neg = self.value(valueDate, F_neg, r, vol, adjDays=adjDays)

        delta = (v_pos - v_neg)/ (0.02)
        
        return delta
            

    # ###############################################################################

    def gamma(self,
              valueDate: FinDate,
              futurePrice: float,
              r: float,
              vol:float,
              adjDays = 0):
        ''' Calculate the analytical gamma of a European vanilla option. '''

        F_pos = futurePrice + 0.01
        F_neg = futurePrice - 0.01
        
        v_pos = self.value(valueDate, F_pos, r, vol, adjDays = adjDays)
        v_neg = self.value(valueDate, F_neg, r, vol, adjDays = adjDays)
        v = self.value(valueDate, futurePrice, r, vol, adjDays=adjDays)

        v = (v_pos + v_neg - 2*v) / (0.01**2)
        
        return v

    def uppergamma(self,
              valueDate: FinDate,
              futurePrice: float,
              r: float,
              vol:float,
              adjDays = 0):
        ''' Calculate the analytical gamma of a European vanilla option. '''

        F_pos = futurePrice + 0.01
        
        v_pos = self.delta(valueDate, F_pos, r, vol, adjDays = adjDays)
        v = self.delta(valueDate, futurePrice, r, vol, adjDays=adjDays)

        v = (v_pos - v) / (0.01)
        
        return v

    def lowergamma(self,
              valueDate: FinDate,
              futurePrice: float,
              r: float,
              vol:float,
              adjDays = 0):
        ''' Calculate the analytical gamma of a European vanilla option. '''

        
        F_neg = futurePrice - 0.01
        v_neg = self.delta(valueDate, F_neg, r, vol, adjDays = adjDays)
        v = self.delta(valueDate, futurePrice, r, vol, adjDays=adjDays)

        v = (v - v_neg) / (0.01)
        
        return v


    # ###############################################################################

    def vega(self,
             valueDate: FinDate,
             futurePrice: float,
             r: float,
             vol: float,
             adjDays = 0):
        ''' Calculate the analytical vega of a European vanilla option. '''
        v_pos = vol + 0.0001
        v_neg = vol - 0.0001
        
        v_pos = self.value(valueDate, futurePrice, r, v_pos, adjDays=adjDays)
        v_neg = self.value(valueDate, futurePrice, r, v_neg, adjDays=adjDays)

        vega = (v_pos - v_neg)/ (0.0002)
        return vega

    # ###############################################################################

    def theta(self,
              valueDate: FinDate,
              futurePrice: float,
              r: float,
              vol: float,
              adjDays = 0 ):
        ''' Calculate the analytical theta of a European vanilla option. '''
        
        total_days = gDaysInYear
        
        v_pos = self.value(valueDate, futurePrice, r, vol, adjDays=adjDays+0.0001)
        v_neg = self.value(valueDate, futurePrice, r, vol, adjDays=adjDays-0.0001)
        v = (v_pos - v_neg)/ (0.0002/ total_days)/ total_days

        return v

    # ###############################################################################

    def rho(self,
            valueDate: FinDate,
            futurePrice: float,
            r: float,
            vol: float,
            adjDays = 0):
        ''' Calculate the analytical rho of a European vanilla option. '''

        r_pos = r + 0.0001
        r_neg = r - 0.0001
        
        v_pos = self.value(valueDate, futurePrice, r_pos, vol, adjDays=adjDays)
        v_neg = self.value(valueDate, futurePrice, r_neg, vol, adjDays=adjDays)

        v = (v_pos - v_neg)/ (0.0002)
        return v
    # ###############################################################################
    def greeks(self,
               valueDate: FinDate,
                futurePrice: float,
                r: float,
                vol: float,
                adjDays = 0):
        # print(valueDate)
        delta = self.delta(valueDate, futurePrice, r, vol, adjDays)
        gamma = self.gamma(valueDate, futurePrice, r, vol, adjDays)
        theta = self.theta(valueDate, futurePrice, r, vol, adjDays)
        vega = self.vega(valueDate, futurePrice, r, vol, adjDays)
        rho = self.rho(valueDate, futurePrice, r, vol, adjDays)

        return np.array([delta, gamma, theta, vega/100, rho/100])