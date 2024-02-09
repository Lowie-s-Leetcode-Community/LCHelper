import json

# these include functions to format objects to compatible json, use for public forwarding
def submission_jstr(submission, user, problem, info):
  problem_type = "Daily" if info["is_daily"] else info["difficulty"]
  score_obj = {
    "mention": f"<@{user['discordId']}>",
    "delta": info["score"],
    "reason": f"New AC submission: {problem_type}"
  }
  result = {
    "type": "Submission",
    "content": {
      "submission": submission,
      "user": user,
      "problem": problem,
      "warn": ('Warning: ' + info["warn"]) if info["warn"] else '',
      "is_daily": info["is_daily"],
      "score": score_obj
    }
  }
  return json.dumps(result, default=str)

def score_update_jstr(memberDiscordId, delta, reason):
  result = {
    "type": "Score",
    "content": {
      "member_mention": f"<@{memberDiscordId}>",
      "delta": delta,
      "reason": reason
    }
  }
  return json.dumps(result, default=str)
