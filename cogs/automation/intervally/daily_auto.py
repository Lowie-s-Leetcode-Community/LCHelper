import discord
from discord import app_commands
from discord.ext import tasks, commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
import os
import asyncio
import traceback
import datetime
from utils.llc_datetime import get_today

# Check if it's the first monday of the month
def is_monthly_reset_time():
    d = datetime.date.today()
    if d.weekday() == 0 and int((d.day - 1) / 7) + 1 == 1:
        return True
    return False

class DailyAutomation(commands.Cog):
    def __init__(self, client):
        self.client = client
        if os.getenv('START_UP_TASKS') == "True": 
            self.daily.start()

    def cog_unload(self):
        self.daily.cancel()

    async def create_new_daily_object(self):
        daily_challenge_info = LC_utils.get_daily_challenge_info()
        db_daily_obj = self.client.db_api.read_latest_daily()
        # {'date': '2024-02-09', 'link': 'https://leetcode.com/problems/largest-divisible-subset/', 'title': 'Largest Divisible Subset', 'title_slug': 'largest-divisible-subset', 'id': '368'}
        if daily_challenge_info['date'] != db_daily_obj['generatedDate'].strftime("%Y-%m-%d"):
            await self.client.db_api.create_daily_object(daily_challenge_info['id'], get_today())
        return daily_challenge_info

    async def create_daily_thread(self, daily_challenge_info):
        # Creating daily thread
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['dailyThreadChannelId'])
        name = f"[{daily_challenge_info['date']}] LeetCode P{daily_challenge_info['id']}"
        await channel.create_thread(name = name, type = discord.ChannelType.public_thread)
        return

    @tasks.loop(minutes = 30)
    async def daily(self):
        daily_challenge_info = await self.create_new_daily_object()
        await self.create_daily_thread(daily_challenge_info)

    @daily.error
    async def on_error(self, exception):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['serverId'])
        await channel.send(f"```py\n{traceback.format_exc()[:800]}```")

        self.daily.restart()

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def stop_daily(self, ctx):
        self.daily.stop()
        await ctx.send(f"{Assets.green_tick} **Daily task stopped.**")

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def start_daily(self, ctx):
        self.daily.start()
        await ctx.send(f"{Assets.green_tick} **Daily task started.**")

async def setup(client):
    await client.add_cog(DailyAutomation(client), guilds=[discord.Object(id=client.config['serverId'])])
