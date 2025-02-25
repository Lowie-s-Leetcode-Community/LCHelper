from datetime import date, datetime, timedelta

import pytz


def get_date_from_timestamp(ts):
    current_utc_time = datetime.fromtimestamp(ts).astimezone(pytz.utc)
    result = current_utc_time.date()

    return result


def get_today():
    current_utc_time = datetime.now(pytz.utc)
    result = current_utc_time.date()
    return result


def get_previous_day():
    today = get_today()
    return today - timedelta(days=1)


class LLCMonth:
    __day__ = None

    def __fdom__(self):
        monday = self.__day__ - timedelta(days=self.__day__.weekday())
        day_in_week_1 = datetime(monday.year, monday.month, 7)
        result = day_in_week_1 - timedelta(days=day_in_week_1.weekday())

        return result.date()

    def __init__(self, datestamp=get_today(), previous=False, next=False):
        self.__day__ = datestamp
        self.__day__ = self.__fdom__()
        # if nothing passes, default to current
        if previous:
            self.__day__ -= timedelta(days=7)
            return
        if next:
            self.__day__ += timedelta(days=42)

    def first_day_of_month(self):
        return self.__fdom__()

    def last_day_of_previous_month(self):
        return self.__fdom__() - timedelta(days=1)

    def month_string(self):
        return self.__fdom__().strftime("%B %Y")

    def format_fdom(self):
        return self.__fdom__().strftime("%d/%m/%y")

    def format_ldom(self):
        return self.last_day_of_previous_month().strftime("%d/%m/%y")

    def date_range(self):
        following_month = LLCMonth(datestamp=self.__day__, next=True)
        return f"({self.format_fdom()} - {following_month.format_ldom()})"


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + timedelta(days_ahead)


def get_next_LLC_week_and_month():
    d = date.today()
    next_mon = next_weekday(d, 0)
    week_no = int((next_mon.day - 1) / 7) + 1
    month_no = next_mon.month
    return week_no, month_no
