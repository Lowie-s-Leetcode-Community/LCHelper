import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from typing import Optional
import random
import string
import datetime

class ConfirmView(discord.ui.View):
    def __init__(self, client, code, username, user_id):
        super().__init__(timeout = 300)
        self.code = code
        self.client = client
        self.username = username
        self.user_id = user_id
        self.response = None
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
            child.label = "Timeout!"
            child.emoji = "⏰"
        await self.response.edit(view = self)


    @discord.ui.button(label = "Verify Me!", style = discord.ButtonStyle.primary)
    async def call_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        assert interaction.user.id == self.user_id
        await interaction.response.defer(thinking = True)
        user_info = LC_utils.get_user_profile(self.username)
        if len(user_info['profile']['summary']) >= 5 and user_info['profile']['summary'][0:5] == self.code:
            lc_db = self.client.DBClient['LC_db']
            lc_col = lc_db['LC_users']
            lc_query = {'discord_id': interaction.user.id}
            lc_result = lc_col.find_one(lc_query)
            if lc_result:
                lc_update = {'$set': {'lc_username': self.username}}
                lc_col.update_one(lc_query, lc_update)
            else:
                lc_col.insert_one({'discord_id': interaction.user.id, 'lc_username': self.username})

            # Also updating the necessary info
            recent_info = LC_utils.get_recent_ac(self.username, 20)
            tmp_query = {
                'all_time': {
                    'max_daily_streak': 0,
                    'current_daily_streak': 0,
                    'score': 0
                },
                'current_month': {
                    'max_daily_streak': 0,
                    'current_daily_streak': 0,
                    'score': 0
                },
                'previous_month': {
                    'max_daily_streak': 0,
                    'current_daily_streak': 0,
                    'score': 0
                },
                'daily_task': {
                    'finished_today_daily': False,
                    'scores_earned_excluding_daily': 0,
                    'easy_solved': 0,
                    'medium_solved': 0,
                    'hard_solved': 0
                },
                'solved': []
            }
            if len(recent_info) == 0:
                tmp_query['recent_ac'] = {
                    "id": None,
                    "title": None,
                    "titleSlug": None,
                    "timestamp": str(int(datetime.datetime.timestamp(datetime.datetime.now())))
                }
            else: tmp_query['recent_ac'] = recent_info[0]
        
            lc_update = {'$set': tmp_query}
            lc_col.update_one(lc_query, lc_update)
            
            lc_query = {}
            lc_result = lc_db['LC_config'].find_one(lc_query)
            verified_role_id = lc_result['verified_role_id']
            unverified_role_id = lc_result['unverified_role_id']
            member = await interaction.guild.fetch_member(interaction.user.id)
            verified_role = discord.utils.get(interaction.guild.roles, id = verified_role_id)
            unverified_role = discord.utils.get(interaction.guild.roles, id = unverified_role_id)
            await member.add_roles(verified_role)
            try:
                # in case the role was already manually removed
                await member.remove_roles(unverified_role)
            except:
                pass

            await interaction.followup.send(content = f"{Assets.green_tick} **Account linked successfully.**")

        else: await interaction.followup.send(content = f"{Assets.red_tick} **Unmatched code. Please try again.**")

        
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        await interaction.followup.send(error)
        
class verify(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'link', description = "Links your Discord with a LeetCode account")
    @app_commands.describe(username = "Specify a username")
    async def _link(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer(thinking = True)
        user_info = LC_utils.get_user_profile(username)
        if user_info:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 5))   
            view = ConfirmView(code = code, username = username, user_id = interaction.user.id, client = self.client)
            await interaction.followup.send(f"**Please paste this code `{code}` at the start of your [profile summary](https://leetcode.com/profile/), then click the button below**", view = view)
            view.response = await interaction.original_response()
        else:
            await interaction.followup.send(f"{Assets.red_tick} **Username doesn't exist, please double check.**")

async def setup(client):
    await client.add_cog(verify(client), guilds=[discord.Object(id=1085444549125611530)])
    #await client.add_cog(verify(client))