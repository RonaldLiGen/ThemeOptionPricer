##############################################################################
# Copyright (C) 2018, 2019, 2020 Dominic O'Kane
##############################################################################

from .FinDate import FinDate

##############################################################################


gDaysInYear = 245
gSmall = 1e-12
gNotebookMode = False
SGDaysInYear_dict = {2021: 253, 2022: 254, 2023: 252}
CNDaysInYear_dict = {2021: 243, 2022: 242, 2023: 242}

# for this_year in range(2021, 2024):
#     SGworkingDays = 0
#     CNworkingDays = 0
#     for this_month in range(1, 13):
#         for this_day in range(1, 32):
#             try:
#                 SGday = FinDate(this_day, this_month, this_year, 11, 0, 'SG')
#                 if (not SGday._isHoliday()):
#                     SGworkingDays += 1
#                 CNday = FinDate(this_day, this_month, this_year, 9, 15, 'CN')
#                 if (not CNday._isHoliday()):
#                     CNworkingDays += 1
#             except:
#                 break
#     SGDaysInYear_dict[this_year] = SGworkingDays
#     CNDaysInYear_dict[this_year] = CNworkingDays
        
##############################################################################
