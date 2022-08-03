import xlwings as xw
import pandas as pd
from ThemeOption.products.AsianOptions import opt

@xw.func
def asianprice(tenor, K, callPut, position, S, SA, adjday, adjvol):
    if type(tenor) == float:
        tenor = int(tenor)
    contractTuple = (tenor, str(K) + callPut, position)
    thisOption = opt(contractTuple, S, SA = SA, adjday = adjday, adjvol = adjvol)
    return thisOption.value()

@xw.func
def asianvol(tenor, K, callPut, position, S, SA, adjday, adjvol):
    if type(tenor) == float:
        tenor = int(tenor)
    contractTuple = (tenor, str(K) + callPut, position)
    thisOption = opt(contractTuple, S, SA = SA, adjday = adjday, adjvol = adjvol)
    return thisOption.volmean

@xw.func
def asiandelta(tenor, K, callPut, position, S, SA, adjday, adjvol):
    if type(tenor) == float:
        tenor = int(tenor)
    contractTuple = (tenor, str(K) + callPut, position)
    thisOption = opt(contractTuple, S, SA = SA, adjday = adjday, adjvol = adjvol)
    return thisOption.delta()

@xw.func
def asiangamma(tenor, K, callPut, position, S, SA, adjday, adjvol):
    if type(tenor) == float:
        tenor = int(tenor)    
    contractTuple = (tenor, str(K) + callPut, position)
    thisOption = opt(contractTuple, S, SA = SA, adjday = adjday, adjvol = adjvol)
    return thisOption.gamma()

@xw.func
def asiantheta(tenor, K, callPut, position, S, SA, adjday, adjvol):
    if type(tenor) == float:
        tenor = int(tenor)
    contractTuple = (tenor, str(K) + callPut, position)
    thisOption = opt(contractTuple, S, SA = SA, adjday = adjday, adjvol = adjvol)
    return thisOption.theta()

@xw.func
def asianvega(tenor, K, callPut, position, S, SA, adjday, adjvol):
    if type(tenor) == float:
        tenor = int(tenor)
    contractTuple = (tenor, str(K) + callPut, position)
    thisOption = opt(contractTuple, S, SA = SA, adjday = adjday, adjvol = adjvol)
    return thisOption.vega()

@xw.func
def asianrho(tenor, K, callPut, position, S, SA, adjday, adjvol):
    
    if type(tenor) == float:
        tenor = int(tenor)
    contractTuple = (tenor, str(K) + callPut, position)
    thisOption = opt(contractTuple, S, SA = SA, adjday = adjday, adjvol = adjvol)
    return thisOption.rho()

@xw.func
@xw.arg('df', pd.DataFrame, index=False, header=False)
def myOptionPortfolio(df, adjday, adjvol):
    # wb = xw.Book.caller()
    # sheet = wb.sheets['Outright']
    # # wb = xw.Book(direc)
    # # sheet = wb.sheets[sheetname]
    # # adjday = sheet.range('B1').value
    # # adjvol = sheet.range('D1').value
    # SA = wb.sheets['Ref'].range('B2').value

    tenor = df.iloc[0,0]
    callPut = df.iloc[0,1]
    K = df.iloc[0,2]
    pos = df.iloc[0,3]
    S = df.iloc[0,4]
    SA = df.iloc[0,5]
    tenor = int(tenor)
    contractTuple = (tenor, str(K) + callPut, pos)
    thisOption = opt(contractTuple, S, SA = SA, adjday = adjday, adjvol = adjvol)
    for i in range(1, len(df)):
        tenor = df.iloc[i,0]
        callPut = df.iloc[i,1]
        K = df.iloc[i,2]
        pos = df.iloc[i,3]
        S = df.iloc[i,4]
        SA = df.iloc[i,5]
        tenor = int(tenor)
        contractTuple = (tenor, str(K) + callPut, pos)
        
        if SA == None: 
            thisOption.addOption(contractTuple, S)
        else:
            thisOption.addOption(contractTuple, S, SA = SA)
            
    return thisOption.value(), thisOption.volmean, thisOption.delta(), thisOption.gamma(), thisOption.theta(), thisOption.vega(), thisOption.rho()
