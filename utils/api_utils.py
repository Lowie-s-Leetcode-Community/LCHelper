import json

# these include functions to format objects to compatible json, use for public forwarding
def submission_jstr(submission, user, problem, info):
  result = {
    "type": "Submission",
    "content": {
      "submission": submission,
      "user": user,
      "problem": problem,
      "warn": ('Warning: ' + info["warn"]) if info["warn"] else '',
      "is_daily": info["is_daily"],
    }
  }
  return json.dumps(result, default=str)

def crawling_jstrs(all_objects):
  res = []
  for obj in all_objects:
    if obj['ObjType'] == "Submission":
      submission_obj = obj['Obj']
      res.append(submission_jstr(submission_obj['submission'], submission_obj['user'], submission_obj['problem'], submission_obj['info']))
    elif obj['ObjType'] == "UserDailyObject":
      score_obj = obj['Obj']
      delta = score_obj['delta']
      format_date = score_obj['dailyObject']['generatedDate'].strftime("%b %d, %Y")
      reason = f"Practice score on {format_date}: "
      if delta['solvedDaily'] > 0:
        reason += f"{delta['solvedDaily']}x Daily, "
      if delta['solvedEasy'] > 0:
        reason += f"{delta['solvedEasy']}x Easy, "
      if delta['solvedMedium'] > 0:
        reason += f"{delta['solvedMedium']}x Medium, "
      if delta['solvedHard'] > 0:
        reason += f"{delta['solvedHard']}x Hard, "
      reason = reason[:-2]
      res.append(score_update_jstr(score_obj['user']['discordId'], delta['scoreEarned'], reason))
    else:
      res.append(json.dumps(obj, default=str))
  return res

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
