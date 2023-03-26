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
        #self.api_request.start()

    def cog_unload(self):
        self.api_request.cancel()

    @tasks.loop(seconds = 5)
    async def api_request(self):
        lc_db = self.client.DBClient['LC_db']
        lc_col_user = lc_db['LC_users']
        lc_col_server = lc_db['LC_tracking']
        user_list = list(lc_col_user.find())
        for user in user_list:
            lc_username = user['lc_username']
            recent_info = LC_utils.get_recent_ac(lc_username)
            untracked_new_submission = False
            for submission in reversed(recent_info):
                if submission['timestamp'] != user['recent_ac']['timestamp']:
                    untracked_new_submission = True
                    user = await self.client.fetch_user(user['discord_id'])
                    server_list = [guild.id for guild in user.mutual_guilds]
                    for server_id in server_list:
                        lc_query = {'server_id': server_id}
                        lc_result = lc_col_server.find_one(lc_query)
                        if lc_result:
                            guild = self.client.fetch_guild(server_id)
                            channel = await guild.fetch_channel(lc_result['tracking_channel_id'])
                            lc_user_info = LC_utils.get_user_profile(lc_username)
                            embed = discord.Embed(
                                title = f"**{submission['title']}**",
                                url = f"https://leetcode.com/{submission['titleSlug']}",
                                color = 0xffb800
                            )
                                                
                            embed.set_author(
                                name = f"{lc_username}: {lc_user_info['problem']['solved']['all']}/{lc_user_info['problem']['total_problem']['all']} ({lc_user_info['problem']['percentage']['all']}%)",
                                icon_url = "https://assets.leetcode.com/users/leetcode/avatar_1568224780.png",
                                url = lc_user_info['profile']['link']
                            )
                            embed.set_thumbnail(
                                url = lc_user_info['profile']['avatar']
                            )
                            await channel.send_message()

                else: break
            await asyncio.sleep(5)

    @commands.command()
    @commands.is_owner()
    async def stop_request(self, ctx):
        self.api_request.stop()
        await ctx.send(f"{Assets.green_tick} **Submission crawling task stopped.**")

async def setup(client):
    await client.add_cog(crawl(client))
