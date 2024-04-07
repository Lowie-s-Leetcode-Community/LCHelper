import random

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from typing import Optional
from datetime import datetime
import asyncio
import json
import os
from utils.llc_datetime import get_first_day_of_previous_month, get_first_day_of_current_month, get_today, get_fdom_by_datestamp
import database_api_layer.models as db
from utils.logger import Logger
from typing import Optional, List
from sqlalchemy.exc import SQLAlchemyError
import utils.api_utils as api_utils

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
      connect_args={'options': '-csearch_path={}'.format(dbschema)},
      pool_recycle=480) # 8 minutes, the estimate 
    self.client = client
    self.logger = Logger(client)
  
  # Generalize all session commits behavior
  async def __commit(self, session, context, json_str_desc: str = None, array_desc: List[str] = None):
    result = None
    try:
      session.commit()
    except Exception as e:
      obj = { "action": json_str_desc[:200], "error": e }
      if json_str_desc != None:
        await self.logger.on_db_update(False, context, json.dumps(obj, default=str))
      else:
        await self.logger.on_db_update(False, context, json.dumps(obj, default=str))
      result = False
    else:
      if json_str_desc != None:
        await self.logger.on_db_update(True, context, json_str_desc)
        result = True
      else:
        for obj in array_desc:
          await self.logger.on_db_update(True, context, obj)
        result = True
    return result

  def read_all_users(self):
    result = []
    with Session(self.engine) as session:
      user_controller = ctrlers.UserController()
      all_users = user_controller.read_all(session)
      result = list(map(lambda res: res.as_dict(), all_users))
    return result
  
  def __calculate_daily_object_delta(self, session: Session, user: db.User, daily_object: db.DailyObject,
      user_daily_object: db.UserDailyObject, submissions_list: List[dict]):
    result = {
      "scoreEarned": 0,
      "scorePractice": 0,
      "solvedEasy": 0,
      "solvedMedium": 0,
      "solvedHard": 0,
      "solvedDaily": 0,
      "warn": ""
    }
    score_config = {
      "practiceCap": self.client.config['practiceScoreCap'],
      "Easy": self.client.config['easySolveScore'],
      "Medium": self.client.config['mediumSolveScore'],
      "Hard": self.client.config['hardSolveScore'],
      "Daily": self.client.config['dailySolveScore']
    }
    recorded_practice = (user_daily_object.solvedEasy or 0) * score_config["Easy"] \
      + (user_daily_object.solvedMedium or 0) * score_config["Medium"] \
      + (user_daily_object.solvedHard or 0) * score_config["Hard"]
    recorded_practice = min(recorded_practice, score_config["practiceCap"])
    daily_problem_id = daily_object.problemId
    problem_controller = ctrlers.ProblemController()
    for submission in submissions_list:
      problem = problem_controller.read_one(session, titleSlug=submission['titleSlug'])
      problem_type = ""
      if problem.id == daily_problem_id:
        problem_type = "Daily"
        result["solvedDaily"] = 1
        result["scoreEarned"] += score_config["Daily"]
        if (user_daily_object.solvedDaily or 0) >= 1:
          result["solvedDaily"] = 0
          result["scoreEarned"] -= score_config["Daily"]
          result["warn"] += "Daily points have already been counted\n"
      else:
        problem_type = problem.difficulty
        # Assuming had filtered all older submission
        # "Easy", "Medium", "Hard"
        result[f"solved{problem_type}"] += 1
        result["scoreEarned"] += score_config[problem_type]
        result["scorePractice"] += score_config[problem_type]
    total_practice = recorded_practice + result["scorePractice"]
    if total_practice > score_config["practiceCap"]:
      gamma = total_practice - score_config["practiceCap"]
      result["scorePractice"] -= gamma
      result["scoreEarned"] -= gamma
      result["warn"] += f"Practice surpassed cap {gamma} pts."
    return result

  async def register_new_crawl(self, submissions_blob: dict):
    result = [] # list of new submissions object
    with Session(self.engine, autoflush=False) as session:
      daily_object_controller = ctrlers.DailyObjectController()
      user_controller = ctrlers.UserController()
      user_daily_object_controller = ctrlers.UserDailyObjectController()
      user_monthly_object_controller = ctrlers.UserMonthlyObjectController()
      user_solved_problem_controller = ctrlers.UserSolvedProblemController()
      problem_controller = ctrlers.ProblemController()

      # iterates through each month
      for fdom_f, fdom_blob in submissions_blob.items():
        fdom_d = datetime.strptime(fdom_f, "%Y-%m-%d")
        user_score_earned_delta = {}

        # iterates through each day
        for daily_f, daily_blob in fdom_blob.items():
          daily_d = datetime.strptime(daily_f, "%Y-%m-%d")
          daily_object = daily_object_controller.read_one(session, date=daily_d)

          # if can't found daily object, best practice is to just skip
          if daily_object == None:
#            print(f"Daily object for {daily_f} not found. Skipping...")
            continue

          # iterates through each users
          for username, submissions in daily_blob.items():
            user = user_controller.read_one(session, leetcodeUsername=username)

            user_monthly_object = user_monthly_object_controller.read_one(session, user.id, fdom_d)
            if user_monthly_object == None:
              # ignore this, most probably because:
              # - monthly create is bugged
              # - user haven't join before this submission
              continue
            user_daily_object = user_daily_object_controller.read_or_create_one(session, user.id, daily_object.id)
            filtered_submissions = []
            # first O(n) loop, to compare new list to database
            for sub in submissions:
              problem = problem_controller.read_one(session, titleSlug=sub['titleSlug'])
              if problem == None:
                continue
              user_solved_problem = user_solved_problem_controller.read_one(session, user.id, problem.id)
              if daily_object.problemId != problem.id and user_solved_problem != None:
                # submission is already recorded and no point of keeping track of more
                continue
              filtered_submissions.append(sub)
            # second O(n) loop, to calculate score changes
            daily_delta = self.__calculate_daily_object_delta(session, user, daily_object, user_daily_object, filtered_submissions)
            # third O(n) loop, to save submissions to db and add logs
            for sub in filtered_submissions:
              problem = problem_controller.read_one(session, titleSlug=sub['titleSlug'])
              submission = None
              user_solved_problem = user_solved_problem_controller.read_one(session, user.id, problem.id)
              if user_solved_problem == None:
                submission = user_solved_problem_controller.create_one(session, user.id, problem.id, int(sub['id']))
              if problem.id != daily_object.problemId or user_daily_object.solvedDaily == 0 or user_daily_object.solvedDaily == None: # hasn't registered daily submission yet
                obj = {
                  "submission": sub,
                  "user": user.as_dict(),
                  "problem": problem.as_dict(),
                  "info": {
                    "warn": daily_delta['warn'],
                    "is_daily": problem.id == daily_object.problemId
                  }
                }
                obj["problem"]["topics"] = [topic.topicName for topic in problem.topics]
                result.append({ "ObjType": "Submission", "Obj": obj})
            # update and append changes to daily objects
            daily_if_update = daily_delta['scoreEarned'] + daily_delta['solvedDaily'] + daily_delta['solvedEasy'] + daily_delta['solvedMedium'] + daily_delta['solvedHard']
            if daily_if_update:
              user_daily_object_controller.update_one(
                session=session, userId=user.id, dailyObjectId=daily_object.id,
                scoreEarnedDelta=daily_delta['scoreEarned'], solvedDailyDelta=daily_delta['solvedDaily'],
                solvedEasyDelta=daily_delta['solvedEasy'], solvedMediumDelta=daily_delta['solvedMedium'],
                solvedHardDelta=daily_delta['solvedHard']
              )
              obj = {
                "user": user.as_dict(),
                "dailyObject": daily_object.as_dict(),
                "delta": daily_delta,
              }
              result.append({ "ObjType": "UserDailyObject", "Obj": obj})
            # update and append changes to monthly objects
            if str(user.id) in user_score_earned_delta:
              user_score_earned_delta[str(user.id)] += daily_delta['scoreEarned']
            else:
              user_score_earned_delta[str(user.id)] = daily_delta['scoreEarned']

        # loop to update monthly objects, accumulated from daily deltas
        for userIdStr, scoreEarnedDelta in user_score_earned_delta.items():
          if scoreEarnedDelta <= 0:
            continue

          monthly_obj = user_monthly_object_controller.update_one(
            session=session, userId=int(userIdStr), fdom=fdom_d, scoreEarnedDelta=scoreEarnedDelta
          )
          result.append({ "ObjType": "UserMonthlyObject", "Obj": monthly_obj.as_dict()})
      await self.__commit(session, "RegisterNewCrawl", array_desc=api_utils.crawling_jstrs(result))
    return result

  def read_user_progress(self, memberDiscordId: str):
    with Session(self.engine) as session:
      user = ctrlers.UserController().read_one(session, discordId=memberDiscordId)
      monthly_obj = ctrlers.UserMonthlyObjectController().read_one(session, user.id)
      daily_obj = ctrlers.DailyObjectController().read_one_or_latest(session, date=get_today())
      user_daily_obj = ctrlers.UserDailyObjectController().read_or_create_one(session, user.id, daily_obj.id)
      result = {
        "user_daily": user_daily_obj.as_dict(),
        "monthly": monthly_obj.as_dict(),
        "daily": daily_obj.as_dict(),
        "user": user.as_dict()
      }
    return result

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
      await self.__commit(session, f"DailyObject", json.dumps(result, default=str))
    return result

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

  # Desc: return one random problem, with difficulty filter + tags filter
  def read_gimme(self, lc_query):
    result = []
    with Session(self.engine) as session:
      difficulty = None
      if 'difficulty' in lc_query: difficulty = lc_query['difficulty']
      premium = False
      if 'premium' in lc_query: premium = lc_query['premium']
      problems = ctrlers.ProblemController().read_many(session, difficulty, premium)
      topics_to_include = []
      topics_to_exclude = []
      if 'topics' in lc_query:
        if '$all' in lc_query['topics']:
          topics_to_include.extend(lc_query['topics']['$all'])
        if '$not' in lc_query['topics']:
          topics_to_exclude.extend(lc_query['topics']['$not']['$all'])
      for problem in problems:
        problem_topics = [topic.topicName for topic in problem.topics]
        sat = True
        for topic_name in topics_to_include:
          if topic_name not in problem_topics:
            sat = False
        for topic_name in topics_to_exclude:
          if topic_name in problem_topics:
            sat = False
        if sat:
          prob = problem.as_dict()
          prob["topics"] = list(map(lambda topic: topic.topicName, problem.topics))
          result.append(prob)
    return result

  def read_quiz(self, quiz_detail):
    quiz = []
    with Session(self.engine) as session:
      difficulty = None
      category = None

      if 'difficulty' in quiz_detail: difficulty = quiz_detail['difficulty']
      if 'category' in quiz_detail: category = quiz_detail['category']

      result = ctrlers.QuizController().read_many(session, difficulty, category)

      if len(result) == 0:
        return []
      question = result[random.randint(0, len(result) - 1)]

      quiz.append(question)
      quiz.append(ctrlers.QuizController().read_quiz_answer(session, question.id))
    return quiz


  # Desc: update to DB and send a log message (reason)
  async def update_score(self, memberDiscordId: str, delta: int, reason: str):
    result = {}
    with Session(self.engine) as session:
      user = ctrlers.UserController().read_one(session, discordId=memberDiscordId)
      daily_obj = ctrlers.DailyObjectController().read_one(session, date=get_today())

      user_daily_object = ctrlers.UserDailyObjectController().update_one(
        session, user.id, daily_obj.id, scoreEarnedDelta=delta
      )
      monthly_obj = ctrlers.UserMonthlyObjectController().update_one(
        session, user.id, get_fdom_by_datestamp(get_today()), delta
      )

      result = {"daily": user_daily_object.as_dict(), "monthly": monthly_obj.as_dict()}
      await self.__commit(session, "Scoring",\
        api_utils.score_update_jstr(memberDiscordId, delta, reason))
    return result

  async def update_gacha_score(self, memberDiscordId: str, delta: int):
    result = {}
    with Session(self.engine) as session:
      user = ctrlers.UserController().read_one(session, discordId=memberDiscordId)
      daily_obj = ctrlers.DailyObjectController().read_one(session, date=get_today())

      user_daily_object = ctrlers.UserDailyObjectController().update_one(
        session, user.id, daily_obj.id, scoreEarnedDelta=delta, scoreGacha=delta  
      )
      monthly_obj = ctrlers.UserMonthlyObjectController().update_one(
        session, user.id, get_fdom_by_datestamp(get_today()), delta
      )

      result = {"daily": user_daily_object.as_dict(), "monthly": monthly_obj.as_dict()}
      await self.__commit(session, "Scoring",\
        api_utils.score_update_jstr(memberDiscordId, delta, "Gacha roll!"))
    return result

  def read_profile(self, memberDiscordId: str):
    result = None
    with Session(self.engine) as session:
      user_controller = ctrlers.UserController()

      user = user_controller.read_one(session, discordId=memberDiscordId)
      if user == None:
        return None

      result = user.as_dict()
      daily_object = ctrlers.DailyObjectController().read_one_or_latest(session, date=get_today())
      user_daily_object = ctrlers.UserDailyObjectController().read_one(
        session, user.id, daily_object.id
      )
      if user_daily_object == None:
        result['daily'] = {
          'scoreEarned': 0,
          'solvedDaily': 0,
          'solvedEasy': 0,
          'solvedMedium': 0,
          'solvedHard': 0,
          'rank': "N/A"
        }
      else:
        result['daily'] = user_daily_object.as_dict()
        result['daily']['rank'] = "N/A"

      user_monthly_object = ctrlers.UserMonthlyObjectController().read_one(
        session, user.id
      )
      if user_monthly_object == None:
        result['monthly'] = {
          'scoreEarned': 0,
          'rank': "N/A"
        }
      else:
        result['monthly'] = user_monthly_object.as_dict()
        result['monthly']['rank'] = "N/A"
      result['link'] = f"https://leetcode.com/{user.leetcodeUsername}"
    return result

  async def create_user(self, user_obj: dict):
    result = {}
    with Session(self.engine, autoflush=False) as session:
      user_controller = ctrlers.UserController()
      user = user_controller.create_one(
        session,
        user_obj['leetcodeUsername'],
        user_obj['discordId'],
        user_obj['mostRecentSubId']
      )
      result = user.as_dict()

      user_monthly_object_controller = ctrlers.UserMonthlyObjectController()
      user_monthly_object = user_monthly_object_controller.create_one(
        session, user.id
      )
      await self.__commit(session, "User", json.dumps(result, default=str))
    return result

  async def refresh_server_scores(self, firstDayOfMonth: datetime.date):
    with Session(self.engine, autoflush=False) as session:
      user_controller = ctrlers.UserController()
      user_monthly_object_controller = ctrlers.UserMonthlyObjectController()

      all_users = user_controller.read_all(session)
      for user in all_users:
        user_monthly_object_controller.create_one(
          session, user.id, firstDayOfMonth
        )
      await self.__commit(session, f"UserMonthlyObject<count:{len(all_users)}>", "[]")
    return

  async def purge_left_members(self, current_users_list: List[str]):
    result = []
    with Session(self.engine, autoflush=False) as session:
      user_controller = ctrlers.UserController()
      left_users = user_controller.read_left_users(session, current_users_list)
      print([user.id for user in left_users])
      for user in left_users:
        user_controller.remove_one(session, user.id)
        result.append(user)
      await self.__commit(session, f"Users<delete_count:{len(result)}>", "[]")
    return result

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
