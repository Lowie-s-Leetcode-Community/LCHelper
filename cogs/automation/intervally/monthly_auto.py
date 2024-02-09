import discord
from discord import app_commands
from discord.ext import tasks, commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
import os
import traceback
import datetime
from utils.llc_datetime import get_first_day_of_current_month

class MonthlyAutomation(commands.Cog):
    def __init__(self, client):
        self.client = client
        if os.getenv('START_UP_TASKS') == "True": 
            self.monthly.start()

    def cog_unload(self):
        self.monthly.cancel()
    
    @tasks.loop(hours = 6)
    async def monthly(self):
        await self.update_leaderboard()
        await self.update_problems_list()

    # Update new monthly objects for members who participated last month
    async def update_leaderboard(self):
        # maybe send a message to update last month leaderboard on #general?
        leaderboard = self.client.db_api.read_current_month_leaderboard()
        first_day_of_current_month = get_first_day_of_current_month()
        if len(leaderboard) > 0:
            return
        leaderboard = self.client.db_api.read_last_month_leaderboard()
        for user in leaderboard:
            await self.client.db_api.create_monthly_object(userId=user["userId"], firstDayOfMonth=first_day_of_current_month)
        return

    # Update the problem list, as there are new problems on the site every month
    async def update_problems_list(self):
        db_problems_list = self.client.db_api.read_problems_all()
        # assuming that graphql result has sorted problem properly
        lc_problem_list = LC_utils.crawl_problem_list()
        new_problems = []
        removed_problems = []
        db_ind, lc_ind = 0, 0
        while db_ind < len(db_problems_list) or lc_ind < len(lc_problem_list):
          if db_ind >= len(db_problems_list):
            new_problems.append(lc_problem_list[lc_ind])
            lc_ind += 1
          elif lc_ind >= len(lc_problem_list):
            removed_problems.append(db_problems_list[db_ind])
            db_ind += 1
          else:
            db_cur, lc_cur = db_problems_list[db_ind]['id'], int(lc_problem_list[lc_ind]['frontendQuestionId'])
            if db_cur == lc_cur:
              db_ind += 1
              lc_ind += 1
            elif db_cur < lc_cur:
              removed_problems.append(db_problems_list[db_ind])
              db_ind += 1
            elif db_cur > lc_cur:
              new_problems.append(lc_problem_list[lc_ind])
              lc_ind += 1
              # handling if problem changes slug?
        for problem in new_problems:
          print(problem)
          await self.client.db_api.create_problem(problem)

        # add warning msg for removed_problem?
        return

    @monthly.error
    async def on_error(self, exception):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['devErrorLogId'])
        await channel.send(f"Monthly crawl error```py\n{exception}```")

        self.monthly.restart()

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def stop_(self, ctx):
        self.monthly.stop()
        await ctx.send(f"{Assets.green_tick} **Monthly task stopped.**")

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def start_monthly(self, ctx):
        self.monthly.start()
        await ctx.send(f"{Assets.green_tick} **Monthly task started.**")

async def setup(client):
    await client.add_cog(MonthlyAutomation(client), guilds=[discord.Object(id=client.config['serverId'])])
