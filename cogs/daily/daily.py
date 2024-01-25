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

class daily(commands.Cog):
    def __init__(self, client):
        self.client = client
        if os.getenv('START_UP_TASKS') == "True": 
            self.daily.start()

    def cog_unload(self):
        self.daily.cancel()

    @tasks.loop(seconds = 600)
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
        guild = await self.client.fetch_guild(1085444549125611530)
        lc_col = self.client.DBClient['LC_db']['LC_config']
        lc_result = lc_col.find_one({})
        log_channel = await guild.fetch_channel(lc_result['event_channel_id'])
        await log_channel.send("Daily task started.")
    
        # Creating daily thread
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

        # Checking (and starting monthly task)
        if is_monthly_reset_time():
            lc_col = self.client.DBClient['LC_db']['LC_users']
            await log_channel.send('Monthly task started.')
            users = list(lc_col.find())
            for user in users:
                user['previous_month'], user['current_month'] = user['current_month'], user['previous_month']
                user['current_month']['max_daily_streak'] = 0
                user['current_month']['current_daily_streak'] = 0
                user['current_month']['score'] = 0

                lc_query = {'$set': user}
                lc_col.update_one({'discord_id': user['discord_id']}, lc_query)
                await asyncio.sleep(3)
            await log_channel.send(f'Monthly task completed. Reset the monthly data of {str(len(users))} LLC members!')

    @app_commands.command(name = 'daily', description = "Returns Leetcode's Daily Challenge")
    async def _daily(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        
        # Getting the daily challenge

        # daily_info = LC_utils.get_daily_challenge_info()
        daily_info = self.client.DBClient['LC_db']['LC_daily'].find_one()['daily_challenge']
        info = LC_utils.get_problem_info(daily_info['title_slug'])

        embed = discord.Embed(
            title = f"**{info['title']}**",
            url = f"{info['link']}",
            color = Assets.easy if info['difficulty'] == 'Easy' else Assets.medium if info['difficulty'] == 'Medium' else Assets.hard
        )
        embed.add_field(
            name = "Difficulty",
            value = info['difficulty'],
            inline = True
        )
        embed.add_field(
            name = "AC Count", 
            value = f"{info['total_AC']}/{info['total_submissions']}",
            inline = True,
        )
        embed.add_field(
            name = "AC Rate",
            value = str(info['ac_rate'])[0:5] + "%",
            inline = True,
        )
        tag_list = ""
        for name, link in info['topics'].items():
            tag_list += f"[``{name}``]({link}), "
        
        tag_list = tag_list[:-2]
        tag_list = "||" + tag_list + "||"
        embed.add_field(
            name = "Topics",
            value = tag_list,
            inline = False
        )
        embed.set_footer(
            text = f"{info['likes']} 👍 • {info['dislikes']} 👎"
        )

        await interaction.followup.send(f"Daily Challenge - {daily_info['date']}", embed = embed)

    ### Dev stuff
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
