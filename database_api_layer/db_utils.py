from sqlalchemy import select, func
from sqlalchemy.orm.state import InstanceState

def count_obj_in_session(session, Table):
  count = 0
  for obj in session.new:
    if isinstance(obj, Table):
      count += 1
  return count

def get_min_available_id(session, Table):
  table_name = Table.__table__.name
  if not hasattr(session, "db_remaining_ids"):
    session.db_remaining_ids = {}
  if table_name not in session.db_remaining_ids:
    query = select((Table.id + 1).label("min_id"))\
      .where(~(Table.id + 1).in_(select(Table.id)))
    session.db_remaining_ids[table_name] = list(map(lambda x: x.min_id, session.execute(query).all()))
  rank = count_obj_in_session(session, Table) + 1
  while rank > len(session.db_remaining_ids[table_name]):
    session.db_remaining_ids[table_name].append(session.db_remaining_ids[table_name][-1] + 1)
  return session.db_remaining_ids[table_name][rank - 1]
