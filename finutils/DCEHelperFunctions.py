from .FinDate import FinDate, cnday
from .FinHelperFunctions import singleContractTimeSpecifier, labelToString
from .FinHelperFunctions import contractAggregator, tenor_specifier, KandFlag_specifier, lot_specifier
from .FinHelperFunctions import K_specifier, CP_specifier, Tenor_specifier
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def DCEcode2expiry(contractCode):
    if type(contractCode) == str:
        contractCode = contractCode[-4:]
        contractCode = int(contractCode)
    year = contractCode // 100
    month = contractCode - 2000
    year += 2000
    
    return DCEexpireDate(year, month)



def DCEexpireDate(contract_year, contract_mon):

    futuresExpiryMonth = datetime(contract_year, contract_mon, 1, 15, 0)
    optionsExpiryDate = futuresExpiryMonth + relativedelta(months = -1)
    count = 0
    while count<4:
        if cnday(optionsExpiryDate).isHoliday():
            optionsExpiryDate = optionsExpiryDate + timedelta(days = 1)
        else:
            count += 1
            optionsExpiryDate = optionsExpiryDate + timedelta(days = 1)
    while cnday(optionsExpiryDate).isHoliday():
        optionsExpiryDate = optionsExpiryDate + timedelta(days = 1)
    return cnday(optionsExpiryDate)

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

    else:
        print('time_specifier error')