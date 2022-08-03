import pandas as pd

def PortfolioActionBacktest(actionDF, priceDF):
    
    cashEarnen = - actionDF * priceDF
    cashCum = cashEarnen.cumsum()
    if type(cashCum) != pd.Series:
        cashCum = cashCum.sum(axis = 1)
    postionDF = actionDF.cumsum()
    portfolioValue = postionDF*priceDF
    portfolioValue = portfolioValue.sum(axis = 1) + cashCum
    return portfolioValue

def PortfolioPositionBacktest(postionDF, priceDF):
    actionDF = postionDF.diff()
    actionDF.iloc[0] = postionDF.iloc[0]
    return PortfolioActionBacktest(actionDF, priceDF)

def HedgeWithBool(totalDeltaSeries, boolSeries):
    positionSeries = - totalDeltaSeries.where(boolSeries)
    positionSeries = positionSeries.fillna(method = 'ffill')
    return positionSeries

def BacktestPlotting(portfolioValue):
    pass

def BacktestPerformanceMeasurements(portfolioValue):
    pass