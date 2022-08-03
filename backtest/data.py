# import pkg_resources 
# import pandas as pd

# DM = ["USD", "EUR", "JPY", "GBP", "AUD", "CHF", "CAD", "NZD", "SEK", "NOK", "SGD", "HKD"]
# EM = ["CNY", "MXN", "KRW", "TRY", "INR", "RUB", "BRL", "ZAR", "PLN", "TWD", "THB", "MYR"]
# METAL = ["Gold", "Silver", "Aluminum", "Copper", "Nickel", "Zinc", "Lead", "Tin", "Platinum", "Palladium"]
# ENERGY = ["WTI Crude", "RBOB Gasoline", "Heating Oil", "Natural Gas", "Brent Crude", "Gas Oil"]
# AGRICULTURE = ["Corn", "Soybean", "Soybean Meal", "Soybean Oil", "Wheat", "Oats", "Rough Rice", "Cocoa", 
#                "Coffee", "Orange Juice", "Cotton", "Sugar", "Live Cattle", "Feeder Cattle", "Lean Hogs"]
# ETF_EQ = ["VT", "VOO", "SH", "SSO", "SDS", "UPRO", "SPXL", "SPXU", "SPXS", "IVV", 
#           "ITOT", "VTI", "MGC", "VV", "IJH", "VO", "IJR", "VB", "TNA", "TZA",
#           "IUSG", "VUG", "IUSV", "VTV", "HDV", "USRT", "DIA", "DOG", "DDM", "DXD", 
#           "UDOW", "SDOW", "QQQ", "PSQ", "QLD", "QID", "TQQQ", "SQQQ", "URTY", "SRTY", 
#           "VIXY", "FEZ", "TECS", "FAS", "FAZ", "ERX", "KRE", "XBI", "IBB", "XOP",
#           "IXUS", "VXUS", "EEM", "IEMG", "IDEV", "ESGV", "VSGX", "SHE"]
# ETF_COMDTY = ["GLD", "IAU", "SLV"]
# ETF_SECTOR = ["XLK", "XLRE", "XLU", "XLV", "XLI", "XLC", "XLY", "XLF", "XLB", "XLP", "XLE"]
# ETF_MSCI_DM = ["SPY", "EZU", "EWJ", "EWU", "EWA", "EWL", "EWC", "ENZL", "EWD", "ENOR", "EWS", "EWH"]
# ETF_MSCI_EM = ["MCHI", "EWW", "EWY", "TUR", "INDA", "ERUS", "EWZ", "EZA", "EPOL", "EWT", "THD", "EWM"]
# ETF_FI = ["AGG", "IAGG", "IUSB", "ISTB", "IMTB", "TLH", "ILTB", "TLT", "JNK", "SJNK", 
#           "LQD", "BKLN", "BND", "BNDX", "EMB", "VWOB"]


# def load_fx():
#     """Return a dict of DataFrames of CCY/USD rates of 24 markets
    
#     Contains the following keys:
#         FX.PRC: All 24 markets closing prices
#         FX.RTN: All 24 markets daily returns
#         DMFX.PRC: 12 developed markets closing prices
#         DMFX.RTN: 12 developed markets daily returns
#         EMFX.PRC: 12 emerging markets closing prices
#         EMFX.RTN: 12 emerging markets daily returns
#     """
#     stream = pkg_resources.resource_stream(__name__, "data/fx.csv")
#     fx_price = pd.read_csv(stream, encoding="latin-1")
#     fx_price["Date"] = pd.to_datetime(fx_price.Date, format="%Y-%m-%d")
#     fx_price.set_index("Date", inplace=True)
#     FX = {"FX.PRC": fx_price, "FX.RTN": fx_price.pct_change(),
#           "DMFX.PRC": fx_price[DM], "DMFX.RTN": fx_price[DM].pct_change(),
#           "EMFX.PRC": fx_price[EM], "EMFX.RTN": fx_price[EM].pct_change()}
#     return FX

# def load_eqix():
#     """Return a dict of DataFrames of MSCI equity net return indices of 24 markets
    
#     Contains the following keys:
#         EQIX.PRC: All 24 markets plus world index values
#         EQIX.RTN: All 24 markets plus world daily returns
#         DMEQIX.PRC: 12 developed markets index values
#         DMEQIX.RTN: 12 developed markets daily returns
#         EMEQIX.PRC: 12 emerging markets index values
#         EMEQIX.RTN: 12 emerging markets daily returns
#         GTEQIX.PRC: World index values
#         GTEQIX.RTN: World daily returns
#     """
#     stream = pkg_resources.resource_stream(__name__, "data/eqix.csv")
#     eqix = pd.read_csv(stream, encoding="latin-1")
#     eqix["Date"] = pd.to_datetime(eqix.Date, format="%Y-%m-%d")
#     eqix.set_index("Date", inplace=True)
#     EQIX = {"EQIX.PRC": eqix, "EQIX.RTN": eqix.pct_change(),
#             "DMEQIX.PRC": eqix[DM], "DMEQIX.RTN": eqix[DM].pct_change(),
#             "EMEQIX.PRC": eqix[EM], "EMEQIX.RTN": eqix[EM].pct_change(),
#             "GTEQIX.PRC": eqix["WORLD"], "GTEQIX.RTN": eqix["WORLD"].pct_change()}
#     return EQIX

# def load_useq():
#     """Return a dict of DataFrames of US common stocks compiled with Yahoo Finance data
    
#     Contains the following keys:
#         USEQ.PRC: ~1300 US common stocks closing prices 
#         USEQ.RTN: ~1300 US common stocks daily returns
#     """
#     stream1 = pkg_resources.resource_stream(__name__, "data/useq1.csv")
#     stream2 = pkg_resources.resource_stream(__name__, "data/useq2.csv")
#     useq = pd.concat([pd.read_csv(stream1, encoding="latin-1"), pd.read_csv(stream2, encoding="latin-1").drop(columns=["Date"])], axis=1)
#     useq["Date"] = pd.to_datetime(useq.Date, format="%Y-%m-%d")
#     useq.set_index("Date", inplace=True)
#     EQ = {"USEQ.PRC": useq, "USEQ.RTN": useq.pct_change()}
#     return EQ

# def load_etf():
#     """Return a dict of DataFrames of 112 liquid and functional ETFs compiled with Yahoo Finance data
    
#     Contains the following keys:
#         ETF.PRC: 112 common ETFs closing prices 
#         ETF.RTN: 112 common ETFs daily returns
#         DMEQ.PRC: 12 MSCI developed market index ETFs closing prices
#         DMEQ.RTN: 12 MSCI developed market index ETFs daily returns
#         EMEQ.PRC: 12 MSCI emerging market index ETFs closing prices
#         EMEQ.RTN: 12 MSCI emerging market index ETFs daily returns
#         EQ.PRC: 58 equity index ETFs closing prices
#         EQ.RTN: 58 equity index ETFs daily returns
#         SECTOR.PRC: 11 US sector index ETFs closing prices
#         SECTOR.RTN: 11 US sector index ETFs daily returns
#         FI.PRC: 16 fixed income ETFs closing prices
#         FI.RTN: 16 fixed income ETFs daily returns
#         COMDTY.PRC: 3 precious metal ETFs closing prices
#         COMDTY.RTN: 3 precious metal ETFs daily returns
#     """
#     stream = pkg_resources.resource_stream(__name__, "data/etf.csv")
#     etf = pd.read_csv(stream, encoding="latin-1")
#     etf["Date"] = pd.to_datetime(etf.Date, format="%Y-%m-%d")
#     etf.set_index("Date", inplace=True)
#     ETF = {"ETF.PRC": etf, "ETF.RTN": etf.pct_change(), 
#            "DMEQ.PRC": etf[ETF_MSCI_DM], "DMEQ.RTN": etf.pct_change()[ETF_MSCI_DM],
#            "EMEQ.PRC": etf[ETF_MSCI_EM], "EMEQ.RTN": etf.pct_change()[ETF_MSCI_EM],
#            "EQ.PRC": etf[ETF_EQ], "EQ.RTN": etf.pct_change()[ETF_EQ],
#            "SECTOR.PRC": etf[ETF_SECTOR], "SECTOR.RTN": etf.pct_change()[ETF_SECTOR],
#            "FI.PRC": etf[ETF_FI], "FI.RTN": etf.pct_change()[ETF_FI],
#            "COMDTY.PRC": etf[ETF_COMDTY], "COMDTY.RTN": etf.pct_change()[ETF_COMDTY]}
#     return ETF

# def load_rates():
#     """Return a dict of interest rates 
    
#     Contains the following keys:
#         FI.IBOR: All 24 markets 3M interbank offered rates (yield of FX)
#         DMFI.IBOR: 12 developed markets 3M interbank offered rates (yield of FX)
#         EMFI.IBOR: 12 emerging markets 3M interbank offered rates (yield of FX)
#         FI.GOV10Y: All 24 markets 10Y government rates (long-term risk-free proxy)
#         DMFI.GOV10Y: 12 developed markets 10Y government rates (long-term risk-free proxy)
#         EMFI.GOV10Y: 12 emerging markets 10Y government rates (long-term risk-free proxy)
#         FI.GOV3M: All 24 markets 3M Treasury/government rates (short-term risk-free proxy)
#         DMFI.GOV3M: 12 developed markets 3M Treasury/government rates (short-term risk-free proxy)
#         EMFI.GOV3M: 12 emerging markets 3M Treasury/government rates (short-term risk-free proxy)
#     """
#     stream1 = pkg_resources.resource_stream(__name__, "data/ibor.csv")
#     stream2 = pkg_resources.resource_stream(__name__, "data/figovt10y.csv")
#     stream3 = pkg_resources.resource_stream(__name__, "data/figovt3m.csv")
#     ibor = pd.read_csv(stream1, encoding="latin-1")
#     govt10y = pd.read_csv(stream2, encoding="latin-1")
#     govt3m = pd.read_csv(stream3, encoding="latin-1")
#     ibor["Date"] = pd.to_datetime(ibor.Date, format="%Y-%m-%d")
#     govt10y["Date"] = pd.to_datetime(govt10y.Date, format="%Y-%m-%d")
#     govt3m["Date"] = pd.to_datetime(govt3m.Date, format="%Y-%m-%d")
#     ibor.set_index("Date", inplace=True)
#     govt10y.set_index("Date", inplace=True)
#     govt3m.set_index("Date", inplace=True)
#     FI = {"FI.IBOR": ibor, "DMFI.IBOR": ibor[DM], "EMFI.IBOR": ibor[EM],
#           "FI.GOV10Y": govt10y, "DMFI.GOV10Y": govt10y[DM], "EMFI.GOV10Y": govt10y[EM],
#           "FI.GOV3M": govt3m, "DMFI.GOV3M": govt3m[DM], "EMFI.GOV3M": govt3m[EM]}
#     return FI

# def load_comdty():
#     """Return a dict of DataFrames of commodity futures
    
#     Contains the following keys:
#         COMDTY.PRC: All commodities 1st generic futures ask prices
#         COMDTY.RTN: All commodities 1st generic futures daily returns
#         METAL.PRC: Metals 1st generic futures ask prices
#         METAL.RTN: Metals 1st generic futures daily returns
#         ENERGY.PRC: Energy 1st generic futures ask prices
#         ENERGY.RTN: Energy 1st generic futures daily returns
#         AGRICULTURE.PRC: Agriculture product 1st generic futures ask prices
#         AGRICULTURE.RTN: Agriculture product 1st generic futures daily returns
#     """
#     stream = pkg_resources.resource_stream(__name__, "data/commodity.csv")
#     comdty = pd.read_csv(stream, encoding="latin-1")
#     comdty["Date"] = pd.to_datetime(comdty.Date, format="%Y-%m-%d")
#     comdty.set_index("Date", inplace=True)
#     CM = {"COMDTY.PRC": comdty, "COMDTY.RTN": comdty.pct_change(), 
#           "METAL.PRC": comdty[METAL], "METAL.RTN": comdty.pct_change()[METAL],
#           "ENERGY.PRC": comdty[ENERGY], "ENERGY.RTN": comdty.pct_change()[ENERGY],
#           "AGRICULTURE.PRC": comdty[AGRICULTURE], "AGRICULTURE.RTN": comdty.pct_change()[AGRICULTURE]}
#     return CM