import discord
from utils.asset import Assets

class SubmissionEmbed(discord.Embed):
  def __init__(self, user: dict, problem: dict, submission: dict):
    embed_color = Assets.easy if problem['difficulty'] == 'Easy' else Assets.medium if problem['difficulty'] == 'Medium' else Assets.hard
    submission_str = f"▸ **Submitted:** <t:{int(submission['timestamp'])}:R>"
    if submission['is_daily']:
      submission_str = "▸ 🗓️ **Daily challenge**\n" + submission_str
    super().__init__(
      title = f"[SOLVED] **{problem['id']}. {problem['title']}**",
      description = submission_str,
      url = f"https://leetcode.com/problems/{problem['titleSlug']}",
      color = embed_color
    )
    discord_mention = f"<@{user['discordId']}>"
    self.add_field(
      name = "Author",
      value = discord_mention
    )
    self.add_field(
      name = "Problem difficulty",
      value = problem['difficulty'],
    )
    self.add_field(
      name = "Topics",
      value = f"|| {', '.join(problem['topics'])} ||",
    )
    self.add_field(
      name = "Submission",
      value = f"[Check out the solution!](https://leetcode.com/submissions/detail/{submission['id']})"
    )
    leetcode_username = user['leetcodeUsername']
    leetcode_url = f"https://leetcode.com/{leetcode_username}"
    self.set_author(
      name = f"Author: {leetcode_username}",
      icon_url = "https://assets.leetcode.com/users/leetcode/avatar_1568224780.png",
      url = leetcode_url
    )
    # user = await self.client.fetch_user(int(user['discordId']))
    avatar_url = "https://assets.leetcode.com/users/leetcode/avatar_1568224780.png"
    if user['avatar'] != None:
        avatar_url = user['avatar'].url
    self.set_thumbnail(
        url = avatar_url
    )
