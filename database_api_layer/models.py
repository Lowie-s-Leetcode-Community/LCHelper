from __future__ import annotations

from typing import List, Optional
from sqlalchemy import ForeignKey, Column, String, Integer, Table, Boolean, DateTime, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

_ProblemToTopic = Table(
  "_ProblemToTopic",
  Base.metadata,
  Column("A", ForeignKey("Problem.id")),
  Column("B", ForeignKey("Topic.id")),
)

_MissionToProblem = Table(
  "_MissionToProblem",
  Base.metadata,
  Column("A", ForeignKey("Mission.id")),
  Column("B", ForeignKey("Problem.id")),
)

class User(Base):
    __tablename__ = "User"
    id = mapped_column(Integer, primary_key=True)
    createdAt = mapped_column(DateTime, insert_default=func.now())
    updatedAt = mapped_column(DateTime, insert_default=func.now(), onupdate=func.now())
    discordId = mapped_column(String, nullable=False, unique=True)
    leetcodeUsername = mapped_column(String, nullable=False, unique=True)
    mostRecentSubId = mapped_column(Integer)
    userSolvedProblems: Mapped[List[UserSolvedProblem]] = relationship(back_populates="user")
    userDailyObjects: Mapped[List[UserDailyObject]] = relationship(back_populates="user")
    userMonthlyObjects: Mapped[List[UserMonthlyObject]] = relationship(back_populates="user")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, discordId={self.discordId!r}, leetcodeUsername={self.leetcodeUsername!r})"

class Problem(Base):
    __tablename__ = "Problem"
    id = mapped_column(Integer, primary_key=True)
    createdAt = mapped_column(DateTime, insert_default=func.now())
    updatedAt = mapped_column(DateTime, insert_default=func.now(), onupdate=func.current_timestamp())
    title = mapped_column(String, nullable=False)
    titleSlug = mapped_column(String, nullable=False)
    difficulty = mapped_column(String, nullable=False)
    isPremium = mapped_column(Boolean, nullable=False)
    dailyObjects: Mapped[List[DailyObject]] = relationship(back_populates="problem")
    userSolvedProblems: Mapped[List[UserSolvedProblem]] = relationship(back_populates="problem")
    topics: Mapped[List[Topic]] = relationship(secondary=_ProblemToTopic, back_populates="problems")
    missions: Mapped[List[Mission]] = relationship(secondary=_MissionToProblem, back_populates="problems")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return f"Problem(id={self.id!r}, title={self.title!r}, titleSlug={self.titleSlug!r}, difficulty={self.difficulty!r})"

class UserSolvedProblem(Base):
    __tablename__ = "UserSolvedProblem"
    id = mapped_column(Integer, primary_key=True)
    createdAt = mapped_column(DateTime, insert_default=func.now())
    updatedAt = mapped_column(DateTime, insert_default=func.now(), onupdate=func.now())
    submissionId = mapped_column(Integer)
    problemId = mapped_column(Integer, ForeignKey("Problem.id"))
    userId = mapped_column(Integer, ForeignKey("User.id"))
    problem: Mapped[Problem] = relationship(back_populates="userSolvedProblems")
    user: Mapped[User] = relationship(back_populates="userSolvedProblems")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Topic(Base):
    __tablename__ = "Topic"
    id = mapped_column(Integer, primary_key=True)
    createdAt = mapped_column(DateTime, insert_default=func.now())
    updatedAt = mapped_column(DateTime, insert_default=func.now(), onupdate=func.current_timestamp())
    topicName = mapped_column(String, unique=True)
    problems: Mapped[List[Problem]] = relationship(secondary=_ProblemToTopic, back_populates="topics")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return f"Topic(id={self.id!r}, topicName={self.topicName!r})"

class DailyObject(Base):
    __tablename__ = "DailyObject"
    id = mapped_column(Integer, primary_key=True)
    createdAt = mapped_column(DateTime, insert_default=func.now())
    updatedAt = mapped_column(DateTime, insert_default=func.now(), onupdate=func.current_timestamp())
    problemId = mapped_column(Integer, ForeignKey("Problem.id"))
    generatedDate = mapped_column(Date)
    problem: Mapped[Problem] = relationship(back_populates="dailyObjects")
    userDailyObjects: Mapped[List[UserDailyObject]] = relationship(back_populates="dailyObject")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class UserDailyObject(Base):
    __tablename__ = "UserDailyObject"
    id = mapped_column(Integer, primary_key=True)
    createdAt = mapped_column(DateTime, insert_default=func.now())
    updatedAt = mapped_column(DateTime, insert_default=func.now(), onupdate=func.current_timestamp())

    userId = mapped_column(Integer, ForeignKey("User.id"))
    dailyObjectId = mapped_column(Integer, ForeignKey("DailyObject.id"))
    solvedDaily = mapped_column(Integer, default=0)
    solvedEasy = mapped_column(Integer, default=0)
    solvedMedium = mapped_column(Integer, default=0)
    solvedHard = mapped_column(Integer, default=0)
    scoreEarned = mapped_column(Integer, default=0)
    scoreGacha = mapped_column(Integer, default=-1)
    dailyObject: Mapped[DailyObject] = relationship(back_populates="userDailyObjects")
    user: Mapped[User] = relationship(back_populates="userDailyObjects")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class UserMonthlyObject(Base):
    __tablename__ = "UserMonthlyObject"
    id = mapped_column(Integer, primary_key=True)
    createdAt = mapped_column(DateTime, insert_default=func.now())
    updatedAt = mapped_column(DateTime, insert_default=func.now(), onupdate=func.current_timestamp())
    userId = mapped_column(Integer, ForeignKey("User.id"))
    scoreEarned = mapped_column(Integer)
    firstDayOfMonth = mapped_column(Date)
    user: Mapped[User] = relationship(back_populates="userMonthlyObjects")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Mission(Base):
    __tablename__ = "Mission"
    id = mapped_column(Integer, primary_key=True)
    createdAt = mapped_column(DateTime, insert_default=func.now())
    updatedAt = mapped_column(DateTime, insert_default=func.now(), onupdate=func.current_timestamp())
    name = mapped_column(String)
    description = mapped_column(String)
    rewardImageURL: Mapped[Optional[str]]
    isHidden = mapped_column(Boolean)
    problems: Mapped[List[Problem]] = relationship(secondary=_MissionToProblem, back_populates="missions")

    def __repr__(self) -> str:
        return f"Mission(id={self.id!r}, name={self.name!r}, description={self.description!r}, isHidden={self.isHidden!r})"

class DiscordQuiz(Base):
    __tablename__ = "DiscordQuiz"
    id = mapped_column(Integer, primary_key=True)
    createdAt = mapped_column(DateTime, insert_default=func.now())
    updatedAt = mapped_column(DateTime, insert_default=func.now(), onupdate=func.current_timestamp())
    category = mapped_column(String)
    question = mapped_column(String)
    difficulty = mapped_column(String)
    correctAnswerId = mapped_column(Integer)
    discordQuizAnswer: Mapped[List[DiscordQuizAnswer]] = relationship(back_populates="discordQuiz")

class DiscordQuizAnswer(Base):
    __tablename__ = "DiscordQuizAnswer"
    id = mapped_column(Integer, primary_key=True)
    createdAt = mapped_column(DateTime, insert_default=func.now())
    updatedAt = mapped_column(DateTime, insert_default=func.now(), onupdate=func.current_timestamp())
    answer = mapped_column(String)
    discordQuizId = mapped_column(Integer, ForeignKey("DiscordQuiz.id"))
    discordQuiz: Mapped[DiscordQuiz] = relationship(back_populates="discordQuizAnswer")

class SystemConfiguration(Base):
    __tablename__ = "SystemConfiguration"
    id = mapped_column(Integer, primary_key=True)
    serverId = mapped_column(String)
    verifiedRoleId = mapped_column(String)
    unverifiedRoleId = mapped_column(String)
    timeBeforeKick = mapped_column(Integer)
    dailySolveScore = mapped_column(Integer, default=2)
    easySolveScore = mapped_column(Integer, default=1)
    mediumSolveScore = mapped_column(Integer, default=2)
    hardSolveScore = mapped_column(Integer, default=3)
    practiceScoreCap = mapped_column(Integer, default=6)
    streakBonus = mapped_column(Integer, default=4)
    submissionChannelId = mapped_column(String)
    scoreLogChannelId = mapped_column(String)
    dailyThreadChannelId = mapped_column(String)
    devErrorLogId = mapped_column(String)
    databaseLogId = mapped_column(String)
    backupChannelId = mapped_column(String)
    eventLoggingId = mapped_column(String)
    contestAlertId = mapped_column(String)
    contestRoleId = mapped_column(String)
    dailyDiscussionChannelId = mapped_column(String)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class ContestConfiguration(Base):
    __tablename__ = "ContestConfiguration"
    id = mapped_column(Integer, primary_key=True)
    weeklyContestId = mapped_column(Integer)
    biweeklyContestId = mapped_column(Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
