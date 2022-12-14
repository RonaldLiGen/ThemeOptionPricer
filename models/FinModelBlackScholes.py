##############################################################################
###                      BS formula and GBS formula                        ###
##############################################################################

# TODO Fix this

import numpy as np
from scipy.stats import norm
from ..finutils.FinGlobalVariables import gSmall
N = norm.cdf

###############################################################################
# This is intended to be a fast calculator and validation is left to calling
# functions.


def bsValue(s, t, k, r, q, v, phi):
    ''' Price a derivative using Black-Scholes model where phi is 1 for a call,
    and -1 for a put.'''

    k = np.maximum(k, gSmall)
    t = np.maximum(t, gSmall)
    v = np.maximum(v, gSmall)

    sqrtT = np.sqrt(t)
    ss = s * np.exp(-q*t)
    kk = k * np.exp(-r*t)
    d1 = np.log(ss/kk) / v / sqrtT + v * sqrtT / 2.0
    d2 = d1 - v * sqrtT
    v = phi * ss * N(phi*d1) - phi * kk * N(phi*d2)
    return v

###############################################################################

def gbsValue(s, t, k, r, b, v, phi):
    ''' Price a derivative using Black-Scholes model where phi is 1 for a call,
    and -1 for a put.'''

    d1 = (np.log(s/k)  + (r-b+v**2/2)*t)/(v*np.sqrt(t))
    d2 = d1 - (v*np.sqrt(t))

    v = phi*s*np.exp((b-r)*t)*N(phi * d1) - phi*k*np.exp(-r*t)*N(phi * d2)

    return v