from datetime import datetime, timedelta
import pytz
def get_today():
  current_utc_time = datetime.now(pytz.utc)
  result = current_utc_time.date()
  # for debugging
  fake_today = datetime(2024, 1, 17, 0, 0, 0)
  result = fake_today.date()
  return result

def get_first_day_of_current_month():
  today = datetime.now()
  monday = today - timedelta(days=today.weekday())
  day_in_week_1 = datetime(monday.year, monday.month, 7)
  result = day_in_week_1 - timedelta(days=day_in_week_1.weekday())

  return result.date()

def get_first_day_of_previous_month():
  current_first_day = get_first_day_of_current_month()
  monday = current_first_day - timedelta(days=7)
  day_in_week_1 = datetime(monday.year, monday.month, 7)
  result = day_in_week_1 - timedelta(days=day_in_week_1.weekday())

  return result.date()