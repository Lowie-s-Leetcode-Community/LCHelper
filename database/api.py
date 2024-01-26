########################### Testing-zone ##########################

from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session
import database.models as db

dbschema='lc_db'

engine = create_engine(
  "postgresql://postgres:12345678@localhost:5432/lc_db", 
  connect_args={'options': '-csearch_path={}'.format(dbschema)}, echo=True)
session = Session(engine)

def getLatestDaily():
  dbObject = select(db.DailyObject).order_by(db.DailyObject.id.desc()).limit(1)
  daily = session.scalars(dbObject).one()
  result = daily.__dict__
  problem = daily.problem

  print(problem.topics)

  result["problem"] = problem.__dict__
  result["problem"]["topics"] = list(map(lambda topic: topic.topicName, problem.topics))

  return result
