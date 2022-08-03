from ..finutils.FinDate import FinDate
from ..finutils.FinHelperFunctions import singleContractTimeSpecifier, labelToString
from ..finutils.FinHelperFunctions import contractAggregator, tenor_specifier, KandFlag_specifier, lot_specifier
from ..finutils.FinHelperFunctions import K_specifier, CP_specifier, Tenor_specifier
from datetime import datetime
from .DCEHelperFunctions import DCEexpireDate


def time_specifier(optionIdentity, country):

    if country == 'CN':
        yearMonth = []
        for thisone in optionIdentity: 
            yearMonth.append(singleContractTimeSpecifier(thisone[0])) 
        expiry_dates = {}
        for i in range(len(yearMonth)):
            thisYM = yearMonth[i]
            expiryDate = DCEexpireDate(thisYM[0], thisYM[1])
            expiry_dates[optionIdentity[i]] = expiryDate
        return expiry_dates

    elif country == 'SG':
        yearMonth = []
        for thisone in optionIdentity: 
            yearMonth.append(singleContractTimeSpecifier(thisone[0]))  
        startAveragingDates = {}
        expiry_dates = {}
        for i in range(len(yearMonth)):
            thisYM = yearMonth[i]
            startAveragingDate, expiryDate = SGXexpireDate(thisYM[0], thisYM[1], country)
            startAveragingDates[optionIdentity[i]] = startAveragingDate
            expiry_dates[optionIdentity[i]] = expiryDate
        return startAveragingDates, expiry_dates
        
    else:
        print('time_specifier error')

def SGXexpireDate(contract_year, contract_mon, country = 'SG'):
    if contract_mon != 12 and contract_mon != 1:
        daysInLastMon = (datetime(contract_year,contract_mon,1) - 
                        datetime(contract_year,contract_mon - 1,1)).days
        daysInTheMon = (datetime(contract_year,contract_mon+1,1) - 
                        datetime(contract_year,contract_mon,1)).days
        if type(country) == str and country.upper() == 'SG':
            startAveragingDate = FinDate(contract_year, contract_mon - 1, daysInLastMon, 15, 0, country)
            expiry_date = FinDate(contract_year, contract_mon, daysInTheMon, 15, 0, country)
        elif type(country) == str and country.upper() == 'CN':
            startAveragingDate = FinDate(contract_year, contract_mon - 1, daysInLastMon, 15, 0, country)
            expiry_date = FinDate(contract_year, contract_mon, daysInTheMon, 15, 0, country)
        else:
            startAveragingDate = FinDate(contract_year, contract_mon, 1, country)
            expiry_date = FinDate(contract_year, contract_mon, daysInTheMon, 23, 59, country)
    elif contract_mon == 12:
        daysInLastMon = 30
        daysInTheMon = 31
        if type(country) == str and country.upper() == 'SG':
            startAveragingDate = FinDate(contract_year, contract_mon - 1, daysInLastMon, 15, 00, country)
            expiry_date = FinDate(contract_year, contract_mon, daysInTheMon, 15, 00, country)
        elif type(country) == str and country.upper() == 'CN':
            startAveragingDate = FinDate(contract_year, contract_mon - 1, daysInLastMon, 15, 0, country)
            expiry_date = FinDate(contract_year, contract_mon, daysInTheMon, 15, 00, country)
        else:
            startAveragingDate = FinDate(contract_year, contract_mon, 1, country)
            expiry_date = FinDate(contract_year, contract_mon, daysInTheMon, 23, 59, country)
    else:
        daysInLastMon = 31
        daysInTheMon = 31
        if type(country) == str and country.upper() == 'SG':
            startAveragingDate = FinDate(contract_year - 1, 12, 31, 15, 0, country)
            expiry_date = FinDate(contract_year, contract_mon, daysInTheMon, 15, 00, country)
        elif type(country) == str and country.upper() == 'CN':
            startAveragingDate = FinDate(contract_year - 1, 12, 31, 15, 0, country)
            expiry_date = FinDate(contract_year, contract_mon, daysInTheMon, 15, 00, country)
        else:
            startAveragingDate = FinDate(contract_year, contract_mon, 1, country)
            expiry_date = FinDate(contract_year, contract_mon, daysInTheMon, 23, 59, country)
    
    return startAveragingDate, expiry_date