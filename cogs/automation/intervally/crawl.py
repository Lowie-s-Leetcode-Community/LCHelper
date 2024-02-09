import discord
from discord import app_commands
from discord.ext import tasks, commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from cogs.cmd_interface.task import Task
import os
import asyncio
import traceback
from database_api_layer.api import DatabaseAPILayer
from utils.llc_datetime import get_date_from_timestamp
from datetime import datetime

class Crawl(commands.Cog):
    def __init__(self, client):
        self.client = client
        if os.getenv('START_UP_TASKS') == "True":
            self.crawling.start()
        self.db_api = DatabaseAPILayer(client)

    def cog_unload(self):
        self.crawling.cancel()
    
    async def submissions(self):
        # flaw: this only returns user that are shown on leaderboard???
        leaderboard = self.db_api.read_current_month_leaderboard()
        # benchmarking
        # guild = await self.client.fetch_guild(1085444549125611530)
        # log_channel = await guild.fetch_channel(1202180199060615168)
        # start_time = datetime.now()
        # await log_channel.send(f"Start crawling. Timestamp: {start_time}")
        for user in leaderboard:
            username = user['leetcodeUsername']
            # await log_channel.send(f"Start crawling for username {username}")
            recent_solved = []
            recent_info = LC_utils.get_recent_ac(username, 20)
            if (recent_info == None):
                continue

            for submission in recent_info:
                if int(submission['id']) <= user['mostRecentSubId']:
                    break
                date = get_date_from_timestamp(int(submission['timestamp']))
                daily_obj = self.db_api.read_daily_object(date)

                problem = self.db_api.read_problem_from_slug(submission['titleSlug'])
                await self.db_api.register_new_submission(user['userId'], problem['id'], int(submission['id']), daily_obj['id'])
        # await log_channel.send(f"Finish one submission crawling loop! Timestamp: {datetime.now()}. Delta: {datetime.now() - start_time}")

    @tasks.loop(minutes = 15)
    async def crawling(self):
        await self.submissions()

    @crawling.error
    async def on_error(self, exception):
        guild = await self.client.fetch_guild(1085444549125611530)
        channel = await guild.fetch_channel(1091763595777409025)
        await channel.send(f"Crawling error```py\n{traceback.format_exc()[:800]}```")

        self.crawling.restart()

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def stop_crawling(self, ctx):
        self.crawling.cancel()
        await ctx.send(f"{Assets.green_tick} **Submission crawling task stopped.**")

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def start_crawling(self, ctx):
        self.crawling.start()
        await ctx.send(f"{Assets.green_tick} **Submission crawling task started.**")

async def setup(client):
    await client.add_cog(Crawl(client), guilds=[discord.Object(id=1085444549125611530)])
