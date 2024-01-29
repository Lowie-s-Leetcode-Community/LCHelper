from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from typing import Optional
import os
import asyncio
from dotenv import load_dotenv
from utils.llc_datetime import get_first_day_of_previous_month, get_first_day_of_current_month, get_today
import database_api_layer.models as db

class DatabaseAPILayer:
  engine = None
  def __init__(self):
    dbschema = os.getenv('POSTGRESQL_SCHEMA')
    self.engine = create_engine(
      os.getenv('POSTGRESQL_CRED'), 
      connect_args={'options': '-csearch_path={}'.format(dbschema)}, echo=True)

  # Missing infos in SQL comparing to previous features:
  # - AC Count & Rate
  # - Like & Dislike
  # Infos to be added:
  # - # Comm members solves
  def get_latest_daily(self):
    query = select(db.DailyObject).order_by(db.DailyObject.id.desc()).limit(1)
    result = None
    with Session(self.engine) as session:
      daily = session.scalars(query).one()
      problem = daily.problem
      result = daily.__dict__
      result["problem"] = problem.__dict__
      result["problem"]["topics"] = list(map(lambda topic: topic.topicName, problem.topics))
    return result

  # We disable getting data from random user for now.
  def get_profile(self, memberDiscordId):
    query = select(db.User).where(db.User.discordId == memberDiscordId)
    server_count = 192
    result = None
    with Session(self.engine) as session:
      profile = session.scalars(query).one_or_none()
      if profile == None:
        return None
      # try to optimize using sql filter next time! filter by python is very unoptimized!
      daily_objs = list(filter(lambda obj: obj.dailyObject.generatedDate == get_today(), profile.userDailyObjects))

      result = profile.__dict__
      if len(daily_objs) == 0:
        result['daily'] = {
          'scoreEarned': 0,
          'solvedDaily': 0,
          'solvedEasy': 0,
          'solvedMedium': 0,
          'solvedHard': 0,
          'rank': "N/A"
        }
      else:
        result['daily'] = daily_objs[0].__dict__
        result['daily']['rank'] = "N/A"

      monthly_objs = list(filter(lambda obj: obj.firstDayOfMonth == get_first_day_of_current_month(), profile.userMonthlyObjects))
      if len(monthly_objs) == 0:
        result['monthly'] = {
          'scoreEarned': 0,
          'rank': "N/A"
        }
      else:
        result['monthly'] = monthly_objs[0].__dict__
        result['monthly']['rank'] = "N/A"

    result['link'] = f"https://leetcode.com/{profile.leetcodeUsername}"
    return result

  # Currently, just return user with a monthly object
  def get_current_month_leaderboard(self):
    query = select(db.UserMonthlyObject, db.User).join_from(
      db.UserMonthlyObject, db.User).where(
      db.UserMonthlyObject.firstDayOfMonth == get_first_day_of_current_month()
    ).order_by(db.UserMonthlyObject.scoreEarned.desc())
    result = []
    with Session(self.engine) as session:
      queryResult = session.execute(query).all()
      for res in queryResult:
        result.append({**res.User.__dict__, **res.UserMonthlyObject.__dict__})
    return result
  
  def get_last_month_leaderboard(self):
    query = select(db.UserMonthlyObject, db.User).join_from(
      db.UserMonthlyObject, db.User).where(
      db.UserMonthlyObject.firstDayOfMonth == get_first_day_of_previous_month()
    ).order_by(db.UserMonthlyObject.scoreEarned.desc())
    result = []
    with Session(self.engine) as session:
      queryResult = session.execute(query).all()
      for res in queryResult:
        result.append({**res.User.__dict__, **res.UserMonthlyObject.__dict__})
    return result
  
  # Desc: return one random problem, with difficulty filter + tags filter
  def get_gimme(self, difficulty, tags_1, tags_2, premium = False):
    return {}

  # Desc: update to DB and send a log
  def update_score(self, memberDiscordId, delta):
    return {}


db_api = DatabaseAPILayer()
# fake_user = {
#   'discordId': "97813641364873723",
#   'leetcodeUsername': "fakeshit",
#   'mostRecentSubId': 129,
#   'userSolvedProblems': ["median-of-two-sorted-arrays", "longest-palindromic-substring",
#     "two-sum", "search-in-rotated-sorted-array","roman-to-integer","jump-game-ii"
#   ]
# }
# db_api.add_user(fake_user)
## Features to be refactoring
# tasks
# gimme

# onboard info - need database
#

# qa
