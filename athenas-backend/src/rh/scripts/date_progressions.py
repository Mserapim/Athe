from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from contrib.daterange import NewDateRange


def to_date(dt, days=0):
    _days = days
    start_date = dt
    end_progression = dt + relativedelta(years=1, days=-1)
    drp = NewDateRange(dt, end_progression)
    print(f">> PERIODO AQUISITIVO PREVISTO: {drp}")
    print(f">> DIAS SUSPENSÃO: {days}")
    print("> PRORROGAÇÕES: ")
    start_date = end_progression + relativedelta(days=1)
    dtr1 = NewDateRange()
    while _days > 0:
        end_date = start_date + timedelta(days=_days - 1)
        if end_date.year > start_date.year:
            end_date = date(start_date.year, 12, 31)
        dtr = NewDateRange(start_date, end_date)
        dtr1 += dtr
        _days -= dtr.days
        start_date = dtr.last + timedelta(days=1)
        print(f"> {dtr}: {_days}")
    if dtr1:
        print(f"PERIODO AQUISITIVO: {dtr1 + drp}")
    print(f"PROXIMA PROGRESSÃO: {start_date}")
