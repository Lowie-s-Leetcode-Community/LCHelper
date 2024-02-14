import discord
from discord import app_commands
from discord.ext import tasks, commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from cogs.cmd_interface.task import Task
import os
import asyncio
import traceback
from utils.llc_datetime import get_date_from_timestamp
from datetime import datetime
import pytz
from utils.logger import Logger
import time

class Crawl(commands.Cog):
    def __init__(self, client):
        self.client = client
        if os.getenv('START_UP_TASKS') == "Daily":
            self.crawling.start()
        self.logger = Logger(client)

    def cog_unload(self):
        self.crawling.cancel()
    
    async def submissions(self):
        # flaw: this only returns user that are shown on leaderboard???
        leaderboard = self.client.db_api.read_current_month_leaderboard()
        for user in leaderboard:
            username = user['leetcodeUsername']
            recent_solved = []
            recent_info = LC_utils.get_recent_ac(username, 20)
            if (recent_info == None):
                continue

            for submission in recent_info:
                if int(submission['id']) <= user['mostRecentSubId']:
                    break
                date = get_date_from_timestamp(int(submission['timestamp']))
                daily_obj = self.client.db_api.read_daily_object(date)
                if daily_obj == None:
                    daily_obj = self.client.db_api.read_latest_daily_object()

                problem = self.client.db_api.read_problem_from_slug(submission['titleSlug'])
                # fire-fighting, to be removed
                if problem != None:
                    await self.client.db_api.register_new_submission(user['userId'], problem['id'], submission, daily_obj['id'])
        # await log_channel.send(f"Finish one submission crawling loop! Timestamp: {datetime.now()}. Delta: {datetime.now() - start_time}")

    @tasks.loop(minutes = 10)
    async def crawling(self):
        await self.logger.on_automation_event("Crawl", "start-crawl")
        current_utc_time = datetime.now().astimezone(pytz.utc)
        if 0 <= current_utc_time.hour <= 1:
            await self.logger.on_automation_event("Crawl", "stop-crawl to avoid conflict with other tasks.")
            return
        await self.logger.on_automation_event("Crawl", "submissions()")
        await self.submissions()
        await self.logger.on_automation_event("Crawl", "end-crawl")

    @crawling.error
    async def on_error(self, exception):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['devErrorLogId'])
        await channel.send(f"Crawling error```py\n{traceback.format_exc()[:800]}```")
        await self.logger.on_automation_event("Crawl", "error found")

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
    await client.add_cog(Crawl(client), guilds=[discord.Object(id=client.config['serverId'])])
