from sqlalchemy import create_engine, select, insert, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from typing import Optional
import os
from utils.llc_datetime import get_first_day_of_previous_month, get_first_day_of_current_month, get_today
import database_api_layer.models as db
from utils.logger import Logger
from database_api_layer.db_utils import get_min_available_id, get_multiple_available_id

class DatabaseAPILayer:
  engine = None
  def __init__(self, client):
    dbschema = os.getenv('POSTGRESQL_SCHEMA')
    self.engine = create_engine(
      os.getenv('POSTGRESQL_CRED'), 
      connect_args={'options': '-csearch_path={}'.format(dbschema)}, echo=True)
    self.client = client
    self.logger = Logger(client)
  
  # Generalize all session commits behavior
  async def commit(self, session, context):
    result = None
    try:
      session.commit()
    except Exception as e:
      await self.logger.on_db_update(False, context, e)
      result = False
    else:
      await self.logger.on_db_update(True, context, "")
      result = True
    print(f"~~konichiiwa~~ commit: {context}, result: {result}")
    return

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
  def read_gimme(self, lc_query):
    # getting the choices, including difficulty, premium, included tags, excluded tags
    difficulty = ""
    if 'difficulty' in lc_query: difficulty = lc_query['difficulty']
    premium = False
    if 'premium' in lc_query: premium = lc_query['premium']
    tags_1 = []
    tags_2 = []
    if 'topics' in lc_query:
      if '$all' in lc_query['topics']:
        tags_1.extend(lc_query['topics']['$all'])
      if '$not' in lc_query['topics']:
        tags_2.extend(lc_query['topics']['$not']['$all'])
        
    # query the database, filter difficulty and premium
    if difficulty != "" :
      query = select(db.Problem).where(
        db.Problem.difficulty == difficulty,
        db.Problem.isPremium == premium
      ).order_by(db.Problem.id)
    else :
      query = select(db.Problem).where(
        db.Problem.isPremium == premium
      ).order_by(db.Problem.id)
    result = []
    
    with Session(self.engine) as session:
      queryResult = session.execute(query).all()

      # filter tags
      for res in queryResult:
        topic_list = []
        for topic in res.Problem.topics:
          topic_list.append(topic.topicName)
          
        test = False
        for tag in tags_1:
          if topic_list.count(tag) == 0: test = True

        for tag in tags_2:
          if topic_list.count(tag) > 0: test = True
        
        if test : continue
        result.append(res.Problem)
    
    return result


  # Desc: update to DB and send a log
  def update_score(self, memberDiscordId, delta):
    return {}

  # Can we split this fn into 2?
  async def create_user(self, user_obj):
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
          submissionId=-1
        )
        new_user.userSolvedProblems.append(user_solved_problem)
        idx += 1
      session.add(new_user)
      result = new_user.id
      await self.commit(session, "User")

    return { "id": result }

  async def create_monthly_object(self, userId, firstDayOfMonth):
    with Session(self.engine) as session:
      new_obj = db.UserMonthlyObject(
        id=get_min_available_id(session, db.UserMonthlyObject),
        userId=userId,
        firstDayOfMonth=firstDayOfMonth,
        scoreEarned=0
      )
      session.add(new_obj)
      result = new_obj.id
      await self.commit(session, f"UserMonthlyObject<id:{result}>")

    return { "id": result }

  def read_problems_all(self):
    query = select(db.Problem).order_by(db.Problem.id)
    result = []
    with Session(self.engine) as session:
      queryResult = session.execute(query).all()
      for res in queryResult:
        result.append(res.Problem.__dict__)
    return result

  async def create_problem(self, problem):
    topic_list = list(map(lambda topic: topic['name'], problem['topicTags']))
    query = select(db.Topic).filter(db.Topic.topicName.in_(topic_list))
    with Session(self.engine) as session:
      queryResult = session.execute(query).all()
      print(queryResult)
      new_obj = db.Problem(
        id=get_min_available_id(session, db.Problem),
        title=problem['title'],
        titleSlug=problem['titleSlug'],
        difficulty=problem['difficulty'],
        isPremium=problem['paidOnly'],
        topics=[row.Topic for row in queryResult]
      )

      session.add(new_obj)
      result = new_obj.id
      await self.commit(session, f"Problem<id:{result}>")

    return { "id": result }

## Features to be refactoring
# tasks
# gimme

# onboard info - need database
#

# qa
