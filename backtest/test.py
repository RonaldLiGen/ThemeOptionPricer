# import numpy as np
# import pandas as pd
# from statsmodels.tsa.stattools import adfuller, kpss

# def adf_test(ts):
#     """Return an Augmented Dickey-Fuller test report"""
#     indices = ["Augmented Dickey-Fuller statistic", "p-value", "# of lags used", "# of observations used"]
#     adf_val = adfuller(ts, autolag="AIC")
#     critical_val = pd.Series(adf_val[:4], index=indices)
#     for pct, val in adf_val[4].items():
#         critical_val[f"Critical value ({pct})"] = val
#     return critical_val

# def kpss_test(ts, h0_type="c"):
#     """Return a Kwiatkowski-Phillips-chmidt-shin test report"""
#     indices = ["Kwiatkowski-Phillips-chmidt-Shin statistic", "p-value", "# of lags"]
#     kpss_val = kpss(ts, regression=h0_type)
#     critical_val = pd.Series(kpss_val[:3], index=indices)
#     for pct, val in kpss_val[3].items():
#         critical_val[f"Critical value ({pct})"] = val
#     return critical_val