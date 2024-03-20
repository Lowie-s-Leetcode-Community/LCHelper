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
    async def _task(self, interaction: discord.Interaction):
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
        if user_progress['user_daily']['scoreEarned'] is None or user_progress['user_daily']['scoreEarned'] < 0:
            daily_msg += "Score Earned: **0** pts\n"
        else:
            daily_msg += f"- Score Earned: **{user_progress['user_daily']['scoreEarned']}** pts\n"

        if user_progress['user_daily']['solvedDaily']:
            daily_msg += f"{Assets.green_tick} Complete Daily Challenge 🗓️ ({daily_conf['daily']} pts)\n"
        else:
            daily_msg += f"**{Assets.red_tick} Complete Daily Challenge 🗓️ ({daily_conf['daily']} pts)** -> </daily:1206907242784235525>\n"

        if user_progress['user_daily']['scoreGacha'] is None or user_progress['user_daily']['scoreGacha'] < 0:
            daily_msg += f"{Assets.red_tick} **Test your luck!** -> </gacha:1206907242784235527> **(1-?? pts)**\n"
        else:
            daily_msg += f"{Assets.green_tick} Test your luck! ({user_progress['user_daily']['scoreGacha']} pts)\n"
        
        solved_easy = user_progress['user_daily']['solvedEasy'] if user_progress['user_daily']['solvedEasy'] is not None else 0
        solved_medium = user_progress['user_daily']['solvedMedium'] if user_progress['user_daily']['solvedMedium'] is not None else 0
        solved_hard = user_progress['user_daily']['solvedHard'] if user_progress['user_daily']['solvedHard'] is not None else 0

        practice_score = min(daily_conf['practiceCap'], solved_easy + solved_medium*2 + solved_hard*3)
        if practice_score == daily_conf['practiceCap']:
            daily_msg += f"{Assets.green_tick} Self-practice ({practice_score}/{daily_conf['practiceCap']} pts)\n" 
        else:
            daily_msg += f"{'⌛' if practice_score else Assets.red_tick} **Self-practice ({practice_score}/{daily_conf['practiceCap']} pts)**\n"

        
        daily_msg += f"{Assets.blank} - *Solve an Easy problem ({daily_conf['easy']} pts): **{solved_easy}** solved*\n"   
        daily_msg += f"{Assets.blank} - *Solve a Medium problem ({daily_conf['medium']} pts): **{solved_medium}** solved*\n"    
        daily_msg += f"{Assets.blank} - *Solve a Hard problem ({daily_conf['hard']} pts): **{solved_hard}** solved*\n"

        embed.add_field(
            name = "Daily Progress",
            value = daily_msg,
            inline = False
        )

        embed_list.append(embed)
        await interaction.followup.send(embeds = embed_list)
    
async def setup(client):
    await client.add_cog(Task(client), guilds=[discord.Object(id=client.config['serverId'])])
