from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar


def is_last_day_of_month(date: datetime):
    # Get the last day of the month for the given date
    last_day = calendar.monthrange(date.year, date.month)[1]
    # Check if the date's day is the last day of the month
    return date.day == last_day


def get_next_quarter_dates(date: datetime):
    # Determine the next quarter's starting month
    current_quarter_start_month = ((date.month - 1) // 3) * 3 + 1
    next_quarter_start_month = current_quarter_start_month + 3 if current_quarter_start_month < 10 else 1
    
    # Handle year rollover
    year = date.year if next_quarter_start_month > 1 else date.year + 1
    
    # Start date of the next quarter
    start_date = datetime(year, next_quarter_start_month, 1)
    
    # End date of the next quarter
    end_month = next_quarter_start_month + 2
    last_day = calendar.monthrange(year, end_month)[1]
    end_date = datetime(year, end_month, last_day)
    
    return start_date, end_date