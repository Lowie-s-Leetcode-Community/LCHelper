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

  # Desc: add user basic information into the database
  def add_user(self, user_obj):
    """
    {
      discordId: str
      leetcodeUsername: str
      mostRecentSubId: str
      userSolvedProblems: [...] - next, should optimize info with extra query
    }
    """
    problems = user_obj['userSolvedProblems']
    problems_query = select(db.Problem).filter(db.Problem.titleSlug.in_(problems))
    with Session(self.engine) as session:
      queryResult = session.execute(problems_query).all()

      # have to refactor the "get min id" function to get for later :)
      min_available_user_id = (
        session.query(func.min(db.User.id + 1))
          .filter(~(db.User.id + 1).in_(session.query(db.User.id)))
          .scalar()
      ) or 1

      new_user = db.User(
        id=min_available_user_id,
        discordId=user_obj['discordId'],
        leetcodeUsername=user_obj['leetcodeUsername'],
        mostRecentSubId=user_obj['mostRecentSubId'],
        userSolvedProblems=[]
      )

      available_solved_problem_ids = (
        session.query(func.min(db.UserSolvedProblem.id + 1).label("min_id"))
          .filter(~(db.UserSolvedProblem.id + 1).in_(session.query(db.UserSolvedProblem.id)))
          .all()
      )
      usp_id = 0
      idx = 0
      for problem in queryResult:
        id = usp_id

        if (idx < len(available_solved_problem_ids)):
          id = available_solved_problem_ids[idx].min_id
          usp_id = available_solved_problem_ids[idx].min_id + 1
          idx += 1
        else:
          usp_id += 1
        user_solved_problem = db.UserSolvedProblem(
          id=id,
          problemId=problem.Problem.id,
          submissionId=123
        )
        new_user.userSolvedProblems.append(user_solved_problem)
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
