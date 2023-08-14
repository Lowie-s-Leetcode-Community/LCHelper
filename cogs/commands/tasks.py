import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from ..logging.logging import logging

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
        score_msg = ""
        score_msg += f"- All-time score: **{lc_user['all_time']['score']}**\n"
        score_msg += f"- This month's score: **{lc_user['current_month']['score']}**\n"
        score_msg += f"- Previous month's score: **{lc_user['previous_month']['score']}**"
        embed.add_field(
            name = "Your scores",
            value = score_msg,
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
            daily_msg += f"{'⌛' if lc_user['daily_task']['scores_earned_excluding_daily'] else Assets.red_tick} **Self-practice ({lc_user['daily_task']['scores_earned_excluding_daily']}/6 pts)**\n"
        
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
                monthly_msg += f"{'⌛' if {min(day, lc_user['current_month']['max_daily_streak'])} else Assets.red_tick} **Reach a streak of {min(day, lc_user['current_month']['max_daily_streak'])}/{day} days (4 pts)**\n"
        

        embed.add_field(
            name = f"Monthly tasks ({monthly_score}/16 pts)",
            value = monthly_msg,
            inline = False
        )
        
        
        await interaction.followup.send(embed = embed)
    
    async def on_problem_completed(self, member: discord.Member, lc_user: dict, problem_title_slug: str, is_daily: bool):
        lc_col = self.client.DBClient['LC_db']['LC_users']
        lc_problem = LC_utils.get_problem_info(problem_title_slug)

        # (Non-daily challange) Updating Daily earnable scores + monthly and all-time scores
        if not is_daily:
            cur_score_without_daily = lc_user['daily_task']['scores_earned_excluding_daily']
            earned_score = 0

            if lc_problem['difficulty'] == "Easy": 
                earned_score = min(1, 6 - cur_score_without_daily)
                lc_user['daily_task']['easy_solved'] += 1
            if lc_problem['difficulty'] == "Medium": 
                earned_score = min(2, 6 - cur_score_without_daily)
                lc_user['daily_task']['medium_solved'] += 1
            if lc_problem['difficulty'] == "Hard":
                earned_score = min(3, 6 - cur_score_without_daily)
                lc_user['daily_task']['hard_solved'] += 1 

            cur_score_without_daily += earned_score
            lc_user['daily_task']['scores_earned_excluding_daily'] += earned_score
            lc_user['current_month']['score'] += earned_score
            lc_user['all_time']['score'] += earned_score

            # Logging
            if earned_score:
                await logging.on_score_add(logging(self.client), member = member, score = earned_score, reason = f"Self-practice: {lc_problem['difficulty']} problem")

        # (Daily challenge) Updating streaks and scores
        if is_daily and not lc_user['daily_task']['finished_today_daily']:
            lc_user['daily_task']['finished_today_daily'] = True
        
            lc_user['current_month']['current_daily_streak'] += 1
            lc_user['current_month']['max_daily_streak'] = max(lc_user['current_month']['max_daily_streak'], lc_user['current_month']['current_daily_streak'])
            lc_user['current_month']['score'] += 2
            
            lc_user['all_time']['current_daily_streak'] += 1
            lc_user['all_time']['max_daily_streak'] = max(lc_user['all_time']['max_daily_streak'], lc_user['all_time']['current_daily_streak'])
            lc_user['all_time']['score'] += 2
            
            # Updating score
            await logging.on_score_add(logging(self.client), member = member, score = 2, reason = "Daily AC")

            if lc_user['current_month']['max_daily_streak'] % 7 == 0:
                lc_user['current_month']['score'] += 4
                lc_user['all_time']['score'] += 4
                await logging.on_score_add(logging(self.client), member = member, score = 4, reason = "Monthly task completed")
        
        lc_query = {'$set': lc_user}
        lc_col.update_one({'discord_id': member.id}, lc_query)
    
async def setup(client):
    await client.add_cog(task(client), guilds=[discord.Object(id=1085444549125611530)])
    #await client.add_cog(task(client))
