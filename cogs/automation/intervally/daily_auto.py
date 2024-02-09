import discord
from discord import app_commands
from discord.ext import tasks, commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
import os
import asyncio
import traceback
import datetime

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

    @tasks.loop(hours = 1)
    async def daily(self):
        # Waiting for internal cache, I suppose.
        await self.client.wait_until_ready()
        await asyncio.sleep(5)

        # Fetching daily problem.
        daily_challenge_info = LC_utils.get_daily_challenge_info()
        lc_col_daily = self.client.DBClient['LC_db']['LC_daily']
        lc_current_daily_info = lc_col_daily.find_one({'_id': 1})
        if lc_current_daily_info['daily_challenge']['title'] == daily_challenge_info['title']: 
            # A new daily challenge has not appeared yet, so task is ended here.
            return

        # If there's a new daily challenge -> It's a new day, and we perform a global update on all the members.

        # Updating the "saved" daily challenge with the new daily challenge.
        lc_update = {'$set': {'daily_challenge': daily_challenge_info}}
        lc_col_daily.update_one({'_id': 1}, lc_update)

        # Sending a message to the Discord channel log
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        lc_col = self.client.DBClient['LC_db']['LC_config']
        lc_result = lc_col.find_one({})
        log_channel = await guild.fetch_channel(lc_result['event_channel_id'])
        await log_channel.send("Daily task started.")
    
        # Creating daily thread
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(lc_result['daily_thread_channel_id'])
        #channel = await guild.fetch_channel(1089769159807733831)
        name = f"{daily_challenge_info['date']}. LeetCode P{daily_challenge_info['id']}"
        await channel.create_thread(name = name, type = discord.ChannelType.public_thread)
    
        # Checking daily streak of everyone 
        lc_col = self.client.DBClient['LC_db']['LC_users']
        users = list(lc_col.find())

        for user in users:
            tmp = user
            
            # Setting non-daily people's streak to 0
            if tmp['daily_task']['finished_today_daily'] == False:
                tmp['current_month']['current_daily_streak'] = 0
                tmp['all_time']['current_daily_streak'] = 0

            # Updating tasks info
            lc_query = {'$set': {
                'daily_task':{
                    'finished_today_daily': False,
                    'scores_earned_excluding_daily': 0,
                    'easy_solved': 0,
                    'medium_solved': 0,
                    'hard_solved': 0,
                    'gacha': -1
                },
                'current_month': tmp['current_month'],
                'all_time': tmp['all_time']
            }}
            lc_col.update_one({'discord_id': user['discord_id']}, lc_query)
            await asyncio.sleep(3)
        await log_channel.send('Daily task completed.')

    ### Dev stuff
    @daily.error
    async def on_error(self, exception):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['serverId'])
        await channel.send(f"```py\n{traceback.format_exc()}```")

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
