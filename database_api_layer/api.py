from sqlalchemy import create_engine, select, insert, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from typing import Optional
import os
from utils.llc_datetime import get_first_day_of_previous_month, get_first_day_of_current_month, get_today
import database_api_layer.models as db
from database_api_layer.db_utils import get_min_available_id, get_multiple_available_id

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
  def read_latest_daily(self):
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
  def read_profile(self, memberDiscordId):
    query = select(db.User).where(db.User.discordId == memberDiscordId)
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
  def read_current_month_leaderboard(self):
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
  
  def read_last_month_leaderboard(self):
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
  def read_gimme(self, difficulty, tags_1, tags_2, premium = False):
    return {}

  # Desc: update to DB and send a log
  def update_score(self, memberDiscordId, delta):
    return {}

  def create_user(self, user_obj):
    problems = user_obj['userSolvedProblems']
    problems_query = select(db.Problem).filter(db.Problem.titleSlug.in_(problems))
    with Session(self.engine) as session:
      queryResult = session.execute(problems_query).all()
      min_available_user_id = get_min_available_id(session, db.User)
      new_user = db.User(
        id=min_available_user_id,
        discordId=user_obj['discordId'],
        leetcodeUsername=user_obj['leetcodeUsername'],
        mostRecentSubId=user_obj['mostRecentSubId'],
        userSolvedProblems=[]
      )
      available_solved_problem_ids = get_multiple_available_id(session, db.UserSolvedProblem, len(queryResult))
      idx = 0
      for problem in queryResult:
        user_solved_problem = db.UserSolvedProblem(
          id=available_solved_problem_ids[idx],
          problemId=problem.Problem.id,
          submissionId=123
        )
        new_user.userSolvedProblems.append(user_solved_problem)
        idx += 1
      session.add(new_user)
      result = new_user.id
      session.commit()

    return { "id": result }

db_api = DatabaseAPILayer()
## Features to be refactoring
# tasks
# gimme

# onboard info - need database
#

# qa
