from datetime import datetime, timedelta
import pytz

def get_date_from_timestamp(ts):
  current_utc_time = datetime.fromtimestamp(ts)
  result = current_utc_time.date()

  return result

def get_today():
  current_utc_time = datetime.now(pytz.utc)
  result = current_utc_time.date()
  return result

def get_fdom_by_timestamp(dtime):
  monday = dtime.astimezone(pytz.utc) - timedelta(days=dtime.weekday())
  day_in_week_1 = datetime(monday.year, monday.month, 7)
  result = day_in_week_1 - timedelta(days=day_in_week_1.weekday())

  return result.date()

def get_first_day_of_current_month():
  return get_fdom_by_timestamp(datetime.now(pytz.utc))

def get_first_day_of_previous_month():
  current_first_day = get_first_day_of_current_month()
  monday = current_first_day - timedelta(days=7)
  day_in_week_1 = datetime(monday.year, monday.month, 7)
  result = day_in_week_1 - timedelta(days=day_in_week_1.weekday())

  return result.date()
