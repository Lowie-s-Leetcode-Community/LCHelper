import discord
from discord.ext import tasks, commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
import asyncio
import traceback

class daily(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.daily.start()

    def cog_unload(self):
        self.daily.cancel()

    @tasks.loop(seconds = 120)
    async def daily(self):
        # Waiting for internal cache, I suppose
        await self.client.wait_until_ready()
        await asyncio.sleep(5)

        # Fetching daily problem
        daily_challenge_info = LC_utils.get_daily_challenge_info()
        lc_col_daily = self.client.DBClient['LC_db']['LC_daily']
        lc_current_daily_info = lc_col_daily.find_one({'_id': 1})
        if lc_current_daily_info['daily_challenge']['title'] == daily_challenge_info['title']: 
            # A new daily challenge has not appeared yet
            return

        lc_update = {'$set': {'daily_challenge': daily_challenge_info}}
        lc_col_daily.update_one({'_id': 1}, lc_update)

        guild = await self.client.fetch_guild(1085444549125611530)
        log_channel = await guild.fetch_channel(1091763595777409025)
        await log_channel.send("Daily task started.")
    
        # Creating daily thread
        lc_col_tracking = self.client.DBClient['LC_db']['LC_tracking']
        lc_result = lc_col_tracking.find_one({'server_id': 1085444549125611530})

        guild = await self.client.fetch_guild(1085444549125611530)
        channel = await guild.fetch_channel(lc_result['daily_thread_channel_id'])
        #channel = await guild.fetch_channel(1089769159807733831)
        name = f"{daily_challenge_info['date']}. LeetCode P{daily_challenge_info['id']}"
        await channel.create_thread(name = name, type = discord.ChannelType.public_thread)
    
        # Checking daily streak of everyone 
        lc_col = self.client.DBClient['LC_db']['LC_users']
        users = list(lc_col.find())

        for user in users:
            tmp = user
            
            if tmp['daily_task']['finished_today_daily'] == False:
                tmp['current_month']['current_daily_streak'] = 0
                tmp['all_time']['current_daily_streak'] = 0

            lc_query = {'$set': {
                'daily_task':{
                    'finished_today_daily': False,
                    'scores_earned_excluding_daily': 0,
                    'easy_solved': 0,
                    'medium_solved': 0,
                    'hard_solved': 0
                },
                'current_month': tmp['current_month']
            }}
            lc_col.update_one({'discord_id': user['discord_id']}, lc_query)
            await asyncio.sleep(5)
        await log_channel.send('Daily task completed.')

        # Checking (and starting monthly task)
        # if datetime.datetime.now().day == 1:
        #     lc_col = self.client.DBClient['LC_db']['LC_users']
        #     await log_channel.send('Monthly task started.')
        #     users = list(lc_col.find())
        #     for user in users:
        #         user['previous_month'], user['current_month'] = user['current_month'], user['previous_month']
        #         user['current_month']['max_daily_streak'] = 0
        #         user['current_month']['current_daily_streak'] = 0
        #         user['current_month']['score'] = 0

        #         lc_query = {'$set': user}
        #         lc_col.update_one({'discord_id': user['discord_id']}, lc_query)
        #         await asyncio.sleep(5)
        #     await log_channel.send('Monthly task completed.')

        # Disabling the monthly task

    @daily.error
    async def on_error(self, exception):
        guild = await self.client.fetch_guild(1085444549125611530)
        channel = await guild.fetch_channel(1091763595777409025)
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
    await client.add_cog(daily(client), guilds=[discord.Object(id=1085444549125611530)])
    #await client.add_cog(daily(client))
