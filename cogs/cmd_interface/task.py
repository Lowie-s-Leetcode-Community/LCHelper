import discord
import datetime
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from utils.logger import Logger

class Task(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.logger = Logger(client)

    @app_commands.command(name = 'task', description = "Earn score by doing daily tasks")
    async def _task(self, interaction):
        await interaction.response.defer(thinking = True)
        user_progress = self.client.db_api.read_user_progress(str(interaction.user.id))
        embed_list = []

        embed = discord.Embed(
            title = f"{interaction.user.name}'s Tasks",
            description = """
            *<a:blob_gaming:1093831896212971540> You can earn monthly LLC Score by completing these tasks. [More info](https://www.notion.so/lowie-writes/How-does-LLC-s-Scoring-System-work-33e3316e95024b448690eac31173e795?pvs=4)*
            """,
            color = discord.Colour.blue()
        )
        score_msg = "## Monthly progress"
        score_msg += f"- Your Leetcode username: **{user_progress['user']['leetcodeUsername']}**\n"
        score_msg += f"- This month's score: **{user_progress['monthly']['scoreEarned']}**\n"

        daily_conf = {
            "daily": self.client.config['dailySolveScore'],
            "easy": self.client.config['easySolveScore'],
            "medium": self.client.config['mediumSolveScore'],
            "hard": self.client.config['hardSolveScore'],
            "practiceCap": self.client.config['practiceScoreCap'],
        }
        daily_msg = ""
        daily_msg += f"- Score Earned: **{user_progress['user_daily']['scoreEarned']}** pts\n"
        if user_progress['user_daily']['solvedDaily']:
            daily_msg += f"{Assets.green_tick} Complete Daily Challenge 🗓️ ({daily_conf['daily']} pts)\n"
        else:
            daily_msg += f"**{Assets.red_tick} Complete Daily Challenge 🗓️ ({daily_conf['daily']} pts)** -> </daily:1113100702886141994>\n"

        if user_progress['user_daily']['scoreGacha'] != -1:
            daily_msg += f"{Assets.green_tick} Test your luck! ({user_progress['user_daily']['scoreGacha']} pts)\n"
        else:
            daily_msg += f"{Assets.red_tick} **Test your luck!** -> </gacha:1168530503675166791> **(1-?? pts)**\n"

        # stub
        practice_score = min(daily_conf['practiceCap'], 5)
        if True:
            daily_msg += f"{Assets.green_tick} Self-practice ({practice_score}/{daily_conf['practiceCap']} pts)\n"
        else:
            daily_msg += f"{'⌛' if practice_score else Assets.red_tick} **Self-practice ({practice_score}/{daily_conf['practiceCap']} pts)**\n"

        daily_msg += f"{Assets.blank} - *Solve an Easy problem ({daily_conf['easy']} pts): {user_progress['user_daily']['solvedEasy']} solved*\n"
        daily_msg += f"{Assets.blank} - *Solve a Medium problem ({daily_conf['medium']} pts): {user_progress['user_daily']['solvedMedium']} solved*\n"
        daily_msg += f"{Assets.blank} - *Solve a Hard problem ({daily_conf['hard']} pts): {user_progress['user_daily']['solvedHard']} solved*\n"

        embed.add_field(
            name = "Daily Progress",
            value = daily_msg,
            inline = False
        )

        embed_list.append(embed)
        await interaction.followup.send(embeds = embed_list)
    
async def setup(client):
    await client.add_cog(Task(client), guilds=[discord.Object(id=client.config['serverId'])])
