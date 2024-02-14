from sqlalchemy import select, insert, func, update, inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound, MultipleResultsFound, SQLAlchemyError
from typing import Optional, List
import os
from utils.llc_datetime import get_first_day_of_current_month
import database_api_layer.models as db
from database_api_layer.db_utils import get_min_available_id, get_multiple_available_id
from datetime import datetime, date

# Controllers are responsible for direct interact with daily and returns the correct
# model object to each sessions
# Controllers shouldn't handle the logic

class DailyObjectController:
  def read_latest(self, session):
    query = select(db.DailyObject).order_by(db.DailyObject.id.desc()).limit(1)
    daily = session.scalars(query).one()
    return daily

  # return daily object, or None
  # can't raise MultipleResultFound since the db has unique tupple
  def read_one(self, session: Session, id: Optional[int] = None, date: Optional[date] = None):
    query = select(db.DailyObject)
    if id != None:
      query = query.where(db.DailyObject.id == id)
    elif date != None:
      query = query.where(db.DailyObject.generatedDate == date)
    
    daily = session.scalar(query)
    return daily
  
  # return only daily
  def read_one_or_latest(self, session: Session, id: Optional[int] = None, date: Optional[date] = None):
    result = self.read_one(session=session, id=id, date=date)
    if result == None:
      result = self.read_latest(session=session)
    return result

  def create(self, session: Session, problemId: int, date: date):
    new_obj = db.DailyObject(
      id=get_min_available_id(session, db.DailyObject),
      problemId=problemId,
      generatedDate=date
    )
    session.add(new_obj)
    # session.refresh(new_obj)
    return new_obj

class UserDailyObjectController:
  # can't raise MultipleResultFound since the db has unique tupple
  def read_one(self, session: Session, userId: int, dailyObjectId: int):
    query = select(db.UserDailyObject)\
      .where(db.UserDailyObject.dailyObjectId == dailyObjectId)\
      .where(db.UserDailyObject.userId == userId)
    result = session.scalar(query)
    return result
  
  # same as above, but will create and return if no result is found
  # inspect(result) should be persistent or 
  # according to: https://docs.sqlalchemy.org/en/20/orm/session_state_management.html
  def read_or_create_one(self, session: Session, userId: int, dailyObjectId: int):
    result = self.read_one(session=session, userId=userId, dailyObjectId=dailyObjectId)
    if result == None:
      result = db.UserDailyObject(
        id=get_min_available_id(session, db.UserDailyObject),
        userId=userId,
        dailyObjectId=dailyObjectId
      )
      added = False
      for obj in session.new:
        if isinstance(obj, db.UserDailyObject):
          if obj.userId == result.userId and obj.dailyObjectId == result.dailyObjectId:
            added = True
      if not added:
        session.add(result)
    return result

  # update and divide into cases, whether the object is new or persistent
  def update_one(self, session: Session, userId: int, dailyObjectId: int, scoreEarnedDelta: int,\
      solvedDailyDelta: Optional[int], solvedEasyDelta: Optional[int], solvedMediumDelta: Optional[int],\
      solvedHardDelta: Optional[int], scoreGacha: Optional[int]):
    result = self.read_or_create_one(session=session, userId=userId, dailyObjectId=dailyObjectId)
    insp = inspect(result)
    if insp.persistent:
      update_query = update(db.UserDailyObject)\
        .returning(db.UserDailyObject)\
        .where(db.UserDailyObject.userId == userId)\
        .where(db.UserDailyObject.dailyObjectId == dailyObjectId)\
        .values(scoreEarned = result.scoreEarned + scoreEarnedDelta)
      if solvedDailyDelta != None:
        update_query = update_query.values(solvedDaily = result.solvedDaily + solvedDailyDelta)
      if solvedEasyDelta != None:
        update_query = update_query.values(solvedEasy = result.solvedEasy + solvedEasyDelta)
      if solvedMediumDelta != None:
        update_query = update_query.values(solvedMedium = result.solvedMedium + solvedMediumDelta)
      if solvedHardDelta != None:
        update_query = update_query.values(solvedHard = result.solvedHard + solvedHardDelta)
      if scoreGacha != None:
        update_query = update_query.values(scoreGacha = scoreGacha)
      result = session.execute(update_query).one()
    elif insp.pending:
      result.scoreEarned = scoreEarnedDelta
      if solvedEasyDelta != None:
        result.solvedEasy = solvedEasyDelta
      if solvedMediumDelta != None:
        result.solvedMedium = solvedMediumDelta
      if solvedHardDelta != None:
        result.solvedHard = solvedHardDelta
      if scoreGacha != None:
        result.scoreGacha = scoreGacha
    return result

class UserMonthlyObjectController:
  # can't raise MultipleResultFound since the db has unique tupple
  def read_one(self, session: Session, userId: int, fdom: date = get_first_day_of_current_month()):
    query = select(db.UserMonthlyObject)\
      .where(db.UserMonthlyObject.userId == userId)\
      .where(db.UserMonthlyObject.firstDayOfMonth == fdom)
    return session.scalar(query)

  # same as above, but will create and return if no result is found
  # inspect(result) should be persistent or 
  # according to: https://docs.sqlalchemy.org/en/20/orm/session_state_management.html
  def read_or_create_one(self, session: Session, userId: int, fdom: date = get_first_day_of_current_month()):
    result = self.read_one(session=session, userId=userId, fdom=fdom)
    if result == None:
      result = db.UserMonthlyObject(
        id=get_min_available_id(session, db.UserMonthlyObject),
        userId=userId,
        firstDayOfMonth=fdom
      )
      session.add(result)
      # session.refresh(result)
    return result

  def update_one(self, session: Session, userId: int, fdom: date, scoreEarnedDelta: int):
    result = self.read_or_create_one(session=session, userId=userId, dailyObjectId=dailyObjectId)
    insp = inspect(result)
    if insp.persistent:
      update_query = update(db.UserMonthlyObject)\
        .where(db.UserMonthlyObject.userId == userId)\
        .where(db.UserMonthlyObject.firstDayOfMonth == fdom)\
        .values(scoreEarned = result.scoreEarned + scoreEarnedDelta)
      result = session.execute(update_query).one()
    elif insp.pending:
      result.scoreEarned = scoreEarnedDelta
    return result

class UserSolvedProblemController:
  def read_all(self, session: Session, userId: Optional[int], problemId: Optional[int]):
    query = select(db.UserSolvedProblem)
    if userId != None:
      query = query.where(db.UserSolvedProblem.userId == userId)
    if problemId != None:
      query = query.where(db.UserSolvedProblem.problemId == problemId)
    return session.scalars(query).all()

  def read_one(self, session, userId: int, problemId: int):
    query = select(db.UserSolvedProblem)\
      .where(db.UserSolvedProblem.userId == userId)\
      .where(db.UserSolvedProblem.problemId == problemId)
    return session.scalar(query)
  
  def create_one(self, session, userId: int, problemId: int, submissionId: int = -1):
    result = db.UserSolvedProblem(
      id=get_min_available_id(session, db.UserSolvedProblem),
      userId=userId,
      problemId=problemId,
      submissionId=submissionId
    )
    session.add(result)
    return result
  
  def update_one(self, session: Session, userId: int, problemId: int, submissionId: int = -1):
    result = self.read_one(session, userId, problemId)
    if result == None:
      result = self.create_one(session, userId, problemId, submissionId=submissionId)
    else:
      update_query = update(db.UserSolvedProblem)\
        .where(db.UserSolvedProblem.userId == userId)\
        .where(db.UserSolvedProblem.problemId == problemId)\
        .values(submissionId = submissionId)
      result = session.execute(update_query).one()
    return result

class UserController:
  def read_all(self, session: Session):
    query = select(db.User)
    return session.scalars(query).all()

  def read_one(self, session: Session, userId: Optional[int], leetcodeUsername: Optional[str] = None, discordId: Optional[str] = None):
    query = select(db.User)
    if userId != None:
      query = query.where(db.User.id == userId)
    elif leetcodeUsername != None:
      query = query.where(db.User.leetcodeUsername == leetcodeUsername)
    elif discordId != None:
      query = query.where(db.User.discordId == discordId)
    return session.scalar(query)
  
  def create_one(self, session: Session, leetcodeUsername: str, discordId: str, mostRecentSubId: int = -1):
    new_user = db.User(
      id=get_min_available_id(session, db.User),
      discordId=user_obj['discordId'],
      leetcodeUsername=user_obj['leetcodeUsername'],
      mostRecentSubId=user_obj['mostRecentSubId'],
      userSolvedProblems=[]
    )
    session.add(new_user)
    return new_user
  
  def update_one(self, session: Session, userId: Optional[int], leetcodeUsername: Optional[str], discordId: Optional[str], submissionId: int):
    result = self.read_one(session, userId, leetcodeUsername, discordId)
    if read_one == None:
      result = self.create_one(session, leetcodeUsername, discordId, mostRecentSubId = submissionId)
    else:
      update_query = update(db.User)
      if userId != None:
        update_query = update_query.where(db.User.id == userId)
      elif leetcodeUsername != None:
        update_query = update_query.where(db.User.leetcodeUsername == leetcodeUsername)
      elif discordId != None:
        update_query = update_query.where(db.User.discordId == discordId)
      result = session.execute(update_query).one()
    return result

  # def remove_one(self, session: Session):

class TopicController:
  def read_many_in(self, session: Session, topicNames: List[str]):
    query = select(db.Topic).filter(db.Topic.topicName.in_(topicNames))
    return session.execute(query).all()
  
  def create_one(self, session: Session, topicName: str):
    result = db.Topic(
      id=get_min_available_id(session, db.Topic),
      topicName=topicName
    )
    session.add(result)
    return result

class ProblemController:
  def read_one(self, session: Session, problemId: Optional[int] = None, titleSlug: Optional[str] = None):
    query = select(db.Problem)
    if problemId != None:
      query = query.where(db.Problem.id == problemId)
    elif titleSlug != None:
      query = query.where(db.Problem.titleSlug == titleSlug)
    return session.scalar(query)

  # returns many, use for gimme and various stuffs
  def read_many(self, session: Session, difficulty: Optional[str] = None, isPremium: Optional[bool] = None, includedTopics: list = [], excludedTopics: list = []):
    query = select(db.Problem)
    if difficulty != None:
      query = query.where(difficulty == difficulty)
    if isPremium != None:
      query = query.where(isPremium == isPremium)
    query = query.order_by(db.Problem.id)
    return session.scalars(query).all()

  # topics should be a list of topic Names
  def create_one(self, session: Session, title: str, titleSlug: str, difficulty: str, isPremium: bool, topics: List[str]):
    topic_controller = TopicController()
    topics_list = topic_controller.read_many_in(session, topics)
    new_obj = db.Problem(
      id=get_min_available_id(session, db.Problem),
      title=title,
      titleSlug=titleSlug,
      difficulty=difficulty,
      isPremium=isPremium,
      topics=[row.Topic for row in topics_list]
    )
    session.add(new_obj)
    return new_obj

class SystemConfigurationController:
  def read_latest(self, session: Session):
    query = select(db.SystemConfiguration).where(db.SystemConfiguration.id == 1)
    return session.scalar(query)

  def update(self, session: Session, verifiedRoleId: Optional[str] = None,
      unverifiedRoleId: Optional[str] = None, timeBeforeKick: Optional[str] = None,
      dailySolveScore: Optional[int] = None, easySolveScore: Optional[int] = None,
      mediumSolveScore: Optional[int] = None, hardSolveScore: Optional[int] = None,
      practiceScoreCap: Optional[int] = None, streakBonus: Optional[int] = None,
      submissionChannelId: Optional[str] = None, scoreLogChannelId: Optional[str] = None, 
      dailyThreadChannelId: Optional[str] = None, devErrorLogId: Optional[str] = None,
      databaseLogId: Optional[str] = None, backupChannelId: Optional[str] = None,
      eventLoggingId: Optional[str] = None):
    query = update(db.SystemConfiguration).returning(db.SystemConfiguration).where(db.SystemConfiguration.id == 1)
    if verifiedRoleId != None:
      query = query.values(verifiedRoleId = verifiedRoleId)
    if unverifiedRoleId != None:
      query = query.values(unverifiedRoleId = unverifiedRoleId)
    if timeBeforeKick != None:
      query = query.values(timeBeforeKick = timeBeforeKick)
    if dailySolveScore != None:
      query = query.values(dailySolveScore = dailySolveScore)
    if easySolveScore != None:
      query = query.values(easySolveScore = easySolveScore)
    if mediumSolveScore != None:
      query = query.values(mediumSolveScore = mediumSolveScore)
    if hardSolveScore != None:
      query = query.values(hardSolveScore = hardSolveScore)
    if practiceScoreCap != None:
      query = query.values(practiceScoreCap = practiceScoreCap)
    if streakBonus != None:
      query = query.values(streakBonus = streakBonus)
    if submissionChannelId != None:
      query = query.values(submissionChannelId = submissionChannelId)
    if scoreLogChannelId != None:
      query = query.values(scoreLogChannelId = scoreLogChannelId)
    if dailyThreadChannelId != None:
      query = query.values(dailyThreadChannelId = dailyThreadChannelId)
    if devErrorLogId != None:
      query = query.values(devErrorLogId = devErrorLogId)
    if databaseLogId != None:
      query = query.values(databaseLogId = databaseLogId)
    if backupChannelId != None:
      query = query.values(backupChannelId = backupChannelId)
    if eventLoggingId != None:
      query = query.values(eventLoggingId = eventLoggingId)
    return session.execute(query).one()

# Only controller that needs joining :)
class LeaderboardController:
  def read_monthly(self, session: Session, fdom: date = get_first_day_of_current_month()):
    query = select(db.UserMonthlyObject, db.User).join_from(
      db.UserMonthlyObject, db.User).where(
      db.UserMonthlyObject.firstDayOfMonth == fdom
    ).order_by(db.UserMonthlyObject.scoreEarned.desc())
    return session.execute(query).all()

  def read_daily(self, session: Session, dailyObjectId: int):
    query = select(db.UserDailyObject, db.User).join_from(
      db.UserDailyObject, db.User).where(
      db.UserDailyObject.id == dailyObjectId
    ).order_by(db.UserDailyObject.scoreEarned.desc())
    return session.execute(query).all()