from datetime import datetime, timedelta
import pytz

weeksday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def get_date_from_timestamp(ts):
  current_utc_time = datetime.fromtimestamp(ts).astimezone(pytz.utc)
  result = current_utc_time.date()

  return result

def get_today():
  current_utc_time = datetime.now(pytz.utc)
  result = current_utc_time.date()
  return result

def get_fdom_by_datestamp(datestamp):
  monday = datestamp - timedelta(days=datestamp.weekday())
  day_in_week_1 = datetime(monday.year, monday.month, 7)
  result = day_in_week_1 - timedelta(days=day_in_week_1.weekday())

  return result.date()

def get_first_day_of_current_month():
  return get_fdom_by_datestamp(get_today())

def get_first_day_of_previous_month():
  current_first_day = get_first_day_of_current_month()
  monday = current_first_day - timedelta(days=7)
  day_in_week_1 = datetime(monday.year, monday.month, 7)
  result = day_in_week_1 - timedelta(days=day_in_week_1.weekday())

  return result.date()

def get_weekday():
  currentDate = datetime.utcnow()
  weekday = currentDate.weekday()
  weekDayInChar = weeksday[weekday]
  return weekDayInChar

