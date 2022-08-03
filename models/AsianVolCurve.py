##############################################################################
###                        Asian Option Portfolio                          ###
##############################################################################



from datetime import datetime
import numpy as np
import pandas as pd
from ..finutils.FinHelperFunctions import singleContractTimeSpecifier
from ..finutils.SGXHelperFunctions import SGXexpireDate, time_specifier

from ..finutils.FinDate import FinDate
from ..products import * 

from scipy.interpolate import CubicSpline
from scipy import interpolate

vols_asian = {
        2207 : [0.55, 0.538, 0.556, 0.597, 0.631],
        2208 : [0.552, 0.540, 0.559, 0.560, 0.635],
        2209 : [0.554, 0.542, 0.561, 0.573, 0.638],
        2210 : [0.556, 0.544, 0.563, 0.575, 0.640],
        2211 : [0.557, 0.546, 0.564, 0.579, 0.642],
        2212 : [0.559, 0.548, 0.565, 0.582, 0.645],
        2301 : [0.560, 0.550, 0.567, 0.586, 0.647],
        2302 : [0.562, 0.553, 0.569, 0.59, 0.649],
        2303 : [0.564, 0.554, 0.570, 0.593, 0.651],
        2304 : [0.566, 0.556, 0.571, 0.597, 0.653],
        2305 : [0.568, 0.559, 0.572, 0.600, 0.654],
        2306 : [0.569, 0.560, 0.573, 0.605, 0.655],
        2307 : [0.57, 0.561, 0.574, 0.610, 0.656],
        2308 : [0.572, 0.562, 0.575, 0.613, 0.657],
        2309 : [0.573, 0.563, 0.576, 0.615, 0.658],
        2310 : [0.575, 0.564, 0.577, 0.617, 0.659],
        2311 : [0.577, 0.565, 0.578, 0.619, 0.660],
        2312 : [0.578, 0.566, 0.579, 0.620, 0.660]
    }

delta_call = [0.9, 0.75, 0.5, 0.25, 0.1] # 10DP, 25DP, ATM, 25DC, 10DC
delta_put = [-0.1, -0.25, -0.5, -0.75, -0.9] # 10DP, 25DP, ATM, 25DC, 10DC
country = 'SG'
now_time = datetime.now()
FinDateToday = FinDate(now_time.day,now_time.month,now_time.year, now_time.hour, now_time.minute, country)
    

try:
    SGX_IV = pd.read_excel(r"C:\Users\LiGen\OneDrive - Theme International Trading\positions.xlsm", sheet_name = 'IV', skiprows = 2, index_col = 0).iloc[:10,:5].dropna()  
    contract = SGX_IV.index.map(singleContractTimeSpecifier)
    expiry_date = list(zip(*tuple(map(SGXexpireDate,list(zip(*contract))[0], list(zip(*contract))[1]))))[1]
    T = [this_expiry_date - FinDateToday for this_expiry_date in expiry_date]
    SGX_IV.index = T
    SGX_IV.columns = delta_call
except:
    print('Fail to Load SGX IV Excel, will use default vol curve')
    T_dict = {}
    for thistenor in vols_asian:
        contract = singleContractTimeSpecifier(thistenor)
        startAveragingDate, expiry_date = SGXexpireDate(contract[0], contract[1], country)
        T = expiry_date - FinDateToday
        T_dict[T] =  vols_asian[thistenor]
    SGX_IV = pd.DataFrame.from_dict(T_dict, orient='index', columns = delta_call)



def V2tVolInterpolation(thisT, t1, t2, atmVol1, atmVol2, smileVol1, smileVol2):
    tenorVol = 0
    if t1 == t2 :
        tenorVol = smileVol1
    else:
        atmVol_linear = atmVol1 + (atmVol2 - atmVol1) / (t2 - t1) * (thisT - t1)
        atmVar1 = atmVol1 * atmVol1 * t1
        atmVar2 = atmVol2 * atmVol2 * t2
        atmVol_v2t = np.sqrt(((atmVar2 - atmVar1) / (t2 - t1) * (thisT - t1) + atmVar1) / thisT)
        tenorVol = smileVol1 + (smileVol2 - smileVol1) / (t2 - t1) * (thisT - t1) + atmVol_v2t - atmVol_linear
    return tenorVol

def getKeyVols(thisT, IV):
    for i in range(len(IV)):
        if IV.index[i] >= thisT:
            break
    thisVolList = []
    for thisdelta in IV:
        if i == 0 :
            t1 = IV.index[i]
            t2 = IV.index[i]
            atmVol1 = IV[0.5].iloc[i]
            atmVol2 = IV[0.5].iloc[i]
            smileVol1 = IV[thisdelta].iloc[i]
            smileVol2 = IV[thisdelta].iloc[i]
            
        else:
            t1 = IV.index[i-1]
            t2 = IV.index[i]
            atmVol1 = IV[0.5].iloc[i-1]
            atmVol2 = IV[0.5].iloc[i]
            smileVol1 = IV[thisdelta].iloc[i-1]
            smileVol2 = IV[thisdelta].iloc[i]
        thisVol = V2tVolInterpolation(thisT, t1, t2, atmVol1, atmVol2, smileVol1, smileVol2)
        thisVolList.append(thisVol)
    return np.array(thisVolList)
