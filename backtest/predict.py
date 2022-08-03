# import numpy as np
# import pandas as pd
# from statsmodels.tsa.holtwinters import ExponentialSmoothing
# from pmdarima import auto_arima, ARIMA as arima
# from pmdarima.arima import ndiffs
# from tqdm import tqdm


# def ETS(df, window=252, expanding=True, trend="add", damped=False, damping_slope=None, seasonal=None, seasonal_periods=None, name="Forecast"):
#     """Map the Holt-Winterse ETS model to a rolling DataFrame"""
#     tqdm.pandas()
#     if isinstance(df, pd.Series):
#         df = df.to_frame(name=name)

#     if not expanding:
#         if not damping_slope:
#             return df.interpolate(method="linear", axis=0).rolling(window)\
#                 .progress_apply(lambda ts: ExponentialSmoothing(ts, trend=trend, damped=damped, seasonal=seasonal, seasonal_periods=seasonal_periods).fit().forecast(1))
#         else:
#             return df.interpolate(method="linear", axis=0).rolling(window)\
#                 .progress_apply(lambda ts: ExponentialSmoothing(ts, trend=trend, damped=True, seasonal=seasonal, seasonal_periods=seasonal_periods).fit(damping_slope=damping_slope).forecast(1))
#     else:
#         if not damping_slope:
#             return df.interpolate(method="linear", axis=0).expanding(min_periods=window)\
#                 .progress_apply(lambda ts: ExponentialSmoothing(ts, trend=trend, damped=damped, seasonal=seasonal, seasonal_periods=seasonal_periods).fit().forecast(1))
#         else:
#             return df.interpolate(method="linear", axis=0).rolling(min_periods=window)\
#                 .progress_apply(lambda ts: ExponentialSmoothing(ts, trend=trend, damped=True, seasonal=seasonal, seasonal_periods=seasonal_periods).fit(damping_slope=damping_slope).forecast(1))

# def ARIMA(df, window=252, expanding=True, order=None, seasonal=False, seasonal_order=None, trace=False):
#     """Map the ARIMA model to a rolling DataFrame"""
#     tqdm.pandas()
#     if isinstance(df, pd.Series):
#         df = df.to_frame()

#     if order: # ARIMA with specific parameters
#         df_filled = df.loc[df.first_valid_index():].interpolate(method="linear", axis=0)
#         def ts_predict(ts):
#             model = arima(order=order, seasonal_order=seasonal_order)
#             model.fit(df_filled[:window])
#             def update(x):
#                 value = model.predict(n_periods=1, return_conf_int=False)[0]
#                 model.update(x)
#                 return value
#             return ts.iloc[window:].progress_apply(lambda x: update(x))
#         return df_filled.apply(lambda ts: ts_predict(ts))
#     else:     # Auto-ARIMA
#         df_filled = df.loc[df.first_valid_index():].interpolate(method="linear", axis=0)
#         def ts_predict(ts):
#             kpss_diffs = ndiffs(ts.iloc[:window], alpha=0.05, test="kpss", max_d=6)
#             adf_diffs = ndiffs(ts.iloc[:window], alpha=0.05, test="adf", max_d=6)
#             n_diffs = max(kpss_diffs, adf_diffs)
#             model = auto_arima(ts, d=n_diffs, seasonal=seasonal, stepwise=True, supress_warnings=True, error_action="ignore")
#             def update(x):
#                 value = model.predict(n_periods=1, return_conf_int=False)[0]
#                 model.update(x)
#                 return value
#             return ts.iloc[window:].progress_apply(lambda x: update(x))
#         return df_filled.apply(lambda ts: ts_predict(ts))
