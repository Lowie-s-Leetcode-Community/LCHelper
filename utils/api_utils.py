import json

def submission_jstr(submission_obj):
  result = {
    "type": "Submission",
    "content": submission_obj
  }
  return json.dumps(result)

def score_update_jstr(daily_obj):
  result = {
    "type": "Score",
    "content": daily_obj
  }
  return json.dumps(result)
