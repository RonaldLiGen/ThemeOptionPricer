from .FinError import FinError
from datetime import date, timedelta, datetime
import datetime as dt
import numpy as np

ENFORCE_DAY_FIRST = True

##########################################################################

shortDayNames = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
longDayNames = [
    'MONDAY',
    'TUESDAY',
    'WEDNESDAY',
    'THURSDAY',
    'FRIDAY',
    'SATURDAY',
    'SUNDAY']
shortMonthNames = [
    'JAN',
    'FEB',
    'MAR',
    'APR',
    'MAY',
    'JUN',
    'JUL',
    'AUG',
    'SEP',
    'OCT',
    'NOV',
    'DEC']
longMonthNames = [
    'JANUARY',
    'FEBRUARY',
    'MARCH',
    'APRIL',
    'MAY',
    'JUNE',
    'JULY',
    'AUGUST',
    'SEPTEMBER',
    'OCTOBER',
    'NOVEMBER',
    'DECEMBER']

monthDaysNotLeapYear = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
monthDaysLeapYear = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

###############################################################################

def isLeapYear(y: int):
    ''' Test whether year y is a leap year - if so return True, else False '''
    leapYear = ((y % 4 == 0) and (y % 100 != 0) or (y % 400 == 0))
    return leapYear

def minute_24timekeeping_translater(days, country = None):
    if country is None:
        minutes = days // (1/1440)
        hrLevel = minutes // 60
        minLevel = minutes % 60
    else:
        minutes = days // (1/345)
        if minutes < 75:
            hrLevel = minutes // 60 + 9
            minLevel = minutes % 60
        elif minutes < 105:
            hrLevel = 10
            minLevel = 30 + minutes - 75
        elif minutes < 135:
            hrLevel = 11
            minLevel = minutes - 105
        elif minutes < 165:
            hrLevel = 13
            minLevel = minutes - 135 + 30
        elif minutes < 225:
            hrLevel = 14
            minLevel = minutes - 165
        else:
            minutes = minutes - 225
            hrLevel = 21 + minutes // 60
            minLevel = minutes % 60
    return int(hrLevel), int(round(minLevel, 0))

###############################################################################
# CREATE DATE COUNTER
###############################################################################


gDateCounterList = None
gStartYear = 1900
gEndYear = 2100

CNHolidayList = {

    '2019-01-01': True, 
    '2019-02-04': True, '2019-02-05': True, '2019-02-06': True,
    '2019-02-07': True, '2019-02-08': True, '2019-02-09': True, '2019-02-10': True,
    '2019-04-05': True,
    '2019-05-01': True, 
    '2019-06-07': True,
    '2019-09-13': True,
    '2019-10-01': True, '2019-10-02': True, '2019-10-03': True, '2019-10-04': True, 
    '2019-10-05': True, '2019-10-06': True, '2019-10-07': True,

    '2020-01-01': True, 
    '2020-01-24': True, '2020-01-25': True, '2020-01-26': True, '2020-01-27': True,
    '2020-01-28': True, '2020-01-29': True, '2020-01-30': True,
    '2020-04-06': True, 
    '2020-05-01': True, '2020-05-02': True,
    '2020-06-25': True, '2020-06-26': True,
    '2020-10-08': True,
    '2020-10-01': True, '2020-10-02': True, '2020-10-03': True, '2020-10-04': True, 
    '2020-10-05': True, '2020-10-06': True, '2020-10-07': True, 

    '2021-01-01': True, '2021-01-02': True, '2021-01-03': True,
    '2021-02-11': True, '2021-02-12': True, '2021-02-13': True,
    '2021-02-14': True, '2021-02-15': True, '2021-02-16': True, '2021-02-17': True,
    '2021-04-03': True, '2021-04-04': True, '2021-04-05': True,
    '2021-05-01': True, '2021-05-02': True, '2021-05-03': True, '2021-05-04': True, '2021-05-05': True,
    '2021-06-12': True, '2021-06-13': True, '2021-06-14': True,
    '2021-09-19': True, '2021-09-20': True, '2021-09-21': True,
    '2021-10-01': True, '2021-10-02': True, '2021-10-03': True, '2021-10-04': True,
    '2021-10-05': True, '2021-10-06': True, '2021-10-07': True,

    '2022-01-01': True, '2022-01-02': True, '2022-01-03': True,
    '2022-01-31': True, '2022-02-01': True, '2022-02-02': True, '2022-02-03': True,
    '2022-02-04': True, '2022-02-05': True, '2022-02-06': True,
    '2022-04-04': True, '2022-04-05': True,
    '2022-05-02': True, '2022-05-03': True, '2022-05-04': True,
    '2022-06-03': True,
    '2022-09-12': True,
    '2022-10-01': True, '2022-10-02': True, '2022-10-03': True, '2022-10-04': True, 
    '2022-10-05': True, '2022-10-06': True, '2022-10-07': True,

    '2023-01-02': True,
    '2023-01-21': True, '2023-01-22': True, '2023-01-23': True,
    '2023-01-24': True, '2023-01-25': True, '2023-01-26': True, '2023-01-27': True,
    '2023-04-03': True, '2023-04-04': True, '2023-04-05': True,
    '2023-05-01': True,
    '2023-06-22': True, '2023-06-23': True,
    '2023-09-29': True,
    '2023-10-01': True, '2023-10-02': True, '2023-10-03': True,
    '2023-10-04': True, '2023-10-05': True, '2023-10-06': True, '2023-10-07': True
}

SGHolidayList = {
    '2021-01-01': True,
    '2021-02-12': True,
    '2021-02-13': True,
    '2021-04-02': True,
    '2021-05-13': True,
    '2021-05-01': True,
    '2021-05-26': True,
    '2021-07-20': True,
    '2021-08-09': True,
    '2021-11-04': True,
    '2021-12-25': True,

    '2022-01-01': True,
    '2022-02-01': True,
    '2022-02-02': True,
    '2022-04-15': True,
    '2022-05-01': True,
    '2022-05-02': True,
    '2022-05-03': True,
    '2022-05-15': True,
    '2022-05-16': True,
    '2022-07-11': True,
    '2022-08-09': True,
    '2022-10-24': True,
    '2022-12-25': True,
    '2022-12-26': True,

    '2023-01-01': True,
    '2023-01-22': True,
    '2023-01-23': True,
    '2023-04-07': True,
    '2023-04-21': True,
    '2023-05-01': True,
    '2023-05-05': True,
    '2023-06-28': True,
    '2023-08-09': True,
    '2023-11-12': True,
    '2023-12-25': True
}


def IsHoliday(dtm, cty):

    if (dtm.weekday() == 6 or dtm.weekday() == 5):
        return True
    else:
        if cty == "CN":
            return dtm.strftime("%Y-%m-%d") in CNHolidayList
        if cty == "SG":
            return dtm.strftime("%Y-%m-%d") in SGHolidayList

    return False

def calculateList():
    ''' Calculate list of dates so that we can do quick lookup to get the
    number of dates since 1 Jan 1900 (inclusive) BUT TAKING INTO ACCOUNT THE
    FACT THAT EXCEL MISTAKENLY CALLS 1900 A LEAP YEAR. For us, agreement with
    Excel is more important than this leap year error and in any case, we will
    not usually be calculating day differences with start dates before 28 Feb
    1900. Note that Excel inherited this "BUG" from LOTUS 1-2-3. '''

    dayCounter = 0
    maxDays = 0
    global gDateCounterList
    global gStartYear
    global gEndYear

    # print("Calculating list between", gStartYear, "and", gEndYear)

    gDateCounterList = []

    idx = -1  # the first element will be idx=0

    for yy in range(1900, gEndYear+1):

        # DO NOT CHANGE THIS FOR AGREEMENT WITH EXCEL WHICH ASSUMES THAT 1900
        # WAS A LEAP YEAR AND THAT 29 FEB 1900 ACTUALLY HAPPENED. A LOTUS BUG.
        if yy == 1900:
            leapYear = True
        else:
            leapYear = isLeapYear(yy)

        for mm in range(1, 13):

            if leapYear is True:
                maxDays = monthDaysLeapYear[mm-1]
            else:
                maxDays = monthDaysNotLeapYear[mm-1]

            for _ in range(1, maxDays+1):
                idx += 1
                dayCounter += 1
                if yy >= gStartYear:
                    gDateCounterList.append(dayCounter)

            for _ in range(maxDays, 31):
                idx += 1
                if yy >= gStartYear:
                    gDateCounterList.append(-999)

def dateIndex(d, m, y):
    idx = (y-gStartYear) * 12 * 31 + (m-1) * 31 + (d-1)
    return idx

def dateFromIndex(idx):
    ''' Reverse mapping from index to date. Take care with numba as it can do
    weird rounding on the integer. Seems OK now. '''
    y = int(gStartYear + idx/12/31)
    m = 1 + int((idx - (y-gStartYear) * 12 * 31) / 31)
    d = 1 + idx - (y-gStartYear) * 12 * 31 - (m-1) * 31
    return (d, m, y)

def weekDay(dayCount):
    weekday = (dayCount+5) % 7
    return weekday

###############################################################################

class FinDate():
    ''' A date class to manage dates that is simple to use and includes a
    number of useful date functions used frequently in Finance. '''

    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6

    ###########################################################################

    def __init__(self,
                 y: int,  # Year number which must be between 1900 and 2100 
                 m: int,  # Month number where January = 1, ..., December = 12
                 d: int,  # Day number in month with values from 1 to 31
                 hr: int = 0,
                 mnt: int = 0,
                 country = None):  
        ''' Create a date given a day of month, month and year. The arguments
        must be in the order of day (of month), month number and then the year.
        The year must be a 4-digit number greater than or equal to 1900. '''

        global gStartYear
        global gEndYear

        # If the date has been entered as y, m, d we flip it to d, m, y
        if d >= gStartYear and d < gEndYear and y > 0 and y <= 31:
            tmp = y
            y = d
            d = tmp

        if gDateCounterList is None:
            calculateList()

        if y < 1900:
            raise FinError("Year cannot be before 1900")

        # Resize date list dynamically if required
        if y < gStartYear:
            gStartYear = y
            calculateList()

        if y > gEndYear:
            gEndYear = y
            calculateList()

        if y < gStartYear or y > gEndYear:
            raise FinError(
                "Date: year " + str(y) + " should be " + str(gStartYear) +
                " to " + str(gEndYear))

        if d < 1:
            raise FinError("Date: Leap year. Day not valid.")

        leapYear = isLeapYear(y)

        if leapYear:
            if d > monthDaysLeapYear[m - 1]:
                print(d, m, y)
                raise FinError("Date: Leap year. Day not valid.")
        else:
            if d > monthDaysNotLeapYear[m - 1]:
                print(d, m, y)
                raise FinError("Date: Not Leap year. Day not valid.")

        self.y = y
        self.m = m
        self.d = d
        self.hr = hr
        self.mnt = mnt
        self.excelDate = 0
        if type(country) == str:
            self.country = country.upper()
        else:
            self.country = country
        self.date = str(y) + '-' + str(m) + '-' + str(d)

        self.__refresh()
        
        self.date = dt.datetime(y, m, d, 0, 0)
        self.datetime = dt.datetime(y, m, d, hr, mnt)

        self.minPassedToday = hr*60 + mnt
        self.dayPassedToday = self.minPassedToday / 1440

        
        self.tradingMinutePassed = self.getTradeMinutePassed()
        self.tradingMinuteLeft = self.getTradeMinuteLeft()

        self.tradingDayPassed = self.getTradeDayPassed()
        self.tradingDayLeft = self.getTradeDayLeft()

    ###########################################################################
    
    def getTradeMinutePassed(self):
        realTradingTime = self.getEquivalentTradingDateime()
        if type(self.country) == str and self.country == 'SG':
            if realTradingTime.hour < 9:
                tradingMinutePassed = 0
            elif realTradingTime.hour == 9:
                tradingMinutePassed = 0 + realTradingTime.minute
            elif realTradingTime.hour == 10:
                if realTradingTime.minute < 15:
                    tradingMinutePassed = 60 + realTradingTime.minute
                elif realTradingTime.minute < 30:
                    tradingMinutePassed = 75
                else: 
                    tradingMinutePassed = 75 + realTradingTime.minute-30
            elif realTradingTime.hour == 11:
                if realTradingTime.minute < 30:
                    tradingMinutePassed = 105 + realTradingTime.minute
                else: 
                    tradingMinutePassed = 135 
            elif realTradingTime.hour < 13 or (realTradingTime.hour == 13 and realTradingTime.minute < 30): 
                tradingMinutePassed = 135
            elif realTradingTime.hour < 15:
                tradingMinutePassed = 135 + (realTradingTime.hour-13)*60 + realTradingTime.minute - 30
            elif realTradingTime.hour < 21:
                tradingMinutePassed = 225
            elif realTradingTime.hour < 23:
                tradingMinutePassed = 225 + (realTradingTime.hour-21)*60 + realTradingTime.minute
            else:
                tradingMinutePassed = 345

        elif type(self.country) == str and self.country == 'CN':
            if realTradingTime.hour < 9:
                tradingMinutePassed = 0
            elif realTradingTime.hour == 9:
                tradingMinutePassed = 0 + realTradingTime.minute
            elif realTradingTime.hour == 10:
                if realTradingTime.minute < 15:
                    tradingMinutePassed = 60 + realTradingTime.minute
                elif realTradingTime.minute < 30:
                    tradingMinutePassed = 75
                else: 
                    tradingMinutePassed = 75 + realTradingTime.minute-30
            elif realTradingTime.hour == 11:
                if realTradingTime.minute < 30:
                    tradingMinutePassed = 105 + realTradingTime.minute
                else: 
                    tradingMinutePassed = 135 
            elif realTradingTime.hour < 13 or (realTradingTime.hour == 13 and realTradingTime.minute < 30): 
                tradingMinutePassed = 135
            elif realTradingTime.hour < 15:
                tradingMinutePassed = 135 + (realTradingTime.hour-13)*60 + realTradingTime.minute - 30
            elif realTradingTime.hour < 21:
                tradingMinutePassed = 225
            elif realTradingTime.hour < 23:
                tradingMinutePassed = 225 + (realTradingTime.hour-21)*60 + realTradingTime.minute
            else:
                tradingMinutePassed = 345
        
        else:
            tradingMinutePassed = self.minPassedToday

        return tradingMinutePassed

    def getTradeMinuteLeft(self):
        
        if self.country == "SG":
            return 345 - self.tradingMinutePassed
        elif self.country == "CN":
            return 345 - self.tradingMinutePassed
        else:
            return 1440 - self.tradingMinutePassed
        
    ###########################################################################
    
    def getTradeDayPassed(self):

        if self.hasNightTradingSession():
            if type(self.country) == str and self.country == 'SG':
                tradingDayPassed = self.tradingMinutePassed / 345
                
            elif type(self.country) == str and self.country == 'CN':
                tradingDayPassed = self.tradingMinutePassed / 345
                
            else:
                tradingDayPassed = self.dayPassedToday
        else:
            if type(self.country) == str and self.country == 'SG':
                tradingDayPassed = self.tradingMinutePassed / 225
                
            elif type(self.country) == str and self.country == 'CN':
                tradingDayPassed = self.tradingMinutePassed / 225
                
            else:
                tradingDayPassed = self.dayPassedToday
            
        return tradingDayPassed

    def getTradeDayLeft(self):
        return 1 - self.tradingDayPassed
        
    ###########################################################################

    def hasNightTradingSession(self):
        if self.weekday == 5 or self.weekday == 6:
            return False
        elif self.weekday == 4:
            nextWeekday = self.date + timedelta(days = 3)
            return not IsHoliday(nextWeekday, self.country)
        else:
            nextWeekday = self.date + timedelta(days = 1)
            return not IsHoliday(nextWeekday, self.country)

    def __refresh(self):
        ''' Update internal representation of date as number of days since the
        1st Jan 1900. This is same as Excel convention. '''

        idx = dateIndex(self.d, self.m, self.y)
        daysSinceFirstJan1900 = gDateCounterList[idx]
        wd = weekDay(daysSinceFirstJan1900)
        self.excelDate = daysSinceFirstJan1900
        self.weekday = wd

    ###########################################################################

    def isHoliday(self):
        return IsHoliday(self.date, self.country)

    ###########################################################################

    def __lt__(self, other):
        return self.excelDate + self.dayPassedToday < other.excelDate + other.dayPassedToday

    ###########################################################################

    def __gt__(self, other):

       return self.excelDate + self.dayPassedToday > other.excelDate + other.dayPassedToday

    ###########################################################################

    def __le__(self, other):
        return self.excelDate + self.dayPassedToday <= other.excelDate + other.dayPassedToday

    ###########################################################################

    def __ge__(self, other):
        return self.excelDate + self.dayPassedToday >= other.excelDate + other.dayPassedToday

    ###########################################################################
       
    def __sub__(self, other, type = 'TradingHour'):

        if self < other:
            return - (other.__sub__(self))

        if type == 'TradingHour':
            start = other.toEquivalentTradingTime().date
            end = self.toEquivalentTradingTime().date
            
            fullDayRange = [start, end]
            
            currentDt = fullDayRange[0]
            totalFullDay = 0

            while currentDt < fullDayRange[1]:
                if not IsHoliday(currentDt, self.country):
                    totalFullDay += 1
                currentDt = currentDt + dt.timedelta(days=1)

            return totalFullDay + self.tradingDayPassed - other.tradingDayPassed
        else: 
            start = other.date
            end = self.date
            
            fullDayRange = [start, end]
            
            currentDt = fullDayRange[0]
            totalFullDay = 0

            while currentDt < fullDayRange[1]:     
                totalFullDay += 1
                currentDt = currentDt + dt.timedelta(days=1)

            return totalFullDay + self.dayPassedToday - other.dayPassedToday
           
    ###########################################################################

    def __eq__(self, other):
        return self.excelDate == other.excelDate

    ###########################################################################

    def isWeekend(self):
        ''' returns True if the date falls on a weekend. '''
        # print('the day is ', self.weekday)
        if self.weekday == FinDate.SAT or self.weekday == FinDate.SUN:
            return True
        return False

    ###########################################################################
    
    def addDays(self,
                numDays: float = 1,
                workingDay = False):
        ''' Returns a new date that is numDays after the FinDate. I also make
        it possible to go backwards a number of days. '''

        if workingDay:
            today = self.toEquivalentTradingTime()
            todayDT = today.date
            minToAdd = numDays % 1
            MinutePassed = (minToAdd + today.tradingDayPassed) 
            numDays = numDays // 1 + (MinutePassed // 1)
            MinutePassed = MinutePassed % 1
            hrLevel, minLevel = minute_24timekeeping_translater(MinutePassed, self.country)
            if numDays < 0:
                step = -1
            else:
                step = +1
            while numDays != 0:
                todayDT = todayDT + timedelta(days = step)
                if not IsHoliday(todayDT, self.country):
                    numDays -= step
            newDt = FinDate(todayDT.year, todayDT.month, todayDT.day, hrLevel, minLevel, self.country)
            return newDt

        
        else:
            idx = dateIndex(self.d, self.m, self.y)
            
            minToAdd = numDays % 1
            MinutePassed = (minToAdd + self.dayPassedToday) 
            numDays = numDays // 1 + (MinutePassed // 1)
            MinutePassed = MinutePassed % 1
            hrLevel, minLevel = minute_24timekeeping_translater(MinutePassed)
            if numDays < 0:
                step = -1
            else:
                step = +1
            while numDays != 0:
                idx += step
                if gDateCounterList[idx] > 0:
                    numDays -= step
            (d, m, y) = dateFromIndex(idx)
            newDt = FinDate(d, m, y, hrLevel, minLevel, self.country)
            return newDt

    ###########################################################################

    def addMonths(self,
                  mm: (list, int)):
        ''' Returns a new date that is mm months after the FinDate. If mm is an
        integer or float you get back a single date. If mm is a vector you get
        back a vector of dates.'''

        numMonths = 1
        scalarFlag = False

        if isinstance(mm, int) or isinstance(mm, float):
            mmVector = [mm]
            scalarFlag = True
        else:
            mmVector = mm

        numMonths = len(mmVector)

        dateList = []

        for i in range(0, numMonths):

            mmi = mmVector[i]

            # If I get a float I check it has no decimal places
            if int(mmi) != mmi:
                raise FinError("Must only pass integers or float integers.")

            mmi = int(mmi)

            d = self.d
            m = self.m + mmi
            y = self.y

            while m > 12:
                m = m - 12
                y += 1

            while m < 1:
                m = m + 12
                y -= 1

            leapYear = isLeapYear(y)

            if leapYear:
                if d > monthDaysLeapYear[m - 1]:
                    d = monthDaysLeapYear[m - 1]
            else:
                if d > monthDaysNotLeapYear[m - 1]:
                    d = monthDaysNotLeapYear[m - 1]

            newDt = FinDate(d, m, y, self.hr, self.mnt, self.country)
            dateList.append(newDt)

        if scalarFlag is True:
            return dateList[0]
        else:
            return dateList

    ###########################################################################

    def addYears(self,
                 yy: (np.ndarray, float)):
        ''' Returns a new date that is yy years after the FinDate. If yy is an
        integer or float you get back a single date. If yy is a list you get
        back a vector of dates.'''

        numYears = 1
        scalarFlag = False

        if isinstance(yy, int) or isinstance(yy, float):
            yyVector = [yy]
            scalarFlag = True
        else:
            yyVector = yy

        numYears = len(yyVector)

        dateList = []

        for i in range(0, numYears):

            yyi = yyVector[i]

            # If yyi is not a whole month I adjust for days using average
            # number of days in a month which is 365.242/12
            daysInMonth = 365.242/12.0

            mmi = int(yyi * 12.0)
            ddi = int((yyi * 12.0 - mmi) * daysInMonth)
            newDt = self.addMonths(mmi)
            newDt = newDt.addDays(ddi)

            dateList.append(newDt)

        if scalarFlag is True:
            return dateList[0]
        else:
            return dateList

    ###########################################################################

    def addTradingMinutes(self, minutes = 1):
        outputDay = self.toEquivalentTradingTime()
        newMinute = (outputDay.tradingMinutePassed + minutes) % 345
        daysToAdd = (outputDay.tradingMinutePassed + minutes) // 345

        if newMinute < 75:
            hrLevel = newMinute // 60 + 9
            minLevel = newMinute % 60
        elif newMinute < 105:
            hrLevel = 10
            minLevel = 30 + newMinute - 75
        elif newMinute < 135:
            hrLevel = 11
            minLevel = newMinute - 105
        elif newMinute < 165:
            hrLevel = 13
            minLevel = newMinute - 135 + 30
        elif newMinute < 225:
            hrLevel = 14
            minLevel = newMinute - 165
        else:
            newMinute = newMinute - 225
            hrLevel = 21 + newMinute // 60
            minLevel = newMinute % 60
        
        outputDay = outputDay.addDays(daysToAdd)
        outputDay.mnt = minLevel
        outputDay.hr = hrLevel
        return outputDay.toEquivalentTradingTime()


    def datetime(self):
        ''' Returns a datetime of the date '''
        return datetime(self.y, self.m, self.d, self.hr, self.mnt)

    ###########################################################################

    def __repr__(self):
        ''' returns a formatted string of the date '''
        dateStr = ""
        dateStr += shortDayNames[self.weekday]

        if self.d < 10:
            dateStr += " 0" + str(self.d) + " "
        else:
            dateStr += " " + str(self.d) + " "

        dateStr += shortMonthNames[self.m - 1]
        dateStr += " " + str(self.y)
        dateStr += " -"

        if self.hr < 10:
            dateStr += " 0" + str(self.hr) + " "
        else:
            dateStr += " " + str(self.hr) + " "

        if self.mnt < 10:
            dateStr += ":0" + str(self.mnt) + " "
        else:
            dateStr += ":" + str(self.mnt) + " "
        
        return dateStr

    ###########################################################################

    def __print(self):
        ''' prints formatted string of the date. '''
        print(self)

    def isTradingTime(self):
        if self.country is None:
            return not self.isWeekend()
        if self.isHoliday():
            return False
        elif self.hr < 9:
            return False
        elif self.hr == 10:
            if self.mnt > 15 and self.mnt < 30:
                return False
        elif self.hr == 11:
            if self.mnt > 30:
                return False
        elif self.hr == 12: 
            return False
        elif self.hr == 13 and self.mnt < 30:
            return False
        elif self.hr >= 15 and self.hr < 21:
            return False
        elif self.hr >= 23:
            return False
        elif self.hr > 21 and not self.hasNightTradingSession():
            return False
        return True
    
    def toEquivalentTradingTime(self):
        if self.country is None:
            return self
        else:
            outputDay = self.date
            if IsHoliday(outputDay, self.country):
                while IsHoliday(outputDay, self.country):
                    outputDay = outputDay + timedelta(days = 1)
                hr = 9
                mnt = 0
                output = FinDate(outputDay.year,outputDay.month, outputDay.day, hr, mnt, self.country)
            elif self.hr < 9:
                hr = 9
                mnt = 0
                output = FinDate(outputDay.year,outputDay.month, outputDay.day, hr, mnt, self.country)
            elif self.hr == 10:
                if self.mnt >= 15 and self.mnt < 30:
                    hr = 10
                    mnt = 30
                else:
                    hr = self.hr
                    mnt = self.mnt
                output = FinDate(outputDay.year,outputDay.month, outputDay.day, hr, mnt, self.country)
            elif self.hr == 11:
                if self.mnt >= 30:
                    hr = 13
                    mnt = 30
                else:
                    hr = self.hr
                    mnt = self.mnt
                output = FinDate(outputDay.year,outputDay.month, outputDay.day, hr, mnt, self.country)
            elif self.hr == 12:
                hr = 13
                mnt = 30
                output = FinDate(outputDay.year,outputDay.month, outputDay.day, hr, mnt, self.country)
            elif self.hr == 13 and self.mnt < 30:
                hr = 13
                mnt = 30
                output = FinDate(outputDay.year,outputDay.month, outputDay.day, hr, mnt, self.country)
            elif self.hr >= 15 and self.hr < 21:
                hr = 21
                mnt = 0
                output = FinDate(outputDay.year,outputDay.month, outputDay.day, hr, mnt, self.country)
            elif self.hr >= 21 and not self.hasNightTradingSession():
                outputDay = outputDay + timedelta(days = 1)
                while IsHoliday(outputDay, self.country):
                    outputDay = outputDay + timedelta(days = 1)
                hr = 9
                mnt = 0
                output = FinDate(outputDay.year,outputDay.month, outputDay.day, hr, mnt, self.country)
            elif self.hr >= 23:
                outputDay = outputDay + timedelta(days = 1)
                while IsHoliday(outputDay, self.country):
                    outputDay = outputDay + timedelta(days = 1)
                hr = 9
                mnt = 0
                output = FinDate(outputDay.year,outputDay.month, outputDay.day, hr, mnt, self.country)
            else:
                hr = self.hr
                mnt = self.mnt
                output = FinDate(outputDay.year,outputDay.month, outputDay.day, hr, mnt, self.country)
            return output
        
    def getEquivalentTradingDateime(self):
        if self.country is None:
            return self
        else:
            outputDay = self.date
            if IsHoliday(outputDay, self.country):
                while IsHoliday(outputDay, self.country):
                    outputDay = outputDay + timedelta(days = 1)
                hr = 9
                mnt = 0
            elif self.hr < 9:
                hr = 9
                mnt = 0
            elif self.hr == 10:
                if self.mnt > 15 and self.mnt < 30:
                    hr = 10
                    mnt = 30
                else:
                    hr = self.hr
                    mnt = self.mnt
            elif self.hr == 11:
                if self.mnt > 30:
                    hr = 13
                    mnt = 30
                else:
                    hr = self.hr
                    mnt = self.mnt
            elif self.hr == 12: 
                hr = 13
                mnt = 30
            elif self.hr == 13 and self.mnt < 30:
                hr = 13
                mnt = 30
            elif self.hr >= 15 and self.hr < 21:
                hr = 21
                mnt = 00
            elif self.hr >= 21 and not self.hasNightTradingSession():
                outputDay = outputDay + timedelta(days = 1)
                while IsHoliday(outputDay, self.country):
                    outputDay = outputDay + timedelta(days = 1)
                hr = 9
                mnt = 0
            elif self.hr >= 23:
                outputDay = outputDay + timedelta(days = 1)
                while IsHoliday(outputDay, self.country):
                    outputDay = outputDay + timedelta(days = 1)
                hr = 9
                mnt = 0
            else:
                hr = self.hr
                mnt = self.mnt
            outputDay = datetime(outputDay.year,outputDay.month, outputDay.day, hr, mnt)
        return outputDay
    
###############################################################################

def cnday(valueDate: dt.datetime):
    return FinDate(valueDate.year, valueDate.month, valueDate.day, valueDate.hour, valueDate.minute, 'CN')

def sgday(valueDate: dt.datetime):
    return FinDate(valueDate.year, valueDate.month, valueDate.day, valueDate.hour, valueDate.minute, 'SG')

###############################################################################

def tradingDaysThisMonth(country = 'SG'):
    if country == "SG":
        thisyear = datetime.now().year
        thismonth = datetime.now().month
        count = 0
        thisday = datetime(thisyear, thismonth, 1)
        while thisday.month == thismonth:
            if sgday(thisday).isHoliday():
                thisday = thisday + timedelta(days = 1)
            else:
                thisday = thisday + timedelta(days = 1)
                count += 1
        return count
    else:
        thisyear = datetime.now().year
        thismonth = datetime.now().month
        count = 0
        thisday = datetime(thisyear, thismonth, 1)
        while thisday.month == thismonth:
            if cnday(thisday).isHoliday():
                thisday = thisday + timedelta(days = 1)
            else:
                thisday = thisday + timedelta(days = 1)
                count += 1
        return count

###############################################################################

def FinDateNow(country = 'CN'):
    if country == 'CN':
        return cnday(datetime.now())
    else:
        return sgday(datetime.now())


    ###########################################################################
    
    # def actualTradingDatetime(self):
    #     if self.country == 'CN' or self.country == 'SG':
    #         if self.hr >= 15:
    #             if self.weekday == 5 or self.weekday == 6:
    #                 return self.date
    #             elif self.weekday == 4:
    #                 return self.date + dt.timedelta(days = 3)
    #             else:
    #                 return self.date + dt.timedelta(days = 1)
    #         else:
    #             return self.date
    #     else:
    #         return self.date

###############################################################################
 
