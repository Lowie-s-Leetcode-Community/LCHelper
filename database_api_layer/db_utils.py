from sqlalchemy import select, func
from sqlalchemy.orm.state import InstanceState

def get_multiple_available_id(session, Table, limit):
  query = select((Table.id + 1).label("min_id"))\
    .where(~(Table.id + 1).in_(select(Table.id)))
  result = list(map(lambda x: x.min_id, session.execute(query).all()))
  while len(result) < limit:
    result.append(result[-1] + 1)
  return result[:limit]

def get_min_available_id(session, Table, rank = None):
  if rank == None:
    rank = count_obj_in_session(session, Table) + 1
  available_ids = get_multiple_available_id(session, Table, limit=rank)
  return available_ids[-1]

def count_obj_in_session(session, Table):
  count = 0
  for obj in session.new:
    if isinstance(obj, Table):
      count += 1
  return count
