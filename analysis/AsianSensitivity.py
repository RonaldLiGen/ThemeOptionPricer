from ..finutils import *
from ..products import *


import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd

def analysis_S(contract, spread = None, adjday = 0, vol = None, S = None, SA = None, step = 2):
    
    if S == None:
        S = float(contract[1][:-1])
    if vol == None:
        thisOption = opt(contract, S, spread = spread, adjday = adjday, SA = SA)
        vol = round(thisOption._volmean, 4)
    else:
        vol = round(vol / 100, 4)
    
    start = int(S - 10*step)
    end = int(S + 10*step) + step
    greeks = opt(contract, start, spread = spread, adjday = adjday, fixedVol = vol).greeks()
    
    for s in range(start+step, end, step):
        thisOption = opt(contract, s, spread = spread, adjday = adjday, fixedVol = vol, SA = SA)
        thisGreeks = thisOption.greeks()
        greeks = np.vstack((greeks, thisGreeks))

    greeks = np.around(greeks, 4)
    greeksDF = pd.DataFrame(greeks, columns = ['Delta','Gamma','Theta','Vega','Rho'], index = range(start, end, step))
    greeksDF.index.name = 'S'
    return greeksDF

def analysis_VOL(contract, spread = None, adjday = 0, vol = None, S = None, SA = None, step = 1):
    
    step = step / 100
    if S == None:
        S = float(contract[1][:-1])
    if vol == None:
        thisOption = opt(contract, S, spread = spread, adjday = adjday, SA = SA)
        vol = round(thisOption.volmean, 4)
    else:
        vol = round(vol / 100, 4)
        
    start = vol - 15*step
    end = vol + 12*step
    greeks = opt(contract, S, spread = spread, adjday = adjday, fixedVol = start).greeks()
    
    for v in np.arange(start+step, end, step):
        thisOption = opt(contract, S, spread = spread, adjday = adjday, fixedVol = v, SA = SA)
        thisGreeks = thisOption.greeks()
        greeks = np.vstack((greeks, thisGreeks))

    greeks = np.around(greeks, 4)
    greeksDF = pd.DataFrame(greeks, columns = ['Delta','Gamma','Theta','Vega','Rho'], index = np.around(np.arange(start*100, end*100, step*100), 2))
    greeksDF.index.name = 'Vol'
    return greeksDF

def analysis_T(contract, spread = None, vol = None, S = None, SA = None, step = 1):
    
    if S == None:
        S = float(contract[1][:-1])
    if SA == None:
        SA = S
    if vol == None:
        thisOption = opt(contract, S, spread = spread, SA = SA)
        vol = thisOption.volmean
    else:
        vol = vol / 100
    
    start = -20
    end = 21
    
    greeks = opt(contract, S, spread = spread, adjday = start, fixedVol = vol).greeks()

    for day in np.arange(start+step, end, step):
        thisOption = opt(contract, S, spread = spread, adjday = day, fixedVol = vol, SA = SA)
        thisGreeks = thisOption.greeks()
        greeks = np.vstack((greeks, thisGreeks))

    greeks = np.around(greeks, 4)
    greeksDF = pd.DataFrame(greeks, columns = ['Delta','Gamma','Theta','Vega','Rho'], index = np.arange(start, end, step))
    greeksDF.index.name = 'Adj_Days'
    return greeksDF

def analysis_S_VOL(contract, spread = None, S = None, adjday = 0, vol = None, SA = None, S_step = 1, vol_step = 3):
    
    if S == None:
        S = float(contract[1][:-1])
    if vol == None:
        thisOption = opt(contract, S, spread = spread, adjday = adjday, SA = SA)
        vol = thisOption._volmean
    
    S_start = int(S - 10*S_step)
    S_end = int(S + 10*S_step) + S_step
    
    deltaDF = pd.DataFrame()
    gammaDF = pd.DataFrame()
    thetaDF = pd.DataFrame()
    vegaDF = pd.DataFrame()
    rhoDF = pd.DataFrame()
    for s in np.arange(S_start, S_end, S_step):
        thisGreeks = analysis_VOL(contract, spread = spread, adjday = 0, vol = vol, S = s, SA = SA, step = vol_step)
        thisDelta = thisGreeks['Delta']
        deltaDF[s] = thisDelta
        thisGamma = thisGreeks['Gamma']
        gammaDF[s] = thisGamma
        thisTheta = thisGreeks['Theta']
        thetaDF[s] = thisTheta
        thisVega = thisGreeks['Vega']
        vegaDF[s] = thisVega
        thisRho = thisGreeks['Rho']
        rhoDF[s] = thisRho
        
    deltaDF.columns.name = 'S'
    gammaDF.columns.name = 'S'
    thetaDF.columns.name = 'S'
    vegaDF.columns.name = 'S'
    rhoDF.columns.name = 'S'
    return deltaDF, gammaDF, thetaDF, vegaDF, rhoDF

def plottable_3d_info(df: pd.DataFrame):
    """
    Transform Pandas data into a format that's compatible with
    Matplotlib's surface and wireframe plotting.
    """
    index = df.index
    columns = df.columns

    x, y = np.meshgrid(np.arange(len(columns)), np.arange(len(index)))
    z = np.array([[df[c][i] for c in columns] for i in index])
    
    xticks = dict(ticks=np.arange(len(columns)), labels=columns)
    yticks = dict(ticks=np.arange(len(index)), labels=index)
    
    return x, y, z, xticks, yticks

### Transform to Matplotlib friendly format.
def plotSingleGreek(greekdf, zlabel):
    x, y, z, xticks, yticks = plottable_3d_info(greekdf)

    ### Set up axes and put data on the surface.
    fig = plt.figure(figsize = (16,16))
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, cmap=cm.rainbow,
                           linewidth=0, antialiased=False)

    ### Customize labels and ticks (only really necessary with
    ### non-numeric axes).
    ax.set_xlabel(greekdf.columns.name)
    ax.set_ylabel(greekdf.index.name)
    ax.set_zlabel(zlabel)
    ax.set_zlim3d()
    plt.xticks(**xticks)
    plt.yticks(**yticks)
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.show()

def S_VOL(contract, spread = None, S = None, adjday = 0, vol = None, SA = None, S_step = 1, vol_step = 3):
    deltaDF, gammaDF, thetaDF, vegaDF, rhoDF = analysis_S_VOL(contract, 
                                                              spread, 
                                                              S, 
                                                              adjday, 
                                                              vol, 
                                                              SA, 
                                                              S_step, 
                                                              vol_step)
    plotSingleGreek(deltaDF, 'Delta')
    plotSingleGreek(gammaDF, 'Gamma')
    plotSingleGreek(thetaDF, 'Theta')
    plotSingleGreek(vegaDF, 'Vega')
    plotSingleGreek(rhoDF, 'Rho')

def analysis_S_T(contract, spread = None, S = None, vol = None, SA = None, S_step = 3, T_step = 1):
    
    if S == None:
        S = float(contract[1][:-1])
    if vol == None:
        thisOption = opt(contract, S, spread = spread, SA = SA)
        vol = thisOption._volmean
        vol = vol * 100
    
    S_start = int(S - 10*S_step)
    S_end = int(S + 10*S_step) + S_step
    
    deltaDF = pd.DataFrame()
    gammaDF = pd.DataFrame()
    thetaDF = pd.DataFrame()
    vegaDF = pd.DataFrame()
    rhoDF = pd.DataFrame()
    
    for s in np.arange(S_start, S_end, S_step):
        thisGreeks = analysis_T(contract, spread = spread, vol = vol, S = s, SA = SA, step = T_step)
        thisDelta = thisGreeks['Delta']
        deltaDF[s] = thisDelta
        thisGamma = thisGreeks['Gamma']
        gammaDF[s] = thisGamma
        thisTheta = thisGreeks['Theta']
        thetaDF[s] = thisTheta
        thisVega = thisGreeks['Vega']
        vegaDF[s] = thisVega
        thisRho = thisGreeks['Rho']
        rhoDF[s] = thisRho
        
    deltaDF.columns.name = 'S'
    gammaDF.columns.name = 'S'
    thetaDF.columns.name = 'S'
    vegaDF.columns.name = 'S'
    rhoDF.columns.name = 'S'
    return deltaDF, gammaDF, thetaDF, vegaDF, rhoDF

def S_T(contract, spread = None, S = None, vol = None, SA = None, S_step = 3, T_step = 1):
    deltaDF, gammaDF, thetaDF, vegaDF, rhoDF = analysis_S_T(contract, 
                                                              spread, 
                                                              S, 
                                                              vol, 
                                                              SA, 
                                                              S_step, 
                                                              T_step)
    plotSingleGreek(deltaDF, 'Delta')
    plotSingleGreek(gammaDF, 'Gamma')
    plotSingleGreek(thetaDF, 'Theta')
    plotSingleGreek(vegaDF, 'Vega')
    plotSingleGreek(rhoDF, 'Rho')

def analysis_VOL_T(contract, spread = None, S = None, vol = None, SA = None, Vol_step = 1, T_step = 1):
    
    if S == None:
        S = float(contract[1][:-1])
    if vol == None:
        thisOption = opt(contract, S, spread = spread, SA = SA)
        vol = thisOption.volmean
        vol = vol * 100
    
    vol_start = (vol - 10*Vol_step)
    vol_end = (vol + 10*Vol_step) + Vol_step
    
    deltaDF = pd.DataFrame()
    gammaDF = pd.DataFrame()
    thetaDF = pd.DataFrame()
    vegaDF = pd.DataFrame()
    rhoDF = pd.DataFrame()
    
    for this_vol in np.around(np.arange(vol_start, vol_end, Vol_step), 2):
        thisGreeks = analysis_T(contract, spread = spread, vol = this_vol, S = S, SA = SA, step = T_step)
        thisDelta = thisGreeks['Delta']
        deltaDF[this_vol] = thisDelta
        thisGamma = thisGreeks['Gamma']
        gammaDF[this_vol] = thisGamma
        thisTheta = thisGreeks['Theta']
        thetaDF[this_vol] = thisTheta
        thisVega = thisGreeks['Vega']
        vegaDF[this_vol] = thisVega
        thisRho = thisGreeks['Rho']
        rhoDF[this_vol] = thisRho
        
    deltaDF.columns.name = 'Vol'
    gammaDF.columns.name = 'Vol'
    thetaDF.columns.name = 'Vol'
    vegaDF.columns.name = 'Vol'
    rhoDF.columns.name = 'Vol'
    return deltaDF, gammaDF, thetaDF, vegaDF, rhoDF

def VOL_T(contract, spread = None, S = None, vol = None, SA = None, Vol_step = 1, T_step = 1):
    deltaDF, gammaDF, thetaDF, vegaDF, rhoDF = analysis_VOL_T(contract, 
                                                              spread, 
                                                              S, 
                                                              vol, 
                                                              SA, 
                                                              Vol_step, 
                                                              T_step)
    plotSingleGreek(deltaDF, 'Delta')
    plotSingleGreek(gammaDF, 'Gamma')
    plotSingleGreek(thetaDF, 'Theta')
    plotSingleGreek(vegaDF, 'Vega')
    plotSingleGreek(rhoDF, 'Rho')