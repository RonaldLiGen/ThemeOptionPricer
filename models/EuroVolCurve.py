##############################################################################
###                       Asian Option Vol Surface                         ###
##############################################################################

from datetime import datetime
import numpy as np
import pandas as pd
from ..finutils.FinHelperFunctions import singleContractTimeSpecifier
from ..finutils.DCEHelperFunctions import DCEexpireDate, time_specifier
from ..finutils.FinDate import FinDate
# from scipy import interpolate

vols_euro = {
    2208 : [0.77, 0.67, 0.59, 0.56, 0.56],
    2209 : [0.77, 0.67, 0.59, 0.56, 0.56],
    2301 : [0.77, 0.67, 0.59, 0.56, 0.56],
    2305 : [0.77, 0.67, 0.59, 0.56, 0.56]
}
delta_call = [0.9, 0.75, 0.5, 0.25, 0.1] # 10DP, 25DP, ATM, 25DC, 10DC
delta_put = [-0.1, -0.25, -0.5, -0.75, -0.9] # 10DP, 25DP, ATM, 25DC, 10DC
country = 'CN'
now_time = datetime.now()
FinDateToday = FinDate(now_time.day,now_time.month,now_time.year, now_time.hour, now_time.minute, country)
    

try:
    DCE_IV = pd.read_excel(r"C:\Users\LiGen\OneDrive - Theme International Trading\positions.xlsm", sheet_name = 'IV', skiprows = 14, index_col = 0).iloc[:,:5].dropna()   
    contract = DCE_IV.index.map(singleContractTimeSpecifier)
    expiry_date = list(map(DCEexpireDate,list(zip(*contract))[0], list(zip(*contract))[1]))
    T = [this_expiry_date - FinDateToday for this_expiry_date in expiry_date]
    DCE_IV.index = T
    DCE_IV.columns = delta_call
except:
    print('Fail to Load DCE IV Excel, will use default vol curve')
    T_dict = {}
    for thistenor in vols_euro:
        contract = singleContractTimeSpecifier(thistenor)
        startAveragingDate, expiry_date = DCEexpireDate(contract[0], contract[1], country)
        T = expiry_date - FinDateToday
        T_dict[T] =  vols_euro[thistenor]
    DCE_IV = pd.DataFrame.from_dict(T_dict, orient='index', columns = delta_call)



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


