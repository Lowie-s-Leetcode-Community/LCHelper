import discord
from discord import app_commands
from discord.ext import tasks, commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from typing import Optional
import asyncio

class crawl(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.api_request.start()

    def cog_unload(self):
        self.api_request.cancel()

        
    @tasks.loop(seconds = 30)
    async def api_request(self):
        # Waiting for internal cache, I suppose
        await self.client.wait_until_ready()
        await asyncio.sleep(5)

        lc_db = self.client.DBClient['LC_db']
        lc_col_user = lc_db['LC_users']
        lc_col_server = lc_db['LC_tracking']
        user_list = list(lc_col_user.find())

        # Checking every user in DB
        for user in user_list:
            # Getting the 5 most recent submissions
            lc_username = user['lc_username']
            recent_info = LC_utils.get_recent_ac(lc_username)
            """
            if lc_username == "leanhduy0206":
                recent_info = [{
                    "id": "757122191",
                    "title": "Maximal Rectangle",
                    "titleSlug": "maximal-rectangle",
                    "timestamp": "4000000000000"
                }]
            """
            # Tracking the most recent submissions
            untracked_new_submission = False
            for submission in reversed(recent_info):
                if int(submission['timestamp']) > int(user['recent_ac']['timestamp']):
                    # New AC submissions found, now posting update log in every mutual guild with the user
                    untracked_new_submission = True
                    discord_user = await self.client.fetch_user(user['discord_id'])
                    server_list = [guild.id for guild in discord_user.mutual_guilds]
                    for server_id in server_list:
                        lc_query = {'server_id': server_id}
                        lc_result = lc_col_server.find_one(lc_query)
                        if lc_result:
                            guild = await self.client.fetch_guild(server_id)
                            channel = await guild.fetch_channel(lc_result['tracking_channel_id'])
                            
                            lc_user_info = LC_utils.get_user_profile(lc_username)
                            problem_info = LC_utils.get_question_info(submission['titleSlug'])
                            embed = discord.Embed(
                                title = f"**Solved: {problem_info['title']}**",
                                description = f"▸ **Submitted:** <t:{submission['timestamp']}:R>",
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

                            tag_list = tag_list[:-2]
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
            if untracked_new_submission:
                lc_update = {'$set': {'recent_ac': recent_info[0]}}
                lc_col_user.update_one({'lc_username': lc_username}, lc_update)
            
            await asyncio.sleep(5)

    @api_request.error
    async def on_error(self, exception):
        print(exception)

    @commands.command()
    @commands.is_owner()
    async def stop_request(self, ctx):
        self.api_request.stop()
        await ctx.send(f"{Assets.green_tick} **Submission crawling task stopped.**")

    @commands.command()
    @commands.is_owner()
    async def start_request(self, ctx):
        self.api_request.start()
        await ctx.send(f"{Assets.green_tick} **Submission crawling task started.**")

async def setup(client):
    #await client.add_cog(crawl(client), guilds=[discord.Object(id=1085444549125611530)])
    await client.add_cog(crawl(client))
