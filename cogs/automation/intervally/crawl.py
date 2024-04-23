import discord
from discord import app_commands
from discord.ext import tasks, commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from cogs.cmd_interface.task import Task
import os
import asyncio
import traceback
from utils.llc_datetime import get_date_from_timestamp, get_fdom_by_datestamp
from datetime import datetime
import pytz
from utils.logger import Logger
import time

class Crawl(commands.Cog):
    def __init__(self, client):
        self.client = client
        if os.getenv('START_UP_TASKS') == "True":
            self.crawling.start()
        self.logger = Logger(client)

    def cog_unload(self):
        self.crawling.cancel()

    async def submissions(self):
        all_users = self.client.db_api.read_all_users()
        submissions_blob = {}
        for user in all_users:
            username = user['leetcodeUsername']
            recent_info = LC_utils.get_recent_ac(username, 20)

            if (recent_info == None):
                continue
            # unique, cuz somehow submissions are not unique :)
            uniqued_recent_info = {}
            for sub in recent_info:
                uniqued_recent_info[sub['titleSlug']] = sub
            uniqued_recent_info = uniqued_recent_info.values()

            user_blob = {
                "userId": user['id'],
                "newSubmissions": []
            }
            for submission in uniqued_recent_info:
                date = get_date_from_timestamp(int(submission['timestamp']))
                fdom = get_fdom_by_datestamp(date)
                daily_f = date.strftime("%Y-%m-%d")
                month_f = fdom.strftime("%Y-%m-%d")
                if month_f not in submissions_blob:
                    submissions_blob[month_f] = {}
                if daily_f not in submissions_blob[month_f]:
                    submissions_blob[month_f][daily_f] = {}
                if username not in submissions_blob[month_f][daily_f]:
                    submissions_blob[month_f][daily_f][username] = []
                submissions_blob[month_f][daily_f][username].append(submission)
        await self.client.db_api.register_new_crawl(submissions_blob)

    @tasks.loop(minutes = 25)
    async def crawling(self):
        current_utc_time = datetime.now().astimezone(pytz.utc)
        if current_utc_time.hour == 0 or current_utc_time == 12:
            await self.logger.on_automation_event("Crawl", "No crawl to avoid conflict with other tasks.")
            return

        await self.logger.on_automation_event("Crawl", "start-crawl")
        await self.logger.on_automation_event("Crawl", "submissions()")
        await self.submissions()
        await self.logger.on_automation_event("Crawl", "end-crawl")

    @crawling.error
    async def on_error(self, exception):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['devErrorLogId'])
        await channel.send(f"Crawling error```py\n{traceback.format_exc()[:800]}```")
        await self.logger.on_automation_event("Crawl", "error found")
        time.sleep(90)

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
