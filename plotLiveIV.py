from ThemeOption.finutils import *
from ThemeOption.products import *
from ThemeOption.analysis import *
import numpy as np
import pandas as pd
from datetime import datetime
from WindPy import w
w.start(waitTime=10) # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒  
w.isconnected() # 判断WindPy是否已经登录成功
import numpy as np
import matplotlib.pyplot as plt

def volPlotting():
    
    volrough = 0.475
    expireDate = FinDate(2022,4,11,15,0,'CN')
    now_time = datetime.now()
    FinDateToday = FinDate(now_time.day,now_time.month,now_time.year, now_time.hour, now_time.minute, 'CN')
    def get_K_from_delta(F, callPut, delta, vol):
        T = (expireDate - FinDateToday)/252
        r = 0.05
        b = 0
        v = vol
        return GStrikeFromDelta(callPut, F, T, r, b, v, delta)
    from scipy.stats import norm
    CNDEV = norm.ppf
    c = FinOptionTypes.EUROPEAN_CALL
    p = FinOptionTypes.EUROPEAN_PUT
    def GStrikeFromDelta(callPut, S, T, r, b, v, delta):
    #     print(S, T, r, b, v, delta)
        if callPut == FinOptionTypes.EUROPEAN_CALL:
            GStrikeFromDelta = S * np.exp(-CNDEV(delta * np.exp((r - b) * T)) * v * np.sqrt(T) + (b + v * v / 2) * T)
        else:
            GStrikeFromDelta = S * np.exp(CNDEV(-delta * np.exp((r - b) * T)) * v * np.sqrt(T) + (b + v * v / 2) * T)
        return GStrikeFromDelta
    def boundcheck(x, upper, lower):
        if x>upper:
            return upper
        elif x<lower:
            return lower
        else:
            return x

    x = []
    y = []


    plt.ion()

    def plot_durations(y):
        plt.figure()
        plt.clf()
        plt.subplot(111)
        plt.plot(x, y)
        plt.pause(30)  # pause a bit so that plots are updated

        for i in range(100):
            now_time = datetime.now()
            FinDateToday = FinDate(now_time.day,now_time.month,now_time.year, now_time.hour, now_time.minute, 'CN')
            futurenow = np.mean(w.wsq("I2205.DCE", "rt_ask1,rt_bid1").Data)
            
            upper, lower = 1180, 440
            ATM_K = int(round(get_K_from_delta(futurenow, c, 0.5, volrough), -1))
            ATM_K = boundcheck(ATM_K, upper, lower)
            ATMC_ask, ATMC_bid = w.wsq("I2205-C-"+str(ATM_K)+".DCE", "rt_ask1,rt_bid1").Data
            ATMC_ask, ATMC_bid = ATMC_ask[0], ATMC_bid[0]
            ATMC_premium = (ATMC_ask+ ATMC_bid)/2
            euopt = FinFutureVanillaOption
            iv = euopt(expireDate, ATM_K, c).impliedVol(FinDateToday, futurenow, 0.05, ATMC_premium)
            x.append(datetime.now())
            y.append(iv)
            plot_durations(np.array(y))

if __name__=='__main__':
    volPlotting()
