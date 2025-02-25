import datetime

import discord

from utils.asset import Assets


class ContestEmbed(discord.Embed):
    def __init__(self, contest: dict):
        id = contest["contestId"]
        c_type = contest["type"]
        url = f"https://leetcode.com/contest/{c_type}-contest-{id}/"
        ts = datetime.datetime.fromtimestamp(int(contest["timestamp"]))
        is_future_contest = ts > datetime.datetime.now()
        super().__init__(
            title=f"{c_type.capitalize()} Contest {id}",
            url=url,
            color=Assets.medium if is_future_contest else Assets.easy,
        )
        desc = f"{Assets.leetcode} [Join now]({url}) to win amazing prizes, such at goodies and [LeetCoins](https://leetcode.com/store/)!"
        self.add_field(name="Description", value=desc, inline=False)

        formatted_time = ts.strftime("%I:%M %p. %a, %b %d, %Y")

        icon = Assets.hourglass if is_future_contest else Assets.green_tick

        self.add_field(
            name="When?",
            value=f"{icon} {formatted_time}\n(<t:{int(ts.timestamp())}:R>)",
            inline=True,
        )

        self.add_field(name="Duration", value="90 minutes", inline=True)
