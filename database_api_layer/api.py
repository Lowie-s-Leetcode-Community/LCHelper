########################### Testing-zone ##########################

from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session
import database_api_layer.models as db
from typing import Optional

class DatabaseAPILayer:
  engine = None
  session = None
  def __init__(self):
    dbschema='lc_db'
    self.engine = create_engine(
      "postgresql://postgres:12345678@localhost:5432/lc_db", 
      connect_args={'options': '-csearch_path={}'.format(dbschema)}, echo=True)
    self.session = Session(self.engine)

  # Missing infos in SQL comparing to previous features:
  # - AC Count & Rate
  # - Like & Dislike
  # Infos to be added:
  # - # Comm members solves
  def getLatestDaily(self):
    dbObject = select(db.DailyObject).order_by(db.DailyObject.id.desc()).limit(1)
    daily = self.session.scalars(dbObject).one()
    result = daily.__dict__
    problem = daily.problem

    result["problem"] = problem.__dict__
    result["problem"]["topics"] = list(map(lambda topic: topic.topicName, problem.topics))

    return result

  # We disable getting data from random user for now.
  # Will need another class only with function to call
  def getProfile(self, member):
    dbObject = select(db.User).where(db.User.discordId == member)
    profile = self.session.scalars(dbObject).one()

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

  def getLeaderboard():
    return {}

db_api = DatabaseAPILayer()
# test = DatabaseAPILayer()
# print(test.getProfile("318049602160951297"))
## Features to be refactoring

# leaderboard

# tasks
# gimme

# onboard info - need database
#

# qa
