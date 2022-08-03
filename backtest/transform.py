import numpy as np
import pandas as pd

def null_values(df):
    mis_val = df.isnull().sum()
    mis_val_percent = 100 * df.isnull().sum() / len(df)
    mis_val_table = pd.concat([mis_val, mis_val_percent], axis=1)
    mis_val_table_ren_columns = mis_val_table.rename(
    columns = {0 : 'Missing Values', 1 : '% of Total Values'})
    mis_val_table_ren_columns = mis_val_table_ren_columns[
        mis_val_table_ren_columns.iloc[:,1] != 0].sort_values(
    '% of Total Values', ascending=False).round(1)
    print ("Dataframe has " + str(df.shape[1]) + " columns.\n"      
        "There are " + str(mis_val_table_ren_columns.shape[0]) +
          " columns that have missing values.")
    return mis_val_table_ren_columns

def HT(df, n=2):
    """Get the head and tail of a DataFrame"""
    return df.iloc[np.r_[0:n, -n:0]]

def NANS(df):
    """Create a DataFrame filled with np.nan"""
    return pd.DataFrame(np.nan, index=df.index, columns=df.columns)

def ZEROS(df):
    """Create a DataFrame filled with zeros"""
    return pd.DataFrame(0, index=df.index, columns=df.columns)

def ONES(df):
    """Create a DataFrame filled with ones"""
    return pd.DataFrame(1, index=df.index, columns=df.columns)

def DIFF(df, window=1):
    """Get the differenced series of a DataFrame"""
    return df - df.shift(window)

def RTN(df, window=1, freq="D"):
    """Get the returns from a price DataFrame"""
    df_rtn = df.pct_change().rolling(window).mean()
    if freq == "D":
        return df_rtn
    elif freq == "Y":
        return df_rtn * 252
    
def SMA(df, window=1):
    """Get the simple moving average of a DataFrame"""
    return df.rolling(window).mean()

def EMA(df, halflife=None, alpha=None, com=None, span=None, adjust=True):
    """Get the exponentially weigted moving average of a DataFrame"""
    return df.ewm(halflife=halflife, alpha=alpha, com=com, span=span, adjust=adjust, ignore_na=True).mean()

def ROLLVOL(df, window=252, method="simple", halflife=None, alpha=None, com=None,  span=None, adjust=True):
    """Get the rolling voilatility"""
    if method == "simple":
        return df.rolling(window).std() + 10**(-10) # Add a small value to avoid zero division
    elif method == "exponential":
        if halflife:
            window = halflife
        if span:
            alpha = 2 / (span+1)
        if com:
            alpha = 1 / (1+com)
        if alpha:
            window = -np.log(2) / np.log(1-alpha)
        return df.ewm(halflife=window, adjust=True, ignore_na=True).var() ** 0.5 + 10**(-10) # Add a small value to avoid zero division

def TSNORM(df, window=252, method="simple", alpha=None, adjust=True, rf=0):
    """Get the normalised series along time series"""
    return df.sub(rf).div(df.pipe(ROLLVOL, window=window, method=method, alpha=alpha, adjust=adjust))

def XSNORM(df, rf=0):
    """Get the returns normalised by cross-sectional volatility"""
    return df.sub(rf).div(df.std(axis=1)+10**(-10), axis=0)

def TSDM(df, window=None, method="simple", alpha=None, com=None, span=None, adjust=True):
    """Get the demeaned series along the time series"""
    if not window:
        return df.sub(df.mean(axis=0), axis=1)
    elif method == "simple":
        return df.sub(df.pipe(SMA, window=window))
    elif method == "exponential":
        return df.sub(df.pipe(EMA, window=window, alpha=alpha, com=com, span=span, adjust=adjust, ignore_na=True))        

def XSDM(df):
    """Get the demeaned series across columns"""
    return df.sub(df.mean(axis=1), axis=0)

def TSZSCORE(df, window=None):
    """Get the rolling standard z-score"""
    if not window:
        return df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1), axis=0)
    else:
        return df.sub(df.rolling(window).mean()).div(df.rolling(window).std() + 10**(-10)) # Add a small value to avoid zero division

def XSZSCORE(df, window=None):
    """Get the standard z-score across columns"""
    return df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1)+10**(-10), axis=0)

