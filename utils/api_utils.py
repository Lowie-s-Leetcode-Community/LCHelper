import json

# these include functions to format objects to compatible json, use for public forwarding
def submission_jstr(submissionId, userId, problemId, warn, is_daily):
  result = {
    "type": "Submission",
    "content": {
      "submissionId": submissionId,
      "userId": userId,
      "problemId": problemId,
      "warn": ('Warning: ' + warn) if warn else '',
      "is_daily": is_daily
    }
  }
  return json.dumps(result)

def score_update_jstr(memberDiscordId, delta, reason):
  result = {
    "type": "Score",
    "content": {
      "member_mention": f"<@{memberDiscordId}>",
      "delta": delta,
      "reason": reason
    }
  }
  return json.dumps(result)
