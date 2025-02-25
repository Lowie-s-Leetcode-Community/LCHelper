import discord

from utils.asset import Assets
from utils.lc_utils import LC_utils


class ProblemEmbed(discord.Embed):
    def __init__(self, problem: dict):
        super().__init__(
            title=problem["title"],
            url=f"https://leetcode.com/problems/{problem['titleSlug']}",
            color=Assets.easy
            if problem["difficulty"] == "Easy"
            else Assets.medium
            if problem["difficulty"] == "Medium"
            else Assets.hard,
        )
        info = None
        try:
            info = LC_utils.get_problem_info(problem["titleSlug"])
        except Exception:
            print(f"Can't get information for problem {problem['titleSlug']}")

        self.add_field(
            name="Difficulty",
            value=problem["difficulty"],
            inline=True,
        )
        if info is not None:
            self.add_field(
                name="AC Count",
                value=f"{info['total_AC']}/{info['total_submissions']}",
                inline=True,
            )
            self.add_field(
                name="AC Rate",
                value=str(info["ac_rate"])[0:2] + "%",
                inline=True,
            )
            self.set_footer(text=f"{info['likes']} 👍 • {info['dislikes']} 👎")

            topic_list = ""
            for name, link in info["topics"].items():
                topic_list += f"[``{name}``]({link}), "
            topic_list = topic_list[:-2]
            topic_list = "||" + topic_list + "||"

            self.add_field(name="Topics", value=topic_list, inline=False)
        else:
            self.add_field(
                name="Topics", value=f"||{','.join(problem['topics'])}||", inline=False
            )
