# import numpy as np
# import pandas as pd
# from datetime import datetime
# import matplotlib.pyplot as plt
# import seaborn as sns
# import yfinance as yf
# from empyrical.stats import *
# import empyrical
# import pyfolio as pf
# from .data import *
# from .transform import ROLLVOL, DIFF, ONES
# from .plot import plot_return

# def get_bt_report(returns, benchmark=None, rf=0.0, required_return=None, period="daily", annualization=None):
#     """Create a BT report with metrics from empyrical"""
#     report = {}
#     metrics = ["Start date", "End date", "CAGR", "Cumulative return", "Annual volatility", "Daily 95% VaR", "Max drawdown", 
#                "Sharpe ratio", "Sortino ratio", "Omega ratio", "Calmar ratio", "Tail ratio", "Stability R^2", "Skew", "Extra kurtosis"]
#     factor_returns = None
#     if benchmark:
#         factor_returns= yf.download(benchmark, start=returns.index[0].date(), end=returns.index[-1].date(), auto_adjust=True, progress=False)["Close"].pct_change()
#     if not required_return:
#         required_return = rf
#     if not factor_returns is None:
#         report["Alpha"] = alpha(returns, factor_returns)
#         report["Beta"] = beta(returns, factor_returns)
#         adj_returns = np.asarray(empyrical.stats._adjust_returns(returns, factor_returns * report["Beta"]))
#         metrics.extend(["Alpha", "Beta"])

#     report["Start date"] = returns.dropna().index[0].date()
#     report["End date"] = returns.dropna().index[-1].date()
#     report["CAGR"] = annual_return(returns, period=period, annualization=annualization)
#     report["Cumulative return"] = cum_returns(returns, starting_value=0).iloc[-1]
#     report["Annual volatility"] = annual_volatility(returns, period=period, alpha=2.0, annualization=annualization)
#     report["Daily 95% VaR"] = value_at_risk(returns, cutoff=0.05)
#     report["Max drawdown"] = max_drawdown(returns)
#     report["Sharpe ratio"] = sharpe_ratio(returns, risk_free=rf, period=period, annualization=annualization)
#     report["Sortino ratio"] = sortino_ratio(returns, required_return=required_return, period=period, annualization=annualization)
#     report["Omega ratio"] = omega_ratio(returns, risk_free=rf, required_return=required_return, annualization=252)
#     report["Calmar ratio"] = calmar_ratio(returns, period=period, annualization=annualization) 
#     report["Tail ratio"] = tail_ratio(returns)
#     report["Stability R^2"] = stability_of_timeseries(returns)
#     report["Skew"] = stats.skew(returns)
#     report["Extra kurtosis"] = stats.kurtosis(returns) 
#     return pd.Series(report).reindex(metrics).to_frame(name="Backtest")

# def format_report(row):
#     if row.name in ["CAGR", "Cumulative return", "Annual volatility", "Daily 95% VaR", "Max drawdown", "Alpha", "Beta"]:
#         return ["{:.3%}".format(x) for x in row][0]
#     elif row.name in ["Start date", "End date"]:
#         return row
#     else:
#         return ["{:.2f}".format(x) for x in row][0]

# def get_bt_returns(df_sig, df_return, delay=1, vol_target=0.1, return_sig=True):
#     """Get backtested returns in a DataFrame"""
#     df_bt = df_sig.shift(delay) * df_return
#     vol_scaler = vol_target / df_bt.sum(axis=1).pipe(ROLLVOL, 126).mul(np.sqrt(252))
#     df_sig_scaled = df_sig.mul(vol_scaler, axis=0)
#     df_bt_scaled = df_sig_scaled.shift(delay) * df_return
#     if return_sig:
#         return df_bt_scaled, df_sig_scaled
#     else:
#         return df_bt_scaled

# def bt_fx(df_sig, rf=0.0, delay=1, tc=3*10e-6, benchmark=None, full_start="2000", post_start="2010", end="2017", vol_target=0.1, figsize=(16, 9), output_returns=False, output_post_tc=False):
#     """Backtest FX signal"""
#     # Get BT returns 
#     df_data = load_fx()["FX.RTN"][df_sig.columns]
#     df_bt_scaled, df_sig_scaled = get_bt_returns(df_sig, df_data, delay=delay, vol_target=vol_target, return_sig=True)
#     df_tc = df_sig_scaled.pipe(DIFF).fillna(0).pipe(np.abs).shift(delay).mul(tc)[full_start:end]
#     df_bt_scaled_tc = df_bt_scaled - df_tc

#     # Create BT returns of different lags
#     delays = range(-4, 7)
#     sharpes = [sharpe_ratio(get_bt_returns(df_sig, df_data, delay=d, vol_target=vol_target, return_sig=False).sum(axis=1), risk_free=rf) for d in delays]

#     # Create BT summary report
#     report = get_bt_report(df_bt_scaled[full_start:end].sum(axis=1), benchmark=benchmark, rf=rf).apply(format_report, axis=1)
#     if isinstance(report, pd.Series):
#         report = report.to_frame("Backtest")
#     print(report)

#     # Plot 6-piece summary plot
#     fig, axes = plt.subplots(nrows=2, ncols=3, figsize=figsize)
#     # full period portfolio return
#     plot_bt_return(df_bt_scaled, df_bt_scaled_tc, rf=rf, benchmark=benchmark, start=full_start, end=end, drawdowns=5, ax=axes[0, 0], title="Signal "+full_start+" ~ "+end)
#     # post period portfolio return
#     plot_bt_return(df_bt_scaled, df_bt_scaled_tc, rf=rf, benchmark=benchmark, start=post_start, end=end, drawdowns=3, ax=axes[0, 1], title="Signal "+post_start+" ~ "+end)
#     # asset returns breakdown
#     plot_asset_return(df_bt_scaled, rf=rf, start=full_start, end=end, ax=axes[0, 2], title="Composite Return")
#     # full period drawdown plot
#     plot_bt_drawdown(df_bt_scaled, start=full_start, end=end, ax=axes[1, 0], title="Drawdown")
#     # delayed backtests Sharpe ratio bar plot
#     barlist = axes[1, 1].bar(delays, sharpes, color="coral", alpha=0.7)
#     barlist[4+delay].set_color("darkred")
#     axes[1, 1].set_ylabel("Sharpe ratio", size=9)
#     axes[1, 1].set_xlabel("Delay", size=9)
#     axes[1, 1].set_xticks(delays)
#     axes[1, 1].tick_params(labelsize=9)
#     axes[1, 1].set_title("Delayed Signal", fontsize=19)
#     axes[1, 1].axhline(0.0, color='black', linestyle='-', lw=3)
#     # asset holding heatmap
#     plot_asset_holding(df_sig_scaled, start=full_start, end=end, ax=axes[1, 2], title="Asset Holding")

#     # Output returns if asked
#     if output_returns:
#         if output_post_tc:
#             return df_bt_scaled_tc
#         else:
#             return df_bt_scaled

# def bt_eqix(df_sig, rf=0.0, delay=1, tc=10e-5, benchmark="SPY", full_start="2000", post_start="2010", end="2017", vol_target=0.15, figsize=(16, 9), output_returns=False, output_post_tc=False):
#     """Backtest equity index signal"""
#     # Get BT returns 
#     df_data = load_eqix()["EQIX.RTN"][df_sig.columns]
#     df_bt_scaled, df_sig_scaled = get_bt_returns(df_sig, df_data, delay=delay, vol_target=vol_target, return_sig=True)
#     df_tc = df_sig_scaled.pipe(DIFF).fillna(0).pipe(np.abs).shift(delay).mul(tc)[full_start:end]
#     df_bt_scaled_tc = df_bt_scaled - df_tc

#     # Create BT returns of different lags
#     delays = range(-4, 7)
#     sharpes = [sharpe_ratio(get_bt_returns(df_sig, df_data, delay=d, vol_target=vol_target, return_sig=False).sum(axis=1), risk_free=rf) for d in delays]

#     # Create BT summary report
#     report = get_bt_report(df_bt_scaled[full_start:end].sum(axis=1), benchmark=benchmark, rf=rf).apply(format_report, axis=1)
#     if isinstance(report, pd.Series):
#         report = report.to_frame("Backtest")
#     print(report)

#     # Plot 6-piece summary plot
#     fig, axes = plt.subplots(nrows=2, ncols=3, figsize=figsize)
#     # full period portfolio return
#     plot_bt_return(df_bt_scaled, df_bt_scaled_tc, rf=rf, benchmark=benchmark, start=full_start, end=end, drawdowns=5, ax=axes[0, 0], title="Signal "+full_start+" ~ "+end)
#     # post period portfolio return
#     plot_bt_return(df_bt_scaled, df_bt_scaled_tc, rf=rf, benchmark=benchmark, start=post_start, end=end, drawdowns=3, ax=axes[0, 1], title="Signal "+post_start+" ~ "+end)
#     # asset returns breakdown
#     plot_asset_return(df_bt_scaled, rf=rf, start=full_start, end=end, ax=axes[0, 2], title="Composite Return")
#     # full period drawdown plot
#     plot_bt_drawdown(df_bt_scaled, start=full_start, end=end, ax=axes[1, 0], title="Drawdown")
#     # delayed backtests Sharpe ratio bar plot
#     barlist = axes[1, 1].bar(delays, sharpes, color="coral", alpha=0.7)
#     barlist[4+delay].set_color("darkred")
#     axes[1, 1].set_ylabel("Sharpe ratio", size=9)
#     axes[1, 1].set_xlabel("Delay", size=9)
#     axes[1, 1].set_xticks(delays)
#     axes[1, 1].tick_params(labelsize=9)
#     axes[1, 1].set_title("Delayed Signal", fontsize=19)
#     axes[1, 1].axhline(0.0, color='black', linestyle='-', lw=3)
#     # asset holding heatmap
#     plot_asset_holding(df_sig_scaled, start=full_start, end=end, ax=axes[1, 2], title="Asset Holding")

#     # Output returns if asked
#     if output_returns:
#         if output_post_tc:
#             return df_bt_scaled_tc
#         else:
#             return df_bt_scaled

# def bt_useq(df_sig, rf=0.0, delay=1, tc=10e-5, benchmark="SPY", full_start="2000", post_start="2010", end="2017", vol_target=0.15, figsize=(16, 9), output_returns=False, output_post_tc=False):
#     """Backtest US equity signal"""
#     # Get BT returns 
#     df_data = load_useq()["USEQ.RTN"][df_sig.columns]
#     df_bt_scaled, df_sig_scaled = get_bt_returns(df_sig, df_data, delay=delay, vol_target=vol_target, return_sig=True)
#     df_tc = df_sig_scaled.pipe(DIFF).fillna(0).pipe(np.abs).shift(delay).mul(tc)[full_start:end]
#     df_bt_scaled_tc = df_bt_scaled - df_tc

#     # Create BT returns of different lags
#     delays = range(-4, 7)
#     sharpes = [sharpe_ratio(get_bt_returns(df_sig, df_data, delay=d, vol_target=vol_target, return_sig=False).sum(axis=1), risk_free=rf) for d in delays]

#     # Create BT summary report
#     report = get_bt_report(df_bt_scaled[full_start:end].sum(axis=1), benchmark=benchmark, rf=rf).apply(format_report, axis=1)
#     if isinstance(report, pd.Series):
#         report = report.to_frame("Backtest")
#     print(report)

#     # Plot 6-piece summary plot
#     fig, axes = plt.subplots(nrows=2, ncols=3, figsize=figsize)
#     # full period portfolio return
#     plot_bt_return(df_bt_scaled, df_bt_scaled_tc, rf=rf, benchmark=benchmark, start=full_start, end=end, drawdowns=5, ax=axes[0, 0], title="Signal "+full_start+" ~ "+end)
#     # post period portfolio return
#     plot_bt_return(df_bt_scaled, df_bt_scaled_tc, rf=rf, benchmark=benchmark, start=post_start, end=end, drawdowns=3, ax=axes[0, 1], title="Signal "+post_start+" ~ "+end)
#     # asset returns breakdown
#     plot_asset_return(df_bt_scaled, rf=rf, start=full_start, end=end, ax=axes[0, 2], title="Composite Return")
#     # full period drawdown plot
#     plot_bt_drawdown(df_bt_scaled, start=full_start, end=end, ax=axes[1, 0], title="Drawdown")
#     # delayed backtests Sharpe ratio bar plot
# #     barlist = axes[1, 1].bar(delays, sharpes, color="coral", alpha=0.7)
# #     barlist[4+delay].set_color("darkred")
#     axes[1, 1].set_ylabel("Sharpe ratio", size=9)
#     axes[1, 1].set_xlabel("Delay", size=9)
#     axes[1, 1].set_xticks(delays)
#     axes[1, 1].tick_params(labelsize=9)
#     axes[1, 1].set_title("Delayed Signal", fontsize=19)
#     axes[1, 1].axhline(0.0, color='black', linestyle='-', lw=3)
#     if len(df_sig_scaled.columns) <= 30:
#         # asset holding heatmap
#         plot_asset_holding(df_sig_scaled, start=full_start, end=end, ax=axes[1, 2], title="Asset Holding")
#     else:
#         # rolling volatility
#         plot_rolling_vol(df_sig_scaled, start=full_start, end=end, ax=axes[1, 2], title="6M Rolling Volatility")

#     # Output returns if asked
#     if output_returns:
#         if output_post_tc:
#             return df_bt_scaled_tc
#         else:
#             return df_bt_scaled

# def bt_etf(df_sig, rf=0.0, delay=1, tc=10e-5, benchmark="SPY", full_start="2000", post_start="2010", end="2017", vol_target=0.15, figsize=(16, 9), output_returns=False, output_post_tc=False):
#     """Backtest US equity signal"""
#     # Get BT returns 
#     df_data = load_etf()["ETF.RTN"][df_sig.columns]
#     df_bt_scaled, df_sig_scaled = get_bt_returns(df_sig, df_data, delay=delay, vol_target=vol_target, return_sig=True)
#     df_tc = df_sig_scaled.pipe(DIFF).fillna(0).pipe(np.abs).shift(delay).mul(tc)[full_start:end]
#     df_bt_scaled_tc = df_bt_scaled - df_tc

#     # Create BT returns of different lags
#     delays = range(-4, 7)
#     sharpes = [sharpe_ratio(get_bt_returns(df_sig, df_data, delay=d, vol_target=vol_target, return_sig=False).sum(axis=1), risk_free=rf) for d in delays]

#     # Create BT summary report
#     report = get_bt_report(df_bt_scaled[full_start:end].sum(axis=1), benchmark=benchmark, rf=rf).apply(format_report, axis=1)
#     if isinstance(report, pd.Series):
#         report = report.to_frame("Backtest")
#     print(report)

#     # Plot 6-piece summary plot
#     fig, axes = plt.subplots(nrows=2, ncols=3, figsize=figsize)
#     # full period portfolio return
#     plot_bt_return(df_bt_scaled, df_bt_scaled_tc, rf=rf, benchmark=benchmark, start=full_start, end=end, drawdowns=5, ax=axes[0, 0], title="Signal "+full_start+" ~ "+end)
#     # post period portfolio return
#     plot_bt_return(df_bt_scaled, df_bt_scaled_tc, rf=rf, benchmark=benchmark, start=post_start, end=end, drawdowns=3, ax=axes[0, 1], title="Signal "+post_start+" ~ "+end)
#     # asset returns breakdown
#     plot_asset_return(df_bt_scaled, rf=rf, start=full_start, end=end, ax=axes[0, 2], title="Composite Return")
#     # full period drawdown plot
#     plot_bt_drawdown(df_bt_scaled, start=full_start, end=end, ax=axes[1, 0], title="Drawdown")
#     # delayed backtests Sharpe ratio bar plot
#     barlist = axes[1, 1].bar(delays, sharpes, color="coral", alpha=0.7)
#     barlist[4+delay].set_color("darkred")
#     axes[1, 1].set_ylabel("Sharpe ratio", size=9)
#     axes[1, 1].set_xlabel("Delay", size=9)
#     axes[1, 1].set_xticks(delays)
#     axes[1, 1].tick_params(labelsize=9)
#     axes[1, 1].set_title("Delayed Signal", fontsize=19)
#     axes[1, 1].axhline(0.0, color='black', linestyle='-', lw=3)
#     if len(df_sig_scaled.columns) <= 30:
#         # asset holding heatmap
#         plot_asset_holding(df_sig_scaled, start=full_start, end=end, ax=axes[1, 2], title="Asset Holding")
#     else:
#         # rolling volatility
#         plot_rolling_vol(df_sig_scaled, start=full_start, end=end, ax=axes[1, 2], title="6M Rolling Volatility")

#     # Output returns if asked
#     if output_returns:
#         if output_post_tc:
#             return df_bt_scaled_tc
#         else:
#             return df_bt_scaled

# def bt_comdty(df_sig, rf=0.0, delay=1, tc=10e-5, benchmark=None, full_start="2000", post_start="2010", end="2017", vol_target=0.15, figsize=(16, 9), output_returns=False, output_post_tc=False):
#     """Backtest commodity futures signal"""
#     # Get BT returns 
#     df_data = load_comdty()["COMDTY.RTN"][df_sig.columns]
#     df_bt_scaled, df_sig_scaled = get_bt_returns(df_sig, df_data, delay=delay, vol_target=vol_target, return_sig=True)
#     df_tc = df_sig_scaled.pipe(DIFF).fillna(0).pipe(np.abs).shift(delay).mul(tc)[full_start:end]
#     df_bt_scaled_tc = df_bt_scaled - df_tc

#     # Create BT returns of different lags
#     delays = range(-4, 7)
#     sharpes = [sharpe_ratio(get_bt_returns(df_sig, df_data, delay=d, vol_target=vol_target, return_sig=False).sum(axis=1), risk_free=rf) for d in delays]

#     # Create BT summary report
#     report = get_bt_report(df_bt_scaled[full_start:end].sum(axis=1), benchmark=benchmark, rf=rf).apply(format_report, axis=1)
#     if isinstance(report, pd.Series):
#         report = report.to_frame("Backtest")
#     print(report)

#     # Plot 6-piece summary plot
#     fig, axes = plt.subplots(nrows=2, ncols=3, figsize=figsize)
#     # full period portfolio return
#     plot_bt_return(df_bt_scaled, df_bt_scaled_tc, rf=rf, benchmark=benchmark, start=full_start, end=end, drawdowns=5, ax=axes[0, 0], title="Signal "+full_start+" ~ "+end)
#     # post period portfolio return
#     plot_bt_return(df_bt_scaled, df_bt_scaled_tc, rf=rf, benchmark=benchmark, start=post_start, end=end, drawdowns=3, ax=axes[0, 1], title="Signal "+post_start+" ~ "+end)
#     # asset returns breakdown
#     plot_asset_return(df_bt_scaled, rf=rf, start=full_start, end=end, ax=axes[0, 2], title="Composite Return")
#     # full period drawdown plot
#     plot_bt_drawdown(df_bt_scaled, start=full_start, end=end, ax=axes[1, 0], title="Drawdown")
#     # delayed backtests Sharpe ratio bar plot
#     barlist = axes[1, 1].bar(delays, sharpes, color="coral", alpha=0.7)
#     barlist[4+delay].set_color("darkred")
#     axes[1, 1].set_ylabel("Sharpe ratio", size=9)
#     axes[1, 1].set_xlabel("Delay", size=9)
#     axes[1, 1].set_xticks(delays)
#     axes[1, 1].tick_params(labelsize=9)
#     axes[1, 1].set_title("Delayed Signal", fontsize=19)
#     axes[1, 1].axhline(0.0, color='black', linestyle='-', lw=3)
#     if len(df_sig_scaled.columns) <= 30:
#         # asset holding heatmap
#         plot_asset_holding(df_sig_scaled, start=full_start, end=end, ax=axes[1, 2], title="Asset Holding")
#     else:
#         # rolling volatility
#         plot_rolling_vol(df_sig_scaled, start=full_start, end=end, ax=axes[1, 2], title="6M Rolling Volatility")

#     # Output returns if asked
#     if output_returns:
#         if output_post_tc:
#             return df_bt_scaled_tc
#         else:
#             return df_bt_scaled

# def bt_asset(df_sig, df_data, rf=0.0, delay=1, tc=10e-5, benchmark=None, full_start="2000", post_start="2010", end="2017", vol_target=0.15, figsize=(16, 9), output_returns=False, output_post_tc=False):
#     """Backtest signal on cumstom data"""
#     # Get BT returns 
#     df_data = df_data[df_sig.columns]
#     df_bt_scaled, df_sig_scaled = get_bt_returns(df_sig, df_data, delay=delay, vol_target=vol_target, return_sig=True)
#     df_tc = df_sig_scaled.pipe(DIFF).fillna(0).pipe(np.abs).shift(delay).mul(tc)[full_start:end]
#     df_bt_scaled_tc = df_bt_scaled - df_tc

#     # Create BT returns of different lags
#     delays = range(-4, 7)
#     sharpes = [sharpe_ratio(get_bt_returns(df_sig, df_data, delay=d, vol_target=vol_target, return_sig=False).sum(axis=1), risk_free=rf) for d in delays]

#     # Create BT summary report
#     report = get_bt_report(df_bt_scaled[full_start:end].sum(axis=1), benchmark=benchmark, rf=rf).apply(format_report, axis=1)
#     if isinstance(report, pd.Series):
#         report = report.to_frame("Backtest")
#     print(report)

#     # Plot 6-piece summary plot
#     fig, axes = plt.subplots(nrows=2, ncols=3, figsize=figsize)
#     # full period portfolio return
#     plot_bt_return(df_bt_scaled, df_bt_scaled_tc, rf=rf, benchmark=benchmark, start=full_start, end=end, drawdowns=5, ax=axes[0, 0], title="Signal "+full_start+" ~ "+end)
#     # post period portfolio return
#     plot_bt_return(df_bt_scaled, df_bt_scaled_tc, rf=rf, benchmark=benchmark, start=post_start, end=end, drawdowns=3, ax=axes[0, 1], title="Signal "+post_start+" ~ "+end)
#     # asset returns breakdown
#     plot_asset_return(df_bt_scaled, rf=rf, start=full_start, end=end, ax=axes[0, 2], title="Composite Return")
#     # full period drawdown plot
#     plot_bt_drawdown(df_bt_scaled, start=full_start, end=end, ax=axes[1, 0], title="Drawdown")
#     # delayed backtests Sharpe ratio bar plot
#     barlist = axes[1, 1].bar(delays, sharpes, color="coral", alpha=0.7)
#     barlist[4+delay].set_color("darkred")
#     axes[1, 1].set_ylabel("Sharpe ratio", size=9)
#     axes[1, 1].set_xlabel("Delay", size=9)
#     axes[1, 1].set_xticks(delays)
#     axes[1, 1].tick_params(labelsize=9)
#     axes[1, 1].set_title("Delayed Signal", fontsize=19)
#     axes[1, 1].axhline(0.0, color='black', linestyle='-', lw=3)
#     # asset holding heatmap
#     if len(df_sig_scaled.columns) <= 30:
#         # asset holding heatmap
#         plot_asset_holding(df_sig_scaled, start=full_start, end=end, ax=axes[1, 2], title="Asset Holding")
#     else:
#         # rolling volatility
#         plot_rolling_vol(df_sig_scaled, start=full_start, end=end, ax=axes[1, 2], title="6M Rolling Volatility")

#     # Output returns if asked
#     if output_returns:
#         if output_post_tc:
#             return df_bt_scaled_tc
#         else:
#             return df_bt_scaled

# def combine_bt(df_bt, weights=None, names=None, rf=0.0, delay=1, benchmark=None, full_start="2000", post_start="2010", end="2017", vol_target=0.15, figsize=(16, 9), output_returns=False):
#     """Combine multiple backtests"""
#     # Get BT DataFrame
#     if isinstance(df_bt, list):
#         df_bt = pd.concat([bt.sum(axis=1) for bt in df_bt], axis=1)
    
#     if names:
#         df_bt.columns = names

#     # Weighting BTs
#     df_one = df_bt.pipe(ONES)
#     if not weights:
#         weights = df_one
#     elif isinstance(weights, list, np.ndarray, pd.Series, pd.DataFrame):
#         weights = df_one.mul(weights)
#     df_bt_weighted = df_bt.mul(weights)

#     # Scaling combined BT
#     vol_scaler = vol_target / df_bt_weighted.sum(axis=1).pipe(ROLLVOL, 126).mul(np.sqrt(252))
#     df_bt_scaled = df_bt_weighted.mul(vol_scaler.shift(delay), axis=0)

#     # Create combined BT summary report
#     report = get_bt_report(df_bt_scaled[full_start:end].sum(axis=1), benchmark=benchmark, rf=rf).apply(format_report, axis=1)
#     if isinstance(report, pd.Series):
#         report = report.to_frame("Backtest")
#     print(report)

#     # Plot 6-piece summary plot
#     fig, axes = plt.subplots(nrows=2, ncols=3, figsize=figsize)
#     # full period combined signal return
#     plot_bt_return(df_bt_scaled, rf=rf, benchmark=benchmark, start=full_start, end=end, drawdowns=5, ax=axes[0, 0], title="Signal "+full_start+" ~ "+end)
#     # post period combined signal return
#     plot_bt_return(df_bt_scaled, rf=rf, benchmark=benchmark, start=post_start, end=end, drawdowns=3, ax=axes[0, 1], title="Signal "+post_start+" ~ "+end)
#     # composite signal returns breakdown
#     plot_asset_return(df_bt_scaled, rf=rf, start=full_start, end=end, ax=axes[0, 2], title="Composite Signals")
#     # full period drawdown plot
#     plot_bt_drawdown(df_bt_scaled, start=full_start, end=end, ax=axes[1, 0], title="Drawdown")
#     # delayed backtests Sharpe ratio bar plot
#     plot_monthly_return_heatmap(df_bt_scaled, start=full_start, end=end, ax=axes[1, 1])
#     # asset holding heatmap
#     plot_asset_holding(weights, start=full_start, end=end, ax=axes[1, 2], title="Signal Weight")

#     # Output returns if asked
#     if output_returns:
#         return df_bt_scaled

# def plot_bt_return(df_bt, df_bt_tc=None, rf=0.0, benchmark=None, start="2000", end="2017", ax=None, title="Signal Return", drawdowns=5, figsize=(16, 9), **kwargs):
#     """Plot backtest portfolio return over time with top drawdowns"""  
#     df_bt = df_bt.sum(axis=1).to_frame(name="Signal")
#     if not df_bt_tc is None:
#         df_bt["Post-TC"] = df_bt_tc.sum(axis=1)
#     ax = df_bt.pipe(plot_return, benchmark=benchmark, rf=rf, start=start, end=end, ax=ax, title=title, sort_legends=False, **kwargs)
    
# #     if drawdowns:
# #         df_drawdowns = pf.timeseries.gen_drawdown_table(df_bt[start:end].sum(axis=1), top=drawdowns)
# #         lim = ax.get_ylim()
# #         colors = sns.cubehelix_palette(len(df_drawdowns))[::-1]
# #         for i, (peak, recovery) in df_drawdowns[
# #                 ['Peak date', 'Recovery date']].iterrows():
# #             if pd.isnull(recovery):
# #                 recovery = df_bt.index[-1]
# #             ax.fill_between((peak, recovery),
# #                             lim[0],
# #                             lim[1],
# #                             alpha=.4,
# #                             color=colors[i])
#     end = datetime(pd.to_datetime(end).year+1, 1, 1)
#     ax.set_xlim(start, end)
#     ax.tick_params(axis="x", rotation=0)
#     return ax

# def plot_asset_return(df_bt, rf=0.0, start="2000", end="2017", signal=False, ax=None, title="Asset Return", figsize=(16, 9), **kwargs):
#     """Plot backtest asset return breakdown over time"""
#     df_return = df_bt.copy()
#     if signal:
#         df_return["Signal"] = df_return.sum(axis=1)
#         ax = df_return.pipe(plot_return, rf=rf, start=start, end=end, benchmark="Signal", ax=ax, title=title, sort_legends=True, **kwargs)
#     else:
#         ax = df_return.pipe(plot_return, rf=rf, start=start, end=end, ax=ax, title=title, sort_legends=True, **kwargs)
#     end = datetime(pd.to_datetime(end).year+1, 1, 1)
#     ax.set_xlim(start, end)
#     ax.tick_params(axis="x", rotation=0)
#     return ax

# def plot_asset_holding(df_sig, start="2000", end="2017", ax=None, title="Asset Holding", figsize=(16, 9), cbar=False, **kwargs):
#     """Plot backtest asset holding weights with pyfolio"""
#     if not ax:
#         fig, ax = plt.subplots(1, figsize=figsize)
#         fontsize = 12
#     else:
#         fontsize=9

#     if isinstance(df_sig, pd.Series):
#         df_sig = df_sig.to_frame()

#     # Slice the desirable time range
#     df_full = df_sig.copy()
#     df_select = df_full[start:end]
#     df_select = df_select.fillna(0)
#     if len(df_select.columns) > 15:
#         df_select.iloc[:, :15]
#     sns.heatmap(df_select.T, ax=ax, center=0, cmap=sns.diverging_palette(0, 100, s=100, l=15, as_cmap=True), cbar=cbar, **kwargs)
#     dates = df_select.index.strftime("%Y").unique()
#     xlen = ax.get_xticks()[-1]
#     ax.set_yticks(np.arange(len(df_select.columns))+0.5)
#     ax.set_yticklabels(df_select.columns)
#     ax.set_xticks(np.arange(xlen/len(dates), xlen+xlen/len(dates), step=xlen/len(dates)))
#     ax.set_xticklabels(dates)
#     ax.tick_params(labelsize=fontsize)
#     ax.set_xlabel("")
#     ax.set_title(title, size=fontsize+10)
#     return ax

# def plot_bt_drawdown(df_bt, start="2000", end="2017", ax=None, title="Signal Drawdown", figsize=(16, 9), **kwargs):
#     """Plot backtest portfolio return over time with pyfolio"""
#     if not ax:
#         fig, ax = plt.subplots(1, figsize=figsize)
#         fontsize = 12
#     else:
#         fontsize=9

#     # Slice the desirable time range
#     df_full = df_bt.copy()
#     df_select = df_full[start:end]
#     df_select.sum(axis=1).pipe(pf.plot_drawdown_underwater, ax=ax, **kwargs)
#     ax.tick_params(labelsize=fontsize)
#     ax.set_title(title, size=fontsize+10)
#     ax.set_ylabel("")
#     end = datetime(pd.to_datetime(end).year+1, 1, 1)
#     ax.set_xlim(start, end)
#     ax.tick_params(axis="x", rotation=0)
#     return ax

# def plot_rolling_vol(df_bt, benchmark=None, start="2000", end="2017", ax=None, window=126, title="6M Rolling Vol", figsize=(16, 9), **kwargs):
#     """Plot backtest portfolio rolling volatility with pyfolio"""
#     if not ax:
#         fig, ax = plt.subplots(1, figsize=figsize)
#         fontsize = 12
#     else:
#         fontsize=9

#     # Slice the desirable time range
#     df_full = df_bt.copy()
#     df_select = df_full[start:end].sum(axis=1).to_frame(name="Signal")
#     if benchmark:
#         df_select[benchmark] = yf.download(benchmark, start=df_full.index[0].date(), end=df_full.index[-1].date(), auto_adjust=True, progress=False)["Close"].pct_change()
#         df_select.iloc[0] = 0
#         pf.plot_rolling_volatility(df_select["Signal"], df_select[benchmark], rolling_window=window, ax=ax, **kwargs)
#     else:
#         pf.plot_rolling_volatility(df_select["Signal"], rolling_window=window, ax=ax, **kwargs)
#     ax.tick_params(labelsize=fontsize)
#     vals = ax.get_yticks()
#     ax.set_yticklabels(['{:,.2%}'.format(x) for x in vals], fontsize=fontsize)
#     ax.set_ylabel("")
#     ax.legend(loc="upper left", prop={"size": fontsize, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)
#     ax.set_title(title, size=fontsize+10)
#     end = datetime(pd.to_datetime(end).year+1, 1, 1)
#     ax.set_xlim(start, end)
#     ax.tick_params(axis="x", rotation=0)
#     return ax

# def plot_rolling_sharpe(df_bt, benchmark=None, start="2000", end="2017", ax=None, window=126, title="6M Rolling Sharpe Ratio", figsize=(16, 9), **kwargs):
#     """Plot backtest portfolio rolling Sharpe ratio with pyfolio"""
#     if not ax:
#         fig, ax = plt.subplots(1, figsize=figsize)
#         fontsize = 12
#     else:
#         fontsize=9

#     # Slice the desirable time range
#     df_full = df_bt.copy()
#     df_select = df_full[start:end].sum(axis=1).to_frame(name="Signal")
#     if benchmark:
#         df_select[benchmark] = yf.download(benchmark, start=df_full.index[0].date(), end=df_full.index[-1].date(), auto_adjust=True, progress=False)["Close"].pct_change()
#         df_select.iloc[0] = 0
#         pf.plot_rolling_sharpe(df_select["Signal"], df_select[benchmark], rolling_window=window, ax=ax, **kwargs)
#     else:
#         pf.plot_rolling_sharpe(df_select["Signal"], rolling_window=window, ax=ax, **kwargs)
#     ax.tick_params(labelsize=fontsize)
#     vals = ax.get_yticks()
#     ax.set_yticklabels(['{:,.2%}'.format(x) for x in vals], fontsize=fontsize)
#     ax.set_ylabel("")
#     ax.legend(loc="upper left", prop={"size": fontsize, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)
#     ax.set_title(title, size=fontsize+10)
#     end = datetime(pd.to_datetime(end).year+1, 1, 1)
#     ax.set_xlim(start, end)
#     ax.tick_params(axis="x", rotation=0)
#     return ax

# def plot_monthly_return_heatmap(df_bt, start="2000", end="2017", ax=None, title="Monthly Return (%)", figsize=(8, 8), **kwargs):
#     """Plot montly returns heatmap"""
#     if not ax:
#         fig, ax = plt.subplots(1, figsize=figsize)
#         fontsize = 12
#     else:
#         fontsize=9

#     # Slice the desirable time range
#     df_full = df_bt.copy()
#     df_select = df_full[start:end].sum(axis=1)
#     monthly_ret_table = empyrical.aggregate_returns(df_select, 'monthly')
#     monthly_ret_table = monthly_ret_table.unstack().round(3)

#     sns.heatmap(
#         monthly_ret_table.fillna(0) * 100.0,
#         annot=True,
#         annot_kws={"size": 9},
#         alpha=1.0,
#         center=0.0,
#         cbar=False,
#         cmap=sns.diverging_palette(0, 100, s=100, l=15, as_cmap=True),
#         ax=ax, **kwargs)
    
#     ax.set_ylabel('Year', size=fontsize)
#     ax.set_xlabel('Month', size=fontsize)
#     ax.tick_params(labelsize=fontsize)
#     ax.yaxis.set_tick_params(rotation=0)
#     ax.set_title(title, size=fontsize+10)
#     return ax

# def plot_annual_return(df_bt, start="2000", end="2017", ax=None, title="Annual Return (%)", figsize=(16, 9), **kwargs):
#     """Plot montly returns heatmap"""
#     if not ax:
#         fig, ax = plt.subplots(1, figsize=figsize)
#         fontsize = 12
#     else:
#         fontsize=9

#     # Slice the desirable time range
#     df_full = df_bt.copy()
#     df_select = df_full[start:end].sum(axis=1)

#     ann_ret_df = pd.DataFrame(
#         empyrical.aggregate_returns(
#             df_select,
#             'yearly'))

#     ax.axvline(
#         100 *
#         ann_ret_df.values.mean(),
#         color='steelblue',
#         linestyle='--',
#         lw=4,
#         alpha=0.7)
#     ann_ret_df.sort_index(ascending=False).plot(ax=ax, kind='barh', alpha=0.70, color="coral", **kwargs)
#     ax.axvline(0.0, color='black', linestyle='-', lw=3)

#     vals = ax.get_xticks()
#     ax.set_xticklabels(['{:,.0%}'.format(x) for x in vals], fontsize=fontsize)
#     ax.set_ylabel('Year', size=fontsize)
#     ax.set_xlabel("")
#     ax.tick_params(labelsize=fontsize)
#     ax.yaxis.set_tick_params(rotation=0)
#     ax.set_title(title, size=fontsize+10)
#     ax.legend(loc="upper left", prop={"size": fontsize, "family": "Consolas"}, frameon=True, fancybox=True, framealpha=1, shadow=True, borderpad=0.5)
#     return ax