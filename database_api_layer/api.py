from sqlalchemy import create_engine, select, insert, func, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from typing import Optional
import os
from utils.llc_datetime import get_first_day_of_previous_month, get_first_day_of_current_month, get_today, get_fdom_by_timestamp
import database_api_layer.models as db
from utils.logger import Logger
from database_api_layer.db_utils import get_min_available_id, get_multiple_available_id
from sqlalchemy.exc import SQLAlchemyError
import utils.api_utils as api_utils
import asyncio
import json

class DatabaseAPILayer:
  engine = None
  def __init__(self, client):
    dbschema = os.getenv('POSTGRESQL_SCHEMA')
    self.engine = create_engine(
      os.getenv('POSTGRESQL_CRED'), 
      connect_args={'options': '-csearch_path={}'.format(dbschema)})
    self.client = client
    self.logger = Logger(client)
  
  # Generalize all session commits behavior
  async def __commit(self, session, context, json_desc):
    result = None
    try:
      session.commit()
    except Exception as e:
      obj = { "action": json_desc, "error": e }
      await self.logger.on_db_update(False, context, json.dump(obj, default=str))
      result = False
    else:
      await self.logger.on_db_update(True, context, json_desc)
      result = True
    return result

  def __calculate_submission_infos(self, userId, dailyObjectId, problemId):
    query1 = select(db.UserDailyObject)\
      .where(db.UserDailyObject.userId == userId)\
      .where(db.UserDailyObject.dailyObjectId == dailyObjectId)
    query2 = select(db.Problem.difficulty)\
      .where(db.Problem.id == problemId)
    query3 = select(db.DailyObject)\
      .where(db.DailyObject.id == dailyObjectId)
    score = 0
    warn = None
    is_daily = False
    with Session(self.engine) as session:
      user_daily_obj = session.execute(query1).one_or_none()
      problem_diff = session.execute(query2).one().difficulty
      daily_obj = session.execute(query3).one()

      if daily_obj.DailyObject.problemId == problemId:
        score = 2
        is_daily = True
        if user_daily_obj != None:
          if user_daily_obj.UserDailyObject.solvedDaily >= 1:
            score = 0
            warn = "Daily points have already been counted"
      else:
        practice_cap = 6
        practice_earned = 0
        if user_daily_obj != None:
          info = user_daily_obj.UserDailyObject
          practice_earned = min(info.solvedEasy * 1 + info.solvedMedium * 2 + info.solvedHard * 3, practice_cap)
        problem_score = 1
        if problem_diff == "Medium":
          problem_score = 2
        elif problem_diff == "Hard":
          problem_score = 3
        score = min(practice_cap - practice_earned, problem_score)
        if (score == 0):
          warn = "Point cap reached"
    return { "score": score, "is_daily": is_daily, "difficulty": problem_diff, "warn": warn }

  def __update_user_score(self, session, userId: int, dailyObject: dict, score: int, problem_type = None):
    user_daily_query = select(db.UserDailyObject)\
      .where(db.UserDailyObject.userId == userId)\
      .where(db.UserDailyObject.dailyObjectId == dailyObject['id'])
    user_daily_obj = session.execute(user_daily_query).one_or_none()

    solvedEasy = 1 if problem_type == "Easy" else 0
    solvedMedium = 1 if problem_type == "Medium" else 0
    solvedHard = 1 if problem_type == "Hard" else 0
    solvedDaily = 1 if problem_type == "Daily" else 0

    if user_daily_obj == None:
      user_daily_obj = db.UserDailyObject(
        id=get_min_available_id(session, db.UserDailyObject),
        userId=userId,
        dailyObjectId=dailyObject['id'],
        scoreEarned=score,
        solvedDaily=solvedDaily,
        solvedEasy=solvedEasy,
        solvedMedium=solvedMedium,
        solvedHard=solvedHard
      )
      session.add(user_daily_obj)
    else:
      update_query = update(db.UserDailyObject)\
        .where(db.UserDailyObject.userId == userId)\
        .where(db.UserDailyObject.dailyObjectId == dailyObject['id'])\
        .values(scoreEarned = user_daily_obj.UserDailyObject.scoreEarned + score)\
        .values(solvedEasy = user_daily_obj.UserDailyObject.solvedEasy + solvedEasy)\
        .values(solvedMedium = user_daily_obj.UserDailyObject.solvedMedium + solvedMedium)\
        .values(solvedHard = user_daily_obj.UserDailyObject.solvedHard + solvedHard)\
        .values(solvedDaily = min(1, user_daily_obj.UserDailyObject.solvedDaily + solvedDaily))
      session.execute(update_query)

    first_day_of_month = get_fdom_by_timestamp(dailyObject['generatedDate'])
    user_monthly_query = select(db.UserMonthlyObject)\
      .where(db.UserMonthlyObject.userId == userId)\
      .where(db.UserMonthlyObject.firstDayOfMonth == first_day_of_month)
    user_monthly_obj = session.execute(user_monthly_query).one_or_none()
    if (user_monthly_obj == None):
      new_obj = db.UserMonthlyObject(
        id=get_min_available_id(session, db.UserMonthlyObject),
        userId=userId,
        firstDayOfMonth=first_day_of_month,
        scoreEarned=score
      )
      session.add(new_obj)
      result = new_obj.id
    else:
      update_query = update(db.UserMonthlyObject)\
        .where(db.UserMonthlyObject.userId == userId)\
        .where(db.UserMonthlyObject.firstDayOfMonth == first_day_of_month)\
        .values(scoreEarned = user_monthly_obj.UserMonthlyObject.scoreEarned + score)
      session.execute(update_query)
    return user_daily_obj
  
  def __create_submission(self, session, userId, problemId, submissionId):
    new_obj = db.UserSolvedProblem(
      id=get_min_available_id(session, db.UserSolvedProblem),
      userId=userId,
      problemId=problemId,
      submissionId=submissionId
    )
    session.add(new_obj)
    return new_obj

  def __update_user_sub_id(self, session, userId, submissionId: int):
    update_query = update(db.User)\
      .where(db.User.id == userId)\
      .values(mostRecentSubId = submissionId)
    session.execute(update_query)
    return
  
  def __read_user_from_id(self, session, userId):
    query = select(db.User)\
      .where(db.User.id == userId)
    user = session.scalars(query).one_or_none()
    if user == None:
      return {}
    return user.as_dict()

  def __read_problem_from_id(self, session, problemId):
    query = select(db.Problem)\
      .where(db.Problem.id == problemId)
    problem = session.scalars(query).one_or_none()
    if problem == None:
      return {}
    result = problem.as_dict()
    result["topics"] = list(map(lambda topic: topic.topicName, problem.topics))
    return result

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
        result.append(res.Problem)
    return result

  # Desc: update to DB and send a log
  async def update_score(self, memberDiscordId, delta, reason):
    find_user_query = select(db.User).where(db.User.discordId == memberDiscordId).limit(1)
    find_daily_object = select(db.DailyObject).order_by(db.DailyObject.id.desc()).limit(1)
    result = None
    with Session(self.engine) as session:
      user = session.execute(find_user_query).one()
      daily = session.scalars(find_daily_object).one().__dict__
      result = self.__update_user_score(session, user.User.id, daily, delta)

      await self.__commit(session, "UserDailyObject",\
        api_utils.score_update_jstr(memberDiscordId, delta, reason))
    return result

  async def register_new_submission(self, userId, problemId, submission, dailyObject):
    sub_info = self.__calculate_submission_infos(userId, dailyObject['id'], problemId)
    sub_query = select(db.UserSolvedProblem)\
      .where(db.UserSolvedProblem.userId == userId)\
      .where(db.UserSolvedProblem.problemId == problemId)
    with Session(self.engine, autoflush=False) as session:
      old_submission = session.execute(sub_query).one_or_none()
      problem_type = "Daily" if sub_info["is_daily"] else sub_info["difficulty"]
      if (not sub_info["is_daily"]) and old_submission != None:
        return
      if old_submission == None:
        self.__create_submission(session, userId, problemId, submission["id"])
      self.__update_user_score(session, userId, dailyObject, sub_info["score"], problem_type)
      self.__update_user_sub_id(session, userId, submission["id"])
      user = self.__read_user_from_id(session, userId)
      problem = self.__read_problem_from_id(session, problemId)
      await self.__commit(session, "UserSolvedProblem",\
        api_utils.submission_jstr(submission, user, problem, sub_info))
    return

  # Can we split this fn into 2?
  async def create_user(self, user_obj):
    problems = user_obj['userSolvedProblems']
    problems_query = select(db.Problem).filter(db.Problem.titleSlug.in_(problems))
    with Session(self.engine, autoflush=False) as session:
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
      await self.__commit(session, "User", "[]")

    return { "id": result }

  async def create_user_monthly_object(self, userId, firstDayOfMonth):
    with Session(self.engine, autoflush=False) as session:
      new_obj = db.UserMonthlyObject(
        id=get_min_available_id(session, db.UserMonthlyObject),
        userId=userId,
        firstDayOfMonth=firstDayOfMonth,
        scoreEarned=0
      )
      session.add(new_obj)
      result = new_obj.id
      await self.__commit(session, f"UserMonthlyObject<id:{result}>", "[]")
    return { "id": result }
  
  async def create_daily_object(self, problemId, date):
    with Session(self.engine, autoflush=False) as session:
      new_obj = db.DailyObject(
        id=get_min_available_id(session, db.DailyObject),
        problemId=problemId,
        generatedDate=date,
        isToday=False
      )
      session.add(new_obj)
      result = new_obj.id
      await self.__commit(session, f"DailyObject<id:{result}, date:{date}>", "[]")
    return { "id": result }

  def read_problems_all(self):
    query = select(db.Problem).order_by(db.Problem.id)
    result = []
    with Session(self.engine) as session:
      queryResult = session.execute(query).all()
      for res in queryResult:
        result.append(res.Problem.__dict__)
    return result
  
  def read_problem_from_slug(self, titleSlug):
    query = select(db.Problem).where(db.Problem.titleSlug == titleSlug)
    with Session(self.engine) as session:
      queryResult = session.execute(query).one_or_none()
      if queryResult == None:
        return None

      result = queryResult.Problem.__dict__
    return result

  def read_daily_object(self, date):
    query = select(db.DailyObject).where(db.DailyObject.generatedDate == date)
    result = None
    with Session(self.engine) as session:
      daily = session.scalars(query).one_or_none()
      if daily == None:
        daily = self.read_latest_daily()
        result = daily
      else:
        result = daily.__dict__

    return result

  async def create_problem(self, problem):
    topic_list = list(map(lambda topic: topic['name'], problem['topicTags']))
    query = select(db.Topic).filter(db.Topic.topicName.in_(topic_list))
    with Session(self.engine, autoflush=False) as session:
      queryResult = session.execute(query).all()
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
      await self.__commit(session, f"Problem<id:{result}>", "[]")

    return { "id": result }

  def read_latest_configs(self):
    query = select(db.SystemConfiguration)\
      .where(db.SystemConfiguration.id == 1)
    with Session(self.engine) as session:
      queryResult = session.scalars(query).one()
      cfg = queryResult.as_dict()
    return cfg

## Features to be refactoring

# onboard info - need database

# qa
