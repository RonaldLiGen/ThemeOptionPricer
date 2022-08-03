# import numpy as np
# import scipy.stats as scs
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import yfinance as yf
# from statsmodels.tsa.seasonal import seasonal_decompose
# from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
# import statsmodels.api as sm
# from empyrical.stats import sharpe_ratio
# from .transform import SMA, EMA, ROLLVOL

# colours = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
#            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', 
#            '#00008B', '#FFD700', '#32CD32', '#FF4500', '#4B0082', 
#            '#CD853F', '#DA70D6', '#2F4F4F', '#3CB371', '#008080']

# plt.style.use("seaborn")
# plt.rcParams["figure.figsize"] = [16, 9]
# plt.rcParams["figure.dpi"] = 300
# plt.rcParams["axes.titlesize"] = 24
# plt.rcParams["axes.titleweight"] = "bold"
# plt.rcParams["axes.labelsize"] = 18
# sns.set_palette(sns.color_palette(colours))

# def plot_series(df, start=None, end=None, benchmark=None, title="Series", figsize=(16, 9), **kwargs):
#     """Plot a DataFrame of time series"""
#     if isinstance(df, pd.Series):
#         df = df.to_frame()
#     # Slice the desirable time range
#     df_full = df.copy()
#     if start:
#         if end:
#             df_select = df_full[start:end]
#         else:
#             df_select = df_full[start:]
#     elif end:
#         df_select = df_full[:end]
#     else:
#         df_select = df_full
    
#     columns = df_select.columns
    
#     # Get the data for benchmark asset
#     if benchmark:
#         df_select[benchmark] = yf.download(benchmark, start=df_full.index[0].date(), end=df_full.index[-1].date(), auto_adjust=True, progress=False)["Close"].pct_change()
#         df_select.iloc[0] = 0
    
#     # Plot the return series
#     fig, ax = plt.subplots(1, figsize=figsize)
    
#     df_select[columns].plot(ax=ax, **kwargs)
#     if benchmark:
#         df_select[benchmark].plot(ax=ax, color="black", label=benchmark, **kwargs)    
    
#     plt.xlabel("")
#     ax.tick_params(labelsize=12)
    
#     # Configure the legends
#     if len(columns) <= 15:
#         ax.legend(loc="upper left", prop={"size": 12, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)
#     elif len(columns) <= 30:
#         ax.legend(loc="upper left", ncol=2, prop={"size": 12, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)
#     else:
#         ax.legend(loc="upper left", ncol=3, prop={"size": 12, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)
    
#     ax.set_title(title)
#     return ax

# def plot_return(df, input="return", start=None, end=None, metric="sharpe_ratio", rf=0.0, period="daily", title="Return", benchmark=None, sort_legends=True, ax=None, figsize=(16, 9), **kwargs):
#     """Plot cumulative returns of time series"""
#     if isinstance(df, pd.Series):
#         df = df.to_frame()
#     # Slice the desirable time range
#     df_full = df.copy()
#     if start:
#         if end:
#             df_select = df_full[start:end]
#         else:
#             df_select = df_full[start:]
#     elif end:
#         df_select = df_full[:end]
#     else:
#         df_select = df_full
    
#     columns = df_select.columns.tolist()
    
#     if input in ["price", "Price", "px", "prc"]:
#         df_select = df_select.pct_change()
#         df_select.iloc[0] = 0
#     elif input in ["return", "Return", "rtn", "RTN"]:
#         pass
#     else:
#         raise ValueError(str(input) + "is not one of [\"price\", \"return\"]")
    
#     # Get the data for benchmark asset
#     if benchmark:
#         if benchmark in columns:
#             columns.remove(benchmark)
#         else:
#             df_select[benchmark] = yf.download(benchmark, start=df_full.index[0].date(), end=df_full.index[-1].date(), auto_adjust=True, progress=False)["Close"].pct_change()
    
#     df_select.iloc[0] = 0
#     df_rtn = df_select.add(1).cumprod(axis=0).sub(1) # Compounding

#     # Calculate the Sharpe ratios
#     width = max(len(str(c)) for c in df_select.columns) + 1
#     if metric in ["sharpe_ratio", "sharpe", "sr", "SR"]:
#         sharpe_ratios = pd.Series(sharpe_ratio(df_select, risk_free=rf, period=period), index=df_select.columns)
#         legends = ["{:<{width}}".format(c, width=width) + "SR=" + "{: 0.2f}".format(sharpe_ratios[c]) for c in columns]
#         orders = pd.Series(sharpe_ratios).rank(ascending=False)
#         if benchmark:
#             b_legend = "{:<{width}}".format(benchmark, width=width) + "SR=" + "{: 0.2f}".format(sharpe_ratios[benchmark])
#     elif metric in ["return", "total_return", "annual_return", "tot_return", "avg_return", "rtn"]:
#         tot_returns = df_select.mean() * 252
#         legends = ["{:<{width}}".format(c, width=width) + "R=" + "{: 0.2f}".format(tot_returns[c]) for c in columns]
#         orders = pd.Series(tot_returns).rank(ascending=False)
#         if benchmark:
#             b_legend = "{:<{width}}".format(benchmark, width=width) + "R=" + "{: 0.2f}".format(tot_returns[benchmark])
    
#     # Plot the return series
#     if not ax:
#         fig, ax = plt.subplots(1, figsize=figsize)
#         fontsize = 12
#     else:
#         fontsize=9
    
#     if len(columns) > 30:
#         columns = [x for _, x in sorted(zip(orders.to_list(), columns), key=lambda pair: pair[0])]
#         columns = columns[:5] + columns[-5:]
#     for c in range(len(columns)):
#         df_rtn[columns[c]].plot(ax=ax, label=legends[c], **kwargs)
#     if benchmark:
#         df_rtn[benchmark].plot(ax=ax, color="black", label=b_legend, **kwargs)    
    
#     ax.axhline(0.0, color="black", linestyle="-", lw=2) # Add a normal horizontal line
#     ax.set_xlabel("")
#     vals = ax.get_yticks()
#     ax.set_yticklabels(['{:,.0%}'.format(x) for x in vals], fontsize=fontsize)
#     ax.tick_params(labelsize=fontsize)
    
#     # Configure the legends
#     handles, labels = ax.get_legend_handles_labels()
#     if sort_legends:
#             handles = [x for _, x in sorted(zip(orders.to_list(), handles), key=lambda pair: pair[0])]
#             labels = [x for _, x in sorted(zip(orders.to_list(), labels), key=lambda pair: pair[0])]

#     if len(columns) <= 15:
#         ax.legend(handles, labels, loc="upper left", prop={"size": fontsize, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)
#     elif len(columns) <= 30:
#         ax.legend(handles, labels, loc="upper left", ncol=2, prop={"size": fontsize, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)
#     else:
#         handles = handles[:5] + handles[-5:]
#         labels = labels[:5] + labels[-5:]
#         ax.legend(handles, labels, loc="upper left", ncol=3, prop={"size": fontsize, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)
    
#     ax.set_title(title, size=fontsize+10)
#     return ax

# def plot_dist(ts, bins=50, kde=True, stat="count", standardise=False, title="Return Histogram", color="slateblue", alpha=0.5, figsize=(16, 9), **kwargs):
#     """Plot a histogram and a Q-Q polot side-by-side"""
#     fig, axes = plt.subplots(1, 2, figsize=figsize)
#     mu = ts.mean()
#     sigma = ts.std()
#     if standardise:
#         ts = (ts - mu) / sigma
#         sns.histplot(ts, ax=axes[0], color=color, kde=kde, stat=stat, label="F(0,1)", **kwargs)      
#     else:
#         sns.histplot(ts, ax=axes[0], color=color, kde=kde, stat=stat, label=f"F({mu:.2f}, ${sigma: .2f}^2$)", **kwargs)
#     if standardise and stat=="density":
#         r_range = np.linspace(axes[0].get_xlim()[0], axes[0].get_xlim()[1])
#         axes[0].plot(r_range, scs.norm.pdf(r_range), "darkred", lw=2, label="N(0,1)")
#     elif stat=="density":
#         r_range = np.linspace(axes[0].get_xlim()[0], axes[0].get_xlim()[1])
#         axes[0].plot(r_range, scs.norm.pdf(r_range, loc=mu, scale=sigma), "darkred", lw=2, label=f"N({mu:.2f}, ${sigma: .2f}^2$)")
#     axes[0].set_title(title)  
#     axes[0].legend(loc="upper left", prop={"size": 14, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)
#     axes[0].tick_params(labelsize=12)
#     sm.qqplot(ts, ax=axes[1], line="s", markerfacecolor="slateblue", alpha=0.5)
#     axes[1].tick_params(labelsize=12)
#     axes[1].set_title("Q-Q Plot")
#     plt.tight_layout()
#     plt.show()

# def plot_market_corr(ser, start=None, end=None, name="Return", benchmark="SPY", plot=True, **kwargs):
#     """Plot asset correlation with market"""
#     df_full = ser.to_frame(name=name)
    
#     if start:
#         if end:
#             df_select = df_full[start:end]
#         else:
#             df_select = df_full[start:]
#     elif end:
#         df_select = df_full[:end]
#     else:
#         df_select = df_full
        
#     if benchmark:
#         df_select[benchmark] = yf.download(benchmark, start=df_full.index[0].date(), end=df_full.index[-1].date(), auto_adjust=True, progress=False)["Close"].pct_change()
#         df_select[benchmark][0] = 0
    
#     covar = df_select.iloc[:, 0].cov(df_select[benchmark])
#     var1 = df_select.iloc[:, 0].var()
#     var2 = df_select[benchmark].var()
#     rho = covar / np.sqrt(var1) / np.sqrt(var2)
#     beta = covar / var2
    
#     if plot:
#         sns.jointplot(y=df_select.iloc[:, 0], x=df_select[benchmark], kind="reg", height=8, 
#                       joint_kws={"scatter_kws": dict(alpha=0.3), "color": "slateblue", "line_kws": dict(color="darkred")}, marginal_kws={"color": "slateblue", "bins": 60}, **kwargs)
    
#         plt.annotate(r"$\rho$ = {:.2f}".format(rho), xy=(0.8, 0.55), xycoords="axes fraction", fontsize=12)
#         plt.annotate(r"$\beta$ = {:.2f}".format(beta), xy=(0.8, 0.52), xycoords="axes fraction", fontsize=12)
    
#     return {"rho": rho, "beta": beta}

# def plot_technical(df, start=None, end=None, title="Price", style="line", benchmark="SPY", sma=False, ema=False, 
#        bollinger_bands=True, volume=True, macd=True, rsi=True, atr=False, figsize=(16, 9)):
#     """Plot a technical chart with Matplotlib"""
#     if isinstance(df, pd.Series):
#         df = df.to_frame(name="Close")
#     elif len(df.columns) == 1:
#         df.columns = ["Close"]

#     # Create some common indicator columns
#     df_full = df.copy()
#     df_full["BB_Mid"] = df_full.Close.pipe(SMA, 20)
#     df_full["BB_Up"] = df_full.BB_Mid + df_full.Close.pipe(ROLLVOL, 20) * 2
#     df_full["BB_Low"] = df_full.BB_Mid - df_full.Close.pipe(ROLLVOL, 20) * 2
    
#     def RSI(ts):
#         ts = ts - ts.shift(1)
#         gains = [i if i>0 else np.nan for i in ts[1:]]
#         losses = [np.abs(i) if i<0 else np.nan for i in ts[1:]]
#         rs = np.nanmean(gains) / np.nanmean(losses)
#         return 100 - 100 / (1+rs)
#     df_full["RSI"] = df_full.Close.rolling(15).apply(RSI)
#     df_full["MACD"] = df_full.Close.pipe(EMA, span=12) - df_full.Close.pipe(EMA, span=26)
#     df_full["MACD_Sig"] = df_full.MACD.pipe(EMA, span=9)
#     df_full["MACD_Hist"] = df_full.MACD - df_full.MACD_Sig

#     if atr:
#         df_full["ATR"] = pd.DataFrame([np.abs(df_full.High - df_full.Low), 
#                                        np.abs(df_full.High - df_full.shift(1).Close),
#                                        np.abs(df_full.Low - df_full.shift(1).Close)]).max(axis=0).pipe(EMA, alpha=1/14, adjust=False)
 
#     # Create moving averages
#     if sma:
#         if type(sma) == bool:
#             df_full["SMA"] = df_full.Close.pipe(SMA, 10)
#         elif type(sma) in (int, float):
#             df_full["SMA"] = df_full.Close.pipe(SMA, int(sma))
#         elif type(sma) in (tuple, list):
#             periods = np.sort([i for i in sma])
#             if len(periods) == 1:
#                 df_full["SMA"] = df_full.Close.pipe(SMA, int(periods[0]))
#             elif len(periods) == 2:
#                 df_full["SMA1"] = df_full.Close.pipe(SMA, int(periods[0]))
#                 df_full["SMA2"] = df_full.Close.pipe(SMA, int(periods[1]))
#             else:
#                 df_full["SMA1"] = df_full.Close.pipe(SMA, int(periods[0]))
#                 df_full["SMA2"] = df_full.Close.pipe(SMA, int(periods[1]))
#                 df_full["SMA3"] = df_full.Close.pipe(SMA, int(periods[-1]))
                
#     if ema:
#         if type(ema) == bool:
#             df_full["EMA"] = df_full.Close.pipe(EMA, span=10)
#         elif type(ema) in (int, float):
#             df_full["EMA"] = df_full.Close.pipe(EMA, span=int(ema))
#         elif type(ema) in (tuple, list):
#             periods = np.sort([i for i in ema])
#             if len(periods) == 1:
#                 df_full["EMA"] = df_full.Close.pipe(EMA, span=int(periods[0]))
#             elif len(periods) == 2:
#                 df_full["EMA1"] = df_full.Close.pipe(EMA, span=int(periods[0]))
#                 df_full["EMA2"] = df_full.Close.pipe(EMA, span=int(periods[1]))
#             else:
#                 df_full["EMA1"] = df_full.Close.pipe(EMA, span=int(periods[0]))
#                 df_full["EMA2"] = df_full.Close.pipe(EMA, span=int(periods[1]))
#                 df_full["EMA3"] = df_full.Close.pipe(EMA, span=int(periods[-1]))
    
#     # Slice the desirable time range
#     if start:
#         if end:
#             df_select = df_full[start:end]
#         else:
#             df_select = df_full[start:]
#     elif end:
#         df_select = df_full[:end]
#     else:
#         df_select = df_full
#     df_select = df_select.dropna()
    
#     # Get the data for benchmark asset
#     if benchmark:
#         df_select[benchmark] = yf.download(benchmark, start=df_full.index[0].date(), end=df_full.index[-1].date(), auto_adjust=True, progress=False)["Close"].pct_change()
#         df_select[benchmark][0] = 0
#         df_select[benchmark] = df_select[benchmark].cumsum().add(1).multiply(df_select.Close[0])
    
#     # Set up the figure
#     fig = plt.figure(figsize=figsize)
#     grid = plt.GridSpec(8, 6, hspace=0.05, wspace=0)
    
#     # Configure panel dimensions and plot the technical indicators on the sub panel
#     indicators = 0
#     if macd:
#         indicators += 1
#     if rsi:
#         indicators += 1
#     if atr:
#         indicators += 1
    
#     if indicators >= 2:
#         main_panel = fig.add_subplot(grid[:-4, :], xticklabels=[])
#         sub_panel_1 = fig.add_subplot(grid[-4:-2, :], xticklabels=[])
#         sub_panel_2 = fig.add_subplot(grid[-2:, :])
        
#         if macd:
#             sub_panel_1.plot(df_select.MACD, color="slateblue", label="MACD(12, 26)", linewidth=1.5, zorder=2)
#             sub_panel_1.plot(df_select.MACD_Sig, color="darkorange", label="Signal(9)", linewidth=1.5, zorder=1)
#             sub_panel_1.bar(x=df_select.index, height=df_select.MACD_Hist,
#                             color=(df_select.MACD_Hist>0).map({True: "lightseagreen", False: "lightcoral"}), zorder=0)
#             sub_panel_1.legend(loc="upper left", prop={"size": 11, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)
            
#             if rsi:
#                 sub_panel_2.plot(df_select.RSI, color="purple", label="RSI(14)", linewidth=1.5)
#                 sub_panel_2.fill_between(x=df_select.index, y1=70, y2=30, color="purple", alpha=0.1)
            
#             elif atr:
#                 sub_panel_2.plot(df_select.ATR, color="slateblue", label="ATR(14)", linewidth=1.5)
            
#             sub_panel_2.legend(loc="upper left", prop={"size": 11, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)
        
#         elif rsi:
#             sub_panel_1.plot(df_select.RSI, color="purple", label="RSI(14)", linewidth=1.5)
#             sub_panel_1.fill_between(x=df_select.index, y1=70, y2=30, color="purple", alpha=0.1)
#             sub_panel_1.legend(loc="upper left", prop={"size": 11, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)  
            
#             if atr:
#                 sub_panel_2.plot(df_select.ATR, color="slateblue", label="ATR(14)", linewidth=1.5)
#                 sub_panel_2.legend(loc="upper left", prop={"size": 11, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)
    
#     elif indicators == 1:
#         main_panel = fig.add_subplot(grid[:-2, :], xticklabels=[])
#         sub_panel_1 = fig.add_subplot(grid[-2:, :], xticklabels=[])
        
#         if macd:
#             sub_panel_1.plot(df_select.MACD, color="slateblue", label="MACD(12, 26)", linewidth=1.5, zorder=2)
#             sub_panel_1.plot(df_select.MACD_Sig, color="darkorange", label="Signal(9)", linewidth=1.5, zorder=1)
#             sub_panel_1.bar(x=df_select.index, height=df_select.MACD_Hist,
#                             color=(df_select.MACD_Hist>0).map({True: "lightseagreen", False: "lightcoral"}), zorder=0)
#             sub_panel_1.legend(loc="upper left", prop={"size": 11, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)
        
#         elif rsi:
#             sub_panel_1.plot(df_select.RSI, color="purple", label="RSI(14)", linewidth=1.5)
#             sub_panel_1.fill_between(x=df_select.index, y1=70, y2=30, color="purple", alpha=0.1)
            
#         elif atr:
#             sub_panel_1.plot(df_select.ATR, color="slateblue", label="ATR(14)", linewidth=1.5)
        
#         sub_panel_1.legend(loc="upper left", prop={"size": 11, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)

    
#     else:
#         main_panel = fig.add_subplot(grid[:, :], xticklabels=[])
     
#     # Get the main colour according to the general trend of the selected time range
#     if df_select.dropna()["Close"].iloc[-1] > df_select.dropna()["Close"].iloc[0] :
#         colour = "lightseagreen"
#     else:
#         colour = "lightcoral"
    
#     # Plot on the main panel of either "line" or "candlestick" style
#     if style == "line":
#         close = main_panel.plot(df_select.Close, color=colour, linewidth=2.5, label="Close", zorder=3)
#         w = close
#     elif style in ["candlestick", "candle"]:
#         df_select["candle_height"] = df_select.Close - df_select.Open
#         candle_chart = main_panel.bar(x=df_select.index, height = df_select.candle_height.abs(), bottom = df_select[["Open", "Close"]].min(axis=1),
#                        yerr=[df_select[["Open", "Close"]].max(axis=1)-df_select["Low"],df_select["High"]-df_select[["Open", "Close"]].max(axis=1)], 
#                        color = ['lightseagreen' if i>=0 else 'lightcoral' for i in df_select['candle_height']],
#                        ecolor= ['lightseagreen' if i>=0 else 'lightcoral' for i in df_select['candle_height']], 
#                        width=0.8, label="OHLC", alpha=1, error_kw={'alpha':0.8}, zorder=3)
#         w = [candle_chart]
    
#     # Plot the benchmark cumulative returns scaled to the selected security at the beginning of the period
#     if benchmark:
#         b = main_panel.plot(df_select[benchmark], color="black", linestyle="solid", linewidth=2, label=benchmark, zorder=2)
#         w.append(b[0])
    
#     # Plot the moving averages on the main panel
#     if sma:
#         if type(sma) == bool:
#             line = main_panel.plot(df_select.SMA, color="orange", linewidth=1.5, label="SMA(10)", zorder=2)
#             w.append(line[0])
#         elif type(sma) in (int, float):
#             line = main_panel.plot(df_select.SMA, color=["orange" if int(sma)<=20 else "saddlebrown"][0], linewidth=1.5, label=f"SMA({int(sma):d})", zorder=2)
#             w.append(line[0])
#         elif type(sma) in (tuple, list):
#             periods = np.sort([i for i in sma])
#             if len(periods) == 1:
#                 line = main_panel.plot(df_select.SMA, color=["orange" if int(periods[0])<=20 else "saddlebrown"][0], linewidth=1.5, label=f"SMA({int(periods[0]):d})", zorder=2)
#                 w.append(line[0])
#             elif len(periods) == 2:
#                 line1 = main_panel.plot(df_select["SMA1"], color="orange", linewidth=1.5, label=f"SMA({int(periods[0]):d})", zorder=2)
#                 line2 = main_panel.plot(df_select["SMA2"], color="saddlebrown", linewidth=1.5, label=f"SMA({int(periods[1]):d})", zorder=2)
#                 w.extend([line1[0], line2[0]])
#             else:
#                 line1 = main_panel.plot(df_select["SMA1"], color="orange", linewidth=1.5, label=f"SMA({int(periods[0]):d})", zorder=2)
#                 line2 = main_panel.plot(df_select["SMA2"], color="chocolate", linewidth=1.5, label=f"SMA({int(periods[1]):d})", zorder=2)
#                 line3 = main_panel.plot(df_select["SMA3"], color="saddlebrown", linewidth=1.5, label=f"SMA({int(periods[-1]):d})", zorder=2)
#                 w.extend([line1[0], line2[0], line3[0]])
#     if ema:
#         if type(ema) == bool:
#             line = main_panel.plot(df_select.EMA, color="orange", linewidth=1.5, label="EMA(10)", zorder=2)
#             w.append(line[0])
#         elif type(ema) in (int, float):
#             line = main_panel.plot(df_select.EMA, color=["orange" if int(sma)<=20 else "saddlebrown"][0], linewidth=1.5, label=f"EMA({int(ema):d})", zorder=2)
#             w.append(line[0])
#         elif type(ema) in (tuple, list):
#             periods = np.sort([i for i in ema])
#             if len(periods) == 1:
#                 line = main_panel.plot(df_select.EMA, color=["orange" if int(periods[0])<=20 else "saddlebrown"][0], linewidth=1.5, label=f"EMA({int(periods[0]):d})", zorder=2)
#                 w.append(line[0])
#             elif len(periods) == 2:
#                 line1 = main_panel.plot(df_select["EMA1"], color="orange", linewidth=1.5, label=f"EMA({int(periods[0]):d})", zorder=2)
#                 line2 = main_panel.plot(df_select["EMA2"], color="saddlebrown", linewidth=1.5, label=f"EMA({int(periods[1]):d})", zorder=2)
#                 w.extend([line1[0], line2[0]])
#             else:
#                 line1 = main_panel.plot(df_select["EMA1"], color="orange", linewidth=1.5, label=f"EMA({int(periods[0]):d})", zorder=2)
#                 line2 = main_panel.plot(df_select["EMA2"], color="chocolate", linewidth=1.5, label=f"EMA({int(periods[1]):d})", zorder=2)
#                 line3 = main_panel.plot(df_select["EMA3"], color="saddlebrown", linewidth=1.5, label=f"EMA({int(periods[-1]):d})", zorder=2)
#                 w.extend([line1[0], line2[0], line3[0]])

#     # Plot Bollinger Bands and Volume as overlays on the main panel
#     if bollinger_bands:
#         bb_mid = main_panel.plot(df_select.BB_Mid, linewidth=1.5, color="darkorange", label="SMA(20)", zorder=2)
#         bb_up = main_panel.plot(df_select.BB_Up, linewidth=1.5, color="gold", zorder=2)
#         bb_low = main_panel.plot(df_select.BB_Low, linewidth=1.5, color="gold", zorder=2)
#         bb_fill = main_panel.fill_between(x=df_select.index, y1=df_select.BB_Up, y2=df_select.BB_Low, color="gold", alpha=0.2, label="BBand(20)", zorder=1)
#         w.append(bb_mid[0])
#         w.append(bb_fill)
        
#     if volume:
#         volume_panel = main_panel.twinx()
#         volume = volume_panel.bar(x=df_select.index, height=df_select.Volume, color=colour, label="Volume")
#         volume_panel.set_ylim(0, df_select.Volume.max()*3)
#         volume_panel.patch.set_visible(True)
#         volume_panel.set_xticklabels([])
#         main_panel.set_zorder(1)
#         volume_panel.grid(False)
#         main_panel.patch.set_visible(False)
#         w.append(volume)

#     # Adjust the legend and title of the main panel 
#     main_panel.legend(w, [l.get_label() for l in w], loc="upper left", prop={"size": 11, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)
#     main_panel.set_title(title)
#     plt.show()

# def plot_acf_pacf(ts, acf_lags=None, pacf_lags=None, acf_alpha=0.05, pacf_alpha=0.05, title="Autocorrelation", figsize=(16, 9), **kwargs):
#     """Plot the ACF and PACF of a time series"""
#     fig, axes = plt.subplots(2, 1, figsize=figsize)
#     ts.pipe(plot_acf, ax=axes[0], lags=acf_lags, alpha=acf_alpha, **kwargs)
#     ts.pipe(plot_pacf, ax=axes[1], lags=pacf_lags, alpha=pacf_alpha, **kwargs)
#     axes[0].set_title(title)
#     plt.tight_layout()
#     plt.show()

# def plot_decompose(ts, period=30, model="additive", title="Seasonal Decomposition", figsize=(16, 9), **kwargs):
#     """Plot seasonal decomposition of a series"""
#     ts_decomp = seasonal_decompose(ts, model=model, period=period, **kwargs)
    
#     fig, axes = plt.subplots(4, 1, sharex=True, figsize=figsize)
#     ts_decomp.observed.plot(ax=axes[0])
#     axes[0].set(title=title, ylabel="Observed")
#     axes[0].tick_params(labelsize=12)
#     ts_decomp.trend.plot(ax=axes[1])
#     axes[1].set(ylabel="Trend")
#     axes[1].tick_params(labelsize=12)
#     ts_decomp.seasonal.plot(ax=axes[2])
#     axes[2].set(ylabel="Seasonal")
#     axes[2].tick_params(labelsize=12)
#     ts_decomp.resid.plot(ax=axes[3])
#     axes[3].set(ylabel="Residual")
#     axes[3].tick_params(labelsize=12)
#     plt.xlabel("")
    
#     plt.tight_layout()
#     plt.show()

