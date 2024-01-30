"""Helper Class for date conversions."""
import time
from math import ceil


def current_time_epoch():
    """Returns the current time in epoch format."""
    return int(time.time())

def date_to_epoch(date):
    """Converts a datetime string to epoch time."""
    return int(time.mktime(time.strptime(date, "%Y-%m-%dT%H:%M:%S")))


def epoch_to_date(epoch):
    """Converts an epoch time to a date string."""
    return time.strftime("%d-%m-%Y", time.localtime(epoch))


def extract_quarters_from_date_range(start_date, end_date):
    """Extracts the quarters from a date range maybe from different years."""
    start_quater = ceil(int(start_date.split("-")[1]) / 3)
    years_in_between = int(end_date.split("-")[0]) - int(start_date.split("-")[0])
    end_quater = 4
    quarters = []
    for year in range(years_in_between + 1):
        if year == years_in_between:
            end_quater = ceil(int(end_date.split("-")[1]) / 3)
        for quater in range(start_quater, end_quater + 1):
            quarters.append(f'{year + int(start_date.split("-")[0])}-{quater}')
        start_quater = 1
    return quarters

