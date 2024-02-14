from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from typing import Optional
import os
from utils.llc_datetime import get_first_day_of_previous_month, get_first_day_of_current_month, get_today, get_fdom_by_datestamp
import database_api_layer.models as db
from utils.logger import Logger
from typing import Optional, List
from database_api_layer.db_utils import get_min_available_id, get_multiple_available_id
from sqlalchemy.exc import SQLAlchemyError
import utils.api_utils as api_utils
import asyncio
import json
import database_api_layer.controllers as ctrlers

# API Access layer are to format data get from controllers to front-end
# It calculates inputs to request through controllers and process their outputs to the command lines
# Private fn are indicated by prefix __
# One command/automation fn = one db session open
# Only __commit when all the writings has been made

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

  def __calculate_submission_infos(self, session: Session, user_daily_obj: db.UserDailyObject, daily: db.DailyObject, problem: db.Problem):
    score = 0
    warn = None
    is_daily = False

    if daily.problemId == problem.id:
      score = 2
      is_daily = True
      if (user_daily_obj.solvedDaily or 0) >= 1:
        score = 0
        warn = "Daily points have already been counted"
    else:
      practice_cap = self.client.config['practiceScoreCap']
      easy_score = self.client.config['easySolveScore']
      medium_score = self.client.config['mediumSolveScore']
      hard_score = self.client.config['hardSolveScore']
      practice_earned = (user_daily_obj.solvedEasy or 0) * easy_score + (user_daily_obj.solvedMedium or 0) * medium_score + (user_daily_obj.solvedHard or 0) * hard_score
      practice_earned = min(practice_earned, practice_cap)
      problem_score = 1
      if problem.difficulty == "Medium":
        problem_score = 2
      elif problem.difficulty == "Hard":
        problem_score = 3
      score = min(practice_cap - practice_earned, problem_score)
      if (score == 0):
        warn = "Point cap reached"
    return { "score": score, "is_daily": is_daily, "difficulty": problem.difficulty, "warn": warn }

  async def register_new_submission(self, userId: int, problemId: int, submission: dict, dailyObjectId: dict):
    with Session(self.engine, autoflush=False) as session:
      user_solved_problem_controller = ctrlers.UserSolvedProblemController()
      user_daily_object_controller = ctrlers.UserDailyObjectController()
      user_controller = ctrlers.UserController()

      daily_object = ctrlers.DailyObjectController().read_one_or_latest(session, id=dailyObjectId)
      problem = ctrlers.ProblemController().read_one(session, problemId=problemId)
      user = user_controller.read_one(session, userId=userId)

      old_submission = user_solved_problem_controller.read_one(session, userId, problemId)
      user_daily_object = user_daily_object_controller.read_or_create_one(session, userId, dailyObjectId)
      sub_info = self.__calculate_submission_infos(session, user_daily_object, daily_object, problem)

      problem_type = "Daily" if sub_info["is_daily"] else sub_info["difficulty"]
      if (not sub_info["is_daily"]) and old_submission != None:
        return
      if old_submission == None:
        user_solved_problem_controller.create_one(session, userId, problemId, submission['id'])
      user_daily_object_controller.update_one(session, userId, dailyObjectId,
        scoreEarnedDelta=sub_info["score"], solvedDailyDelta=int(problem_type == "Daily"),
        solvedEasyDelta=int(problem_type == "Easy"), solvedMediumDelta=int(problem_type == "Medium"),
        solvedHardDelta=int(problem_type == "Hard"), scoreGacha=-1)
      await self.__commit(session, "UserSolvedProblem",\
        api_utils.submission_jstr(submission, user.as_dict(), problem.as_dict(), sub_info))
    return

  # def __update_user_sub_id(self, session, userId, submissionId: int):
  #   update_query = update(db.User)\
  #     .where(db.User.id == userId)\
  #     .values(mostRecentSubId = submissionId)
  #   session.execute(update_query)
  #   return
  
  # def __read_user_from_id(self, session, userId):
  #   query = select(db.User)\
  #     .where(db.User.id == userId)
  #   user = session.scalars(query).one_or_none()
  #   if user == None:
  #     return {}
  #   return user.as_dict()

  # def __read_problem_from_id(self, session, problemId):
  #   query = select(db.Problem)\
  #     .where(db.Problem.id == problemId)
  #   problem = session.scalars(query).one_or_none()
  #   if problem == None:
  #     return {}
  #   result = problem.as_dict()
  #   result["topics"] = list(map(lambda topic: topic.topicName, problem.topics))
  #   return result

  # def __read_user_monthly_object(self, session, userId, firstDayOfMonth = get_first_day_of_current_month()):
  #   query = select(db.UserMonthlyObject)\
  #     .where(db.UserMonthlyObject.userId == userId)\
  #     .where(db.UserMonthlyObject.firstDayOfMonth == firstDayOfMonth)
  #   obj = session.scalars(query).one_or_none()
  #   return obj

  # def __read_user_daily_object(self, session, userId, dailyObjectId = None):
  #   if dailyObjectId == None:
  #     query = select(db.DailyObject).order_by(db.DailyObject.id.desc()).limit(1)
  #     dailyObj = session.scalars(query).one()
  #     dailyObjectId = dailyObj.id
  #   query = select(db.UserDailyObject)\
  #     .where(db.UserDailyObject.userId == userId)\
  #     .where(db.UserDailyObject.dailyObjectId == dailyObjectId)
  #   obj = session.scalars(query).one_or_none()
  #   return obj
  
  # def __read_latest_daily_object(self, session):
  #   query = select(db.DailyObject).order_by(db.DailyObject.id.desc()).limit(1)
  #   daily = session.scalars(query).one()
  #   return daily

  # def __read_daily_object(self, session, date = get_today()):
  #   try:
  #     query = select(db.DailyObject).where(db.DailyObject.generatedDate == date)
  #     daily = session.scalars(query).one()
  #   except:
  #     daily = self.__read_latest_daily_object(session)
  #     print(f"Daily object at ({date}) not found. Using DailyObj from {str(daily.generatedDate)}")
  #   return daily

  # def read_user_progress(self, memberDiscordId: str):
  #   query = select(db.User).where(db.User.discordId == memberDiscordId)
  #   with Session(self.engine) as session:
  #     user = session.scalars(query).one_or_none()
  #     monthly_obj = self.__read_user_monthly_object(session, user.id)
  #     daily_obj = self.__read_daily_object(session)
  #     daily_obj_id = daily_obj.id
  #     user_daily_obj = self.__read_user_daily_object(session, user.id, daily_obj_id)
  #     result = {
  #       "user_daily": user_daily_obj.as_dict(),
  #       "monthly": monthly_obj.as_dict(),
  #       "daily": daily_obj.as_dict(),
  #       "user": user.as_dict()
  #     }
  #   return result

  # Infos to be added:
  # - # Comm members solves
  def read_latest_daily_object(self):
    with Session(self.engine) as session:
      daily_object_controller = ctrlers.DailyObjectController()
      daily = daily_object_controller.read_latest(session=session)
      problem = daily.problem
      result = daily.as_dict()
      result["problem"] = problem.as_dict()
      result["problem"]["topics"] = list(map(lambda topic: topic.topicName, problem.topics))
    return result

  async def create_or_keep_daily_object(self, problemId, date):
    with Session(self.engine, autoflush=False) as session:
      daily_object_controller = ctrlers.DailyObjectController()
      current_daily = daily_object_controller.read_latest(session=session)
      result = current_daily.as_dict()
      if current_daily.generatedDate != date:
        new_obj = daily_object_controller.create(session=session, problemId=problemId, date=date)
        session.add(new_obj)
        result = new_obj.as_dict()
      await self.__commit(session, f"DailyObject", result)
    return result

  # # We disable getting data from random user for now.
  # def read_profile(self, memberDiscordId: str):
  #   query = select(db.User).where(db.User.discordId == memberDiscordId)
  #   result = None
  #   with Session(self.engine) as session:
  #     profile = session.scalars(query).one_or_none()
  #     if profile == None:
  #       return None
  #     # try to optimize using sql filter next time! filter by python is very unoptimized!
  #     daily_objs = list(filter(lambda obj: obj.dailyObject.generatedDate == get_today(), profile.userDailyObjects))

  #     result = profile.__dict__
  #     if len(daily_objs) == 0:
  #       result['daily'] = {
  #         'scoreEarned': 0,
  #         'solvedDaily': 0,
  #         'solvedEasy': 0,
  #         'solvedMedium': 0,
  #         'solvedHard': 0,
  #         'rank': "N/A"
  #       }
  #     else:
  #       result['daily'] = daily_objs[0].__dict__
  #       result['daily']['rank'] = "N/A"

  #     monthly_objs = list(filter(lambda obj: obj.firstDayOfMonth == get_first_day_of_current_month(), profile.userMonthlyObjects))
  #     if len(monthly_objs) == 0:
  #       result['monthly'] = {
  #         'scoreEarned': 0,
  #         'rank': "N/A"
  #       }
  #     else:
  #       result['monthly'] = monthly_objs[0].__dict__
  #       result['monthly']['rank'] = "N/A"

  #   result['link'] = f"https://leetcode.com/{profile.leetcodeUsername}"
  #   return result

  # Currently, just return user with a monthly object
  def read_current_month_leaderboard(self):
    result = []
    with Session(self.engine) as session:
      leaderboard_controller = ctrlers.LeaderboardController()
      query_result = leaderboard_controller.read_monthly(session=session)
      for res in query_result:
        result.append({**res.User.as_dict(), **res.UserMonthlyObject.as_dict()})
    return result

  def read_last_month_leaderboard(self):
    result = []
    with Session(self.engine) as session:
      leaderboard_controller = ctrlers.LeaderboardController()
      query_result = leaderboard_controller.read_monthly(
        session=session,
        fdom=get_first_day_of_previous_month()
      )
      for res in query_result:
        result.append({**res.User.as_dict(), **res.UserMonthlyObject.as_dict()})
    return result

  def read_daily_object(self, date):
    result = {}
    with Session(self.engine) as session:
      daily_object_controller = ctrlers.DailyObjectController()
      daily = daily_object_controller.read_one_or_latest(session=session, date=date)
      result = daily.as_dict()
    return result
  # # Desc: return one random problem, with difficulty filter + tags filter
  # def read_gimme(self, lc_query):
  #   # getting the choices, including difficulty, premium, included tags, excluded tags
  #   difficulty = ""
  #   if 'difficulty' in lc_query: difficulty = lc_query['difficulty']
  #   premium = False
  #   if 'premium' in lc_query: premium = lc_query['premium']
  #   tags_1 = []
  #   tags_2 = []
  #   if 'topics' in lc_query:
  #     if '$all' in lc_query['topics']:
  #       tags_1.extend(lc_query['topics']['$all'])
  #     if '$not' in lc_query['topics']:
  #       tags_2.extend(lc_query['topics']['$not']['$all'])
  #   # query the database, filter difficulty and premium
  #   if difficulty != "" :
  #     query = select(db.Problem).where(
  #       db.Problem.difficulty == difficulty,
  #       db.Problem.isPremium == premium
  #     ).order_by(db.Problem.id)
  #   else :
  #     query = select(db.Problem).where(
  #       db.Problem.isPremium == premium
  #     ).order_by(db.Problem.id)
  #   result = []
    
  #   with Session(self.engine) as session:
  #     queryResult = session.execute(query).all()
  #     # filter tags
  #     for res in queryResult:
  #       topic_list = []
  #       for topic in res.Problem.topics:
  #         topic_list.append(topic.topicName)
  #       result.append(res.Problem)
  #   return result

  # # Desc: update to DB and send a log
  # async def update_score(self, memberDiscordId: str, delta, reason):
  #   find_user_query = select(db.User).where(db.User.discordId == memberDiscordId)
  #   result = None
  #   with Session(self.engine) as session:
  #     daily = self.__read_daily_object(session)
  #     user = session.scalars(find_user_query).one()
  #     result = self.__update_user_score(session, user.id, daily.as_dict(), delta)

  #     await self.__commit(session, "UserDailyObject",\
  #       api_utils.score_update_jstr(memberDiscordId, delta, reason))
  #   return result

  # # 90% same as fn above but also update gacha column
  # async def update_gacha_score(self, memberDiscordId: str, delta):
  #   find_user_query = select(db.User).where(db.User.discordId == memberDiscordId)
  #   result = None
  #   reason = "Gacha roll!"
  #   with Session(self.engine) as session:
  #     daily = self.__read_daily_object(session)
  #     user = session.scalars(find_user_query).one()
  #     result = self.__update_user_score(session, user.id, daily.as_dict(), delta)
  #     update_query = update(db.UserDailyObject)\
  #       .where(db.UserDailyObject.userId == user.id)\
  #       .where(db.UserDailyObject.dailyObjectId == daily.id)\
  #       .values(scoreGacha = delta)
  #     session.execute(update_query)
  #     status = await self.__commit(session, "UserDailyObject",\
  #       api_utils.score_update_jstr(memberDiscordId, delta, reason))
  #     res = {
  #       "result": result,
  #       "status": status
  #     }
  #   return res

  # # Can we split this fn into 2?
  # async def create_user(self, user_obj):
  #   problems = user_obj['userSolvedProblems']
  #   problems_query = select(db.Problem).filter(db.Problem.titleSlug.in_(problems))
  #   with Session(self.engine, autoflush=False) as session:
  #     queryResult = session.execute(problems_query).all()
  #     min_available_user_id = get_min_available_id(session, db.User)
  #     new_user = db.User(
  #       id=min_available_user_id,
  #       discordId=user_obj['discordId'],
  #       leetcodeUsername=user_obj['leetcodeUsername'],
  #       mostRecentSubId=user_obj['mostRecentSubId'],
  #       userSolvedProblems=[]
  #     )
  #     available_solved_problem_ids = get_multiple_available_id(session, db.UserSolvedProblem, len(queryResult))
  #     idx = 0
  #     for problem in queryResult:
  #       user_solved_problem = db.UserSolvedProblem(
  #         id=available_solved_problem_ids[idx],
  #         problemId=problem.Problem.id,
  #         submissionId=-1
  #       )
  #       new_user.userSolvedProblems.append(user_solved_problem)
  #       idx += 1
  #     session.add(new_user)
  #     result = new_user.id
  #     await self.__commit(session, "User", "[]")

  #   return { "id": result }

  # async def create_user_monthly_object(self, userId, firstDayOfMonth):
  #   with Session(self.engine, autoflush=False) as session:
  #     new_obj = db.UserMonthlyObject(
  #       id=get_min_available_id(session, db.UserMonthlyObject),
  #       userId=userId,
  #       firstDayOfMonth=firstDayOfMonth,
  #       scoreEarned=0
  #     )
  #     session.add(new_obj)
  #     result = new_obj.id
  #     await self.__commit(session, f"UserMonthlyObject<id:{result}>", "[]")
  #   return { "id": result }

  def read_problems_all(self):
    result = []
    with Session(self.engine) as session:
      problem_controller = ctrlers.ProblemController()
      result = list(map(lambda x: x.as_dict(), problem_controller.read_many(session=session)))
    return result
  
  def read_problem_from_slug(self, titleSlug):
    with Session(self.engine) as session:
      problem_controller = ctrlers.ProblemController()
      problem = problem_controller.read_one(session=session, titleSlug=titleSlug)
      if problem == None:
        return None

      result = problem.as_dict()
    return result

  async def create_problems(self, problems_list: List[dict]):
    result = []
    with Session(self.engine, autoflush=False) as session:
      problem_controller = ctrlers.ProblemController()
      for problem in problems_list:
        topic_list = list(map(lambda topic: topic['name'], problem['topicTags']))
        prob = problem_controller.create_one(
          session,
          title=problem['title'],
          titleSlug=problem['titleSlug'],
          difficulty=problem['difficulty'],
          isPremium=problem['paidOnly'],
          topics=topic_list
        )
        result.append(prob.as_dict())
      # TODO: format result to json to commit
      await self.__commit(session, f"Problem<count:{len(result)}>", "[]")
    return result

  def read_latest_configs(self):
    with Session(self.engine) as session:
      sys_conf_controller = ctrlers.SystemConfigurationController()
      queryResult = sys_conf_controller.read_latest(session=session)
      cfg = queryResult.as_dict()
    return cfg

  async def update_submission_channel(self, new_channel_id: str):
    result = {}
    with Session(self.engine) as session:
      sys_conf_controller = ctrlers.SystemConfigurationController()
      result = sys_conf_controller.update(session=session, submissionChannelId=new_channel_id)
      result = result.SystemConfiguration.as_dict()
      await self.__commit(session, "SystemConfiguration", result)
    return result

  async def update_score_channel(self, new_channel_id: str):
    result = {}
    with Session(self.engine) as session:
      sys_conf_controller = ctrlers.SystemConfigurationController()
      result = sys_conf_controller.update(session=session, scoreLogChannelId=new_channel_id)
      result = result.SystemConfiguration.as_dict()
      await self.__commit(session, "SystemConfiguration", result)
    return result
