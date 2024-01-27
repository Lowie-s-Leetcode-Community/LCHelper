########################### Testing-zone ##########################

from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
import database_api_layer.models as db
from typing import Optional

class DatabaseAPILayer:
  engine = None
  def __init__(self):
    dbschema='lc_db'
    self.engine = create_engine(
      "postgresql://postgres:12345678@localhost:5432/lc_db", 
      connect_args={'options': '-csearch_path={}'.format(dbschema)}, echo=True)

  # Missing infos in SQL comparing to previous features:
  # - AC Count & Rate
  # - Like & Dislike
  # Infos to be added:
  # - # Comm members solves
  def getLatestDaily(self):
    query = select(db.DailyObject).order_by(db.DailyObject.id.desc()).limit(1)
    result = None
    with Session(self.engine) as session:
      daily = session.scalars(query).one()
      result = daily.__dict__
    problem = daily.problem

    result["problem"] = problem.__dict__
    result["problem"]["topics"] = list(map(lambda topic: topic.topicName, problem.topics))

    return result

  # We disable getting data from random user for now.
  # Will need another class only with function to call
  def getProfile(self, member):
    query = select(db.User).where(db.User.discordId == member)
    profile = None
    with Session(self.engine) as session:
      profile = session.scalars(query).one_or_none()
    if profile == None:
      return None
    result = profile.__dict__
    
    monthly_data = {
      'score': 0,
      'rank': 69
    }
    daily_data = {
      'scoreEarned': 0,
      'solvedDaily': 0,
      'solvedEasy': 0,
      'solvedMedium': 0,
      'solvedHard': 0,
      'rank': 69
    }
    # TODO: write command to get today daily, monthly
    # case: daily, monthly not generated (case user haven't do anything)

    result['daily'] = daily_data
    result['monthly'] = monthly_data
    result['link'] = f"https://leetcode.com/{profile.leetcodeUsername}"
    return result

  # Stub, need to move somewhere else also
  def getFirstDayOfMonth(self):
    return '2024-01-01'

  # Currently, just return user with a monthly object
  def getCurrentMonthLeaderboard(self):
    query = select(db.UserMonthlyObject, db.User).join_from(
      db.UserMonthlyObject, db.User).where(
      db.UserMonthlyObject.firstDayOfMonth == self.getFirstDayOfMonth()
    ).order_by(db.UserMonthlyObject.scoreEarned.desc())
    result = []
    with Session(self.engine) as session:
      queryResult = session.execute(query).all()
      for res in queryResult:
        result.append({**res.User.__dict__, **res.UserMonthlyObject.__dict__})
    return result

db_api = DatabaseAPILayer()

## Features to be refactoring
# tasks
# gimme

# onboard info - need database
#

# qa
