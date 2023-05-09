import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from typing import Optional, Union
import random
import string
import asyncio
import datetime

class task(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'tasks', description = "[BETA] Earn score by doing daily tasks")
    async def _task(self, interaction):
        await interaction.response.defer(thinking = True)
        lc_user = self.client.DBClient['LC_db']['LC_users'].find_one({'discord_id': interaction.user.id})
        embed = discord.Embed(
            title = "Tasks",
            description = """
            You can earn scores by completing specific tasks. [More info](https://www.notion.so/lowie-writes/How-does-LLC-s-Scoring-System-work-33e3316e95024b448690eac31173e795?pvs=4)
            """,
            color = discord.Colour.blue()
        )
        embed.add_field(
            name = "Your scores",
            value = f"""
            - All-time score: **{lc_user['all_time']['score']}**
            - This month's score: **{lc_user['current_month']['score']}**
            - Previous month's score: **{lc_user['previous_month']['score']}**
            """,
            inline = False
        )
        daily_msg = ""
        daily_score = lc_user['daily_task']['scores_earned_excluding_daily']
        if lc_user['daily_task']['finished_today_daily']:
            daily_score += 2
            daily_msg += f"{Assets.green_tick} Complete Daily Challenge 🗓️ (2 pts)\n"
        else:
            daily_msg += f"{Assets.red_tick} **Complete Daily Challenge 🗓️ (2 pts)**\n"

        if lc_user['daily_task']['scores_earned_excluding_daily'] == 6:
            daily_msg += f"{Assets.green_tick} Self-practice (6/6 pts)\n"
        else:
            daily_msg += f"{Assets.red_tick} **Self-practice ({lc_user['daily_task']['scores_earned_excluding_daily']}/6 pts)**\n"
        
        daily_msg += f"{Assets.blank} - *Solve an Easy problem (1 pts): {lc_user['daily_task']['easy_solved']} solved*\n"
        daily_msg += f"{Assets.blank} - *Solve a Medium problem (2 pts): {lc_user['daily_task']['medium_solved']} solved*\n"
        daily_msg += f"{Assets.blank} - *Solve a Hard problem (3 pts): {lc_user['daily_task']['hard_solved']} solved*\n"
        embed.add_field(
            name = f"Daily tasks ({daily_score}/8 pts)",
            value = daily_msg,
            inline = False
        )

        monthly_msg = ""
        monthly_score = 0
        monthly_checkpoint = [7, 14, 21, 28]
        for day in monthly_checkpoint:
            if lc_user['current_month']['max_daily_streak'] >= day:
                monthly_score += 4
                monthly_msg += f"{Assets.green_tick} Reach a streak of {min(day, lc_user['current_month']['max_daily_streak'])}/{day} days (4 pts)\n"
            else:
                monthly_msg += f"{Assets.red_tick} **Reach a streak of {min(day, lc_user['current_month']['max_daily_streak'])}/{day} days (4 pts)**\n"
        

        embed.add_field(
            name = f"Monthly tasks ({monthly_score}/16 pts)",
            value = monthly_msg,
            inline = False
        )
        
        
        await interaction.followup.send(embed = embed)
    
    
    
async def setup(client):
    await client.add_cog(task(client), guilds=[discord.Object(id=1085444549125611530)])
    #await client.add_cog(task(client))
