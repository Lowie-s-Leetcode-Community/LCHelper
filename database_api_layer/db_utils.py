from sqlalchemy import select, insert, func

def get_min_available_id(session, Table):
  min_available_id = (
    session.query(func.min(Table.id + 1))
      .filter(~(Table.id + 1).in_(session.query(Table.id)))
      .scalar()
  )
  return min_available_id or 1

def get_multiple_available_id(session, Table, limit):
  min_available_id = (
    session.query(func.min(Table.id + 1).label("min_id"))
      .filter(~(Table.id + 1).in_(session.query(Table.id)))
      .all()
  )
  result = list(map(lambda x: x.min_id, min_available_id))
  while len(result) < limit:
    result.append(result[-1] + 1)
  return result[:limit]
