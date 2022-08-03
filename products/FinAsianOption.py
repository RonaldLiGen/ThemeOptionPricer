##############################################################################
###                          Asian Option Pricer                           ###
##############################################################################

import numpy as np
from numba import njit
from scipy import optimize

from ..finutils.FinMath import N
from ..finutils.FinGlobalVariables import gDaysInYear
from ..finutils.FinError import FinError
from ..finutils.FinOptionTypes import FinOptionTypes
from ..finutils.FinDate import FinDate
from scipy import optimize
from ..models.FinModelBlackScholes import gbsValue
from ..finutils.FinHelperFunctions import labelToString
import math

###############################################################################

from enum import Enum

###############################################################################

errorStr = "In averaging period, need to enter accrued average."

###############################################################################

class FinAsianOption():
    ''' Class for an Equity Asian Option. This is an option with a final payoff
    linked to the averaging of the stock price over some specified period
    before the option expires. The valuation is done for both an arithmetic and
    a geometric average but the former can only be done either using an
    analytical approximation of the arithmetic average distribution or by using
    Monte-Carlo simulation.'''

    ###############################################################################

    def __init__(self,
                 startAveragingDate: FinDate,
                 expiryDate: FinDate,
                 strikePrice: float,
                 optionType: FinOptionTypes):
        ''' Create an FinEquityAsian option object which takes a start date for
        the averaging, an expiry date, a strike price, an option type and a
        number of observations. '''

        if startAveragingDate > expiryDate:
            raise FinError("Averaging starts after expiry date")

        self.startAveragingDate = startAveragingDate
        self.expiryDate = expiryDate
        self.strikePrice = float(strikePrice)
        self.optionType = optionType
        self.numObservations = math.ceil(expiryDate - startAveragingDate) + 1
        self.country = startAveragingDate.country
    ###############################################################################


    def value(self,
              valueDate: FinDate,
              stockPrice: float,
              r: float,
              costOfCarry: float,
              vol: float,
              SA: float = None,
              adjDays: float = 0,
              ):
            #   method: FinAsianOptionValuationMethods = FinAsianOptionValuationMethods.TURNBULL_WAKEMAN):
        ''' Calculate the value of an Asian option using one of the specified
        analytical approximations for an average rate option. These are the
        three enumerated values in the enum FinAsianOptionValuationMethods. The
        choices of approximation are (i) GEOMETRIC - the average is a geometric
        one as in paper by Kenna and Worst (1990), (ii) TURNBULL_WAKEMAN -
        this is a value based on an edgeworth expansion of the moments of the
        arithmetic average, and (iii) CURRAN - another approximative approach
        by Curran based on conditioning on the geometric mean price. Just
        choose the corresponding enumerated value to switch between these
        different approaches.

        Note that the accrued average is only required if the value date is
        inside the averaging period for the option. '''

       
        # if method == FinAsianOptionValuationMethods.TURNBULL_WAKEMAN:

        if self.optionType == FinOptionTypes.FUTURES:
            return stockPrice

        v = self._valueTurnbullWakeman(valueDate,
                                        adjDays,
                                        stockPrice,
                                        r,
                                        costOfCarry,
                                        vol,
                                        SA)


        return v

    ###############################################################################
    
    def _valueTurnbullWakeman(self, valueDate, adjDays, S, r,
                              b, vol, SA):
        ''' Asian option valuation based on paper by Turnbull and Wakeman 1991
        which uses the edgeworth expansion to find the first two moments of the
        arithmetic average. '''


        total_days = gDaysInYear
        adjYears = adjDays/total_days

        TinDays = (self.expiryDate - valueDate)
        T2inDays = (self.expiryDate - self.startAveragingDate)

        T2 = T2inDays/total_days
        T =  TinDays/total_days - adjYears
        K = self.strikePrice

        tau = T2 - T
        t1 = max(0, -tau)
        K = self.strikePrice
        
        # b = costOfCarry
        # Note: because of the vol interpolation, the dividend here is fixed, which may not be the actual case
        
        b=0
        sigma = vol
   
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
            print(M2, "but b is no longer 0")
            b_A = np.log(M1)/T

        sigma_A = np.sqrt(np.log(M2)/T - 2*b_A)
        
        if tau > 0:  # we are in the averaging period
            if SA is None:
                raise FinError(errorStr)
            # we adjust the strike to account for the accrued coupon
            K = (K * T2 - SA * tau) / T
            if K < 0:
                if self.optionType == FinOptionTypes.EUROPEAN_CALL:
                    return (SA*(T2-T)/T2 + S*T/T2 - self.strikePrice) * np.exp(-r*T)
                else:
                    return 0

        if tau > 0:
            if self.optionType == FinOptionTypes.EUROPEAN_CALL:
                v = gbsValue(S, T, K, r, b_A, sigma_A, 1) * (T / T2)
            else:
                v = gbsValue(S, T, K, r, b_A, sigma_A, -1) * (T / T2)
        else:
            if self.optionType == FinOptionTypes.EUROPEAN_CALL:
                v = gbsValue(S, T, K, r, b_A, sigma_A, 1)
            else:
                v = gbsValue(S, T, K, r, b_A, sigma_A, -1)
        

        return v

    ###############################################################################
    def impliedVolatility(self,
                          valueDate,
                          price: float,
                          adjDays: float,
                          stockPrice: float,
                          r: float,
                          costOfCarry: float,
                          SA: float = None):
                          
        ''' Calculate the implied volatility of a European vanilla option. '''

        def _f(volatility):
            objFn = self.value(valueDate,
                                stockPrice,
                                r,
                                costOfCarry,
                                volatility,
                                SA,
                                adjDays = adjDays
                                )
            # print( objFn - price)
            return objFn - price

        def _fprime(volatility):
            
            objFn = self.vega(valueDate,
                                stockPrice,
                                r,
                                costOfCarry,
                                volatility,
                                SA,
                                adjDays = adjDays)

            return objFn
        
        sigma = optimize.newton(_f, x0=0.7, fprime=_fprime, tol=1e-8, maxiter=10000)
        
        return sigma

    ###############################################################################

    def __repr__(self):
        
        s = labelToString("OBJECT TYPE", type(self).__name__)
        s += labelToString("START", str(self.startAveragingDate))
        s += labelToString("EXPIRY", str(self.expiryDate))
        s += labelToString("STRIKE", self.strikePrice)
            # s += labelToString("OPTION TYPE", self.optionType)
        
    
        return s

    ###############################################################################

    # def _print(self):
    #     ''' Simple print function for backward compatibility. '''
    #     print(self)

    ###############################################################################

    def delta(self,
              valueDate,
              stockPrice: float,
              r: float,
              costOfCarry: float,
              vol: float,
              SA: float = None,
              adjDays = 0):
        ''' Calculate the approximated delta of an Asian option. '''

        v_neg = self._valueTurnbullWakeman(valueDate,
                                            adjDays,
                                            stockPrice - 0.005,
                                            r,
                                            costOfCarry,
                                            vol,
                                            SA)

        v_pos = self._valueTurnbullWakeman(valueDate,
                                            adjDays,
                                            stockPrice + 0.005,
                                            r,
                                            costOfCarry,
                                            vol,
                                            SA)
        # print(v_pos, v_neg)
        v = (v_pos - v_neg) / 0.01

        return v

    ###############################################################################

    def gamma(self,
              valueDate,
              stockPrice: float,
              r: float,
              costOfCarry: float,
              vol: float,
              SA: float = None,
              adjDays = 0):
        ''' Calculate the approximated gamma of an Asian option. '''
        
        v_neg = self._valueTurnbullWakeman(valueDate,
                                            adjDays,
                                            stockPrice - 0.005,
                                            r,
                                            costOfCarry,
                                            vol,
                                            SA)

        v_pos = self._valueTurnbullWakeman(valueDate,
                                            adjDays,
                                            stockPrice + 0.005,
                                            r,
                                            costOfCarry,
                                            vol,
                                            SA)

                                    
        v = self._valueTurnbullWakeman(valueDate,
                                            adjDays,
                                            stockPrice,
                                            r,
                                            costOfCarry,
                                            vol,
                                            SA)

        v = (v_pos + v_neg - 2*v) / (0.005**2)

        return v
    

    def uppergamma(self,
              valueDate,
              stockPrice: float,
              r: float,
              costOfCarry: float,
              vol: float,
              SA: float = None,
              adjDays = 0):
        ''' Calculate the approximated gamma of an Asian option. '''
        

        v_pos = self.delta(valueDate,
                            stockPrice+0.005,
                            r,
                            costOfCarry,
                            vol,
                            SA,
                            adjDays)

                                    
        v = self.delta(valueDate,
                        stockPrice,
                        r,
                        costOfCarry,
                        vol,
                        SA,
                        adjDays)

        v = (v_pos - v) / 0.005

        return v
    
    def lowergamma(self,
              valueDate,
              stockPrice: float,
              r: float,
              costOfCarry: float,
              vol: float,
              SA: float = None,
              adjDays = 0):
        ''' Calculate the approximated gamma of an Asian option. '''
        
        v_neg = self.delta(valueDate,
                            stockPrice-0.005,
                            r,
                            costOfCarry,
                            vol,
                            SA,
                            adjDays)

        
                                    
        v = self.delta(valueDate,
                        stockPrice,
                        r,
                        costOfCarry,
                        vol,
                        SA,
                        adjDays)

        v = (v - v_neg) / 0.005

        return v
    
    ################################################################################

    def vega(self,
              valueDate,
              stockPrice: float,
              r: float,
              costOfCarry: float,
              vol: float,
              SA: float = None,
              adjDays = 0):
        ''' Calculate the approximated vega of an Asian option. '''


        vol_pos = vol + 0.00005
        vol_neg = vol - 0.00005

        v_neg = self._valueTurnbullWakeman(valueDate,
                                            adjDays,
                                            stockPrice,
                                            r,
                                            costOfCarry,
                                            vol_neg,
                                            SA)

        v_pos = self._valueTurnbullWakeman(valueDate,
                                            adjDays,
                                            stockPrice,
                                            r,
                                            costOfCarry,
                                            vol_pos,
                                            SA)

        v = (v_pos - v_neg) / 0.0001

        return v

    ################################################################################

    def theta(self,
              valueDate,
              stockPrice: float,
              r: float,
              costOfCarry: float,
              vol: float,
              SA: float = None,
              adjDays = 0):
        ''' Calculate the approximated theta of an Asian option. '''
        
        v_neg = self._valueTurnbullWakeman(valueDate,
                                            adjDays - 0.005,
                                            stockPrice,
                                            r,
                                            costOfCarry,
                                            vol,
                                            SA)

        v_pos = self._valueTurnbullWakeman(valueDate,
                                            adjDays + 0.005,
                                            stockPrice,
                                            r,
                                            costOfCarry,
                                            vol,
                                            SA)

        v = (v_pos - v_neg) / (0.01/gDaysInYear) / gDaysInYear

        return v

    ###############################################################################

    def rho(self,
              valueDate,
              stockPrice: float,
              r: float,
              costOfCarry: float,
              vol: float,
              SA: float = None,
              adjDays = 0):
        ''' Calculate the approximated delta of an Asian option. '''


        v_neg = self._valueTurnbullWakeman(valueDate,
                                            adjDays,
                                            stockPrice,
                                            r - 0.00005,
                                            costOfCarry,
                                            vol,
                                            SA)

        v_pos = self._valueTurnbullWakeman(valueDate,
                                            adjDays,
                                            stockPrice,
                                            r + 0.00005,
                                            costOfCarry,
                                            vol,
                                            SA)

        v = (v_pos - v_neg) / 0.0001

        return v

    ###############################################################################

    def greeks(self,
              valueDate,
              stockPrice: float,
              r: float,
              costOfCarry: float,
              vol: float,
              SA: float = None,
              adjDays = 0):
        # print(valueDate)
        delta = self.delta(stockPrice, r, costOfCarry, vol, SA, valueDate, adjDays)
        gamma = self.gamma(stockPrice, r, costOfCarry, vol, SA, valueDate, adjDays)
        theta = self.theta(stockPrice, r, costOfCarry, vol, SA, valueDate, adjDays)
        vega = self.vega(stockPrice, r, costOfCarry, vol, SA, valueDate, adjDays)
        rho = self.rho(stockPrice, r, costOfCarry, vol, SA, valueDate, adjDays)

        return np.array([delta, gamma, theta, vega/100, rho/100])

    ###############################################################################
    
    
    

###############################################################################

