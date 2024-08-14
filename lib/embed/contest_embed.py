import datetime
import discord
from utils.asset import Assets

class ContestEmbed(discord.Embed):
  def __init__(self, is_biweekly: bool, contest: dict):
    # print(contest)
    c_type = "Biweekly" if is_biweekly else "Weekly"
    id = contest["contestId"]
    url = f"https://leetcode.com/contest/{c_type.lower()}-contest-{id}/"
    super().__init__(
      title=f"{c_type} Contest {id}",
      url=url,
      color=Assets.medium
    )
    desc = "This LeetCode contest is sponsored by LeetCode. Join now to win amazing prizes, such at goodies and [LeetCoins](https://leetcode.com/store/)!"
    self.add_field(
      name="Description",
      value=desc,
      inline = False
    )

    ts = datetime.datetime.fromtimestamp(int(contest['timestamp']))
    formatted_time = ts.strftime("%I:%M %p. %a, %b %d, %Y")

    self.add_field(
      name="When?",
      value=f"{formatted_time}\n(<t:{int(ts.timestamp())}:R>)",
      inline=True
    )

    self.add_field(
      name="Sign up",
      value=f"[Click here to sign up!]({url})",
      inline=True
    )
