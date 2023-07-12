import discord
from discord import app_commands
from discord.ext import tasks, commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from cogs.daily import daily
from cogs.tasks import task
from typing import Optional
import asyncio
import traceback

class crawl(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.crawling.start()

    def cog_unload(self):
        self.crawling.cancel()

    @tasks.loop(seconds = 120)
    async def crawling(self):
        # Waiting for internal cache, I suppose
        await self.client.wait_until_ready()
        await asyncio.sleep(5)

        lc_db = self.client.DBClient['LC_db']
        lc_col_user = lc_db['LC_users']
        lc_col_server = lc_db['LC_tracking']
        user_list = list(lc_col_user.find())

        # Checking every user in DB
        for user in user_list:
            # Getting the most recent submissions
            lc_username = user['lc_username']
            recent_solved = []
            recent_info = LC_utils.get_recent_ac(lc_username, 20)

            # For debugging
            """
            if lc_username == "leanhduy0206":
                recent_info = [{
                    'id': '926059124', 
                    'title': 'Binary Search', 
                    'titleSlug': 'binary-search', 
                    'timestamp': '4680366541'
                }]
            """
            # Tracking the most recent submissions
            untracked_new_submission = False
            for submission in reversed(recent_info):
                if int(submission['timestamp']) > int(user['recent_ac']['timestamp']):
                    # New AC submissions found
                    # Checking if daily challenge
                    daily_info = self.client.DBClient['LC_db']['LC_daily'].find_one()['daily_challenge']
                    is_daily_challenge = True if daily_info['title_slug'] == submission['titleSlug'] else False

                    if (submission['titleSlug'] not in user['solved']) or (is_daily_challenge and user['daily_task']['finished_today_daily']):
                        # Getting channel log
                        server_id = 1085444549125611530
                        lc_result = lc_col_server.find_one({'server_id': 1085444549125611530})
                        guild = await self.client.fetch_guild(server_id)
                        channel = await guild.fetch_channel(lc_result['tracking_channel_id'])

                        # Posting update log in LLC
                        untracked_new_submission = True
                        discord_member = await guild.fetch_member(user['discord_id'])
                        lc_user_info = LC_utils.get_user_profile(lc_username)
                        problem_info = LC_utils.get_problem_info(submission['titleSlug'])
                        desc_str = f"▸ **Submitted:** <t:{submission['timestamp']}:R>"

                        if is_daily_challenge: desc_str = "▸ 🗓️ **Daily challenge**\n" + desc_str
                        
                        embed = discord.Embed(
                            title = f"**Solved: {problem_info['title']}**",
                            description = desc_str,
                            url = f"{problem_info['link']}",
                            color = Assets.easy if problem_info['difficulty'] == 'Easy' else Assets.medium if problem_info['difficulty'] == 'Medium' else Assets.hard
                        )
                        embed.add_field(
                            name = "Difficulty",
                            value = problem_info['difficulty'],
                            inline = True
                        )
                        embed.add_field(
                            name = "AC Count", 
                            value = f"{problem_info['total_AC']}/{problem_info['total_submissions']}",
                            inline = True,
                        )
                        embed.add_field(
                            name = "AC Rate",
                            value = str(problem_info['ac_rate'])[0:5] + "%",
                            inline = True,
                        )
                        tag_list = ""
                        for name, link in problem_info['topics'].items():
                            tag_list += f"[``{name}``]({link}), "

                        tag_list = f"||{tag_list[:-2]}||"
                        embed.add_field(
                            name = "Topics",
                            value = tag_list,
                            inline = False
                        )
                        embed.set_footer(
                            text = f"{problem_info['likes']} 👍 • {problem_info['dislikes']} 👎"
                        )
                                            
                        embed.set_author(
                            name = f"{lc_username}: {lc_user_info['problem']['solved']['all']}/{lc_user_info['problem']['total_problem']['all']} ({lc_user_info['problem']['percentage']['all']}%)",
                            icon_url = "https://assets.leetcode.com/users/leetcode/avatar_1568224780.png",
                            url = lc_user_info['profile']['link']
                        )
                        embed.set_thumbnail(
                            url = lc_user_info['profile']['avatar']
                        )
                        
                        await channel.send(embed = embed)
                        recent_solved.append(submission['titleSlug'])

                        # Updating daily earnable scores
                        await task.on_problem_completed(task(self.client), member = discord_member, lc_user = user, problem_title_slug = submission['titleSlug'], is_daily = is_daily_challenge)


            # Updating solved list and most recent solved in database
            if untracked_new_submission:
                solved_list = list(set(user['solved'] + recent_solved))
                lc_update = {'$set': {
                    'recent_ac': recent_info[0],
                    'solved': solved_list
                }}
                lc_col_user.update_one({'lc_username': lc_username}, lc_update)
            
            await asyncio.sleep(5)

    @crawling.error
    async def on_error(self, exception):
        guild = await self.client.fetch_guild(1085444549125611530)
        channel = await guild.fetch_channel(1091763595777409025)
        await channel.send(f"```py\n{traceback.format_exc()}```")

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
    await client.add_cog(crawl(client), guilds=[discord.Object(id=1085444549125611530)])
    #await client.add_cog(crawl(client))