import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from typing import Optional
import random
import string
import datetime
from database_api_layer.api import DatabaseAPILayer

class ConfirmView(discord.ui.View):
    def __init__(self, client, code, username, user_id):
        super().__init__(timeout = 300)
        self.code = code
        self.client = client
        self.username = username
        self.user_id = user_id
        self.response = None
        self.db_api = DatabaseAPILayer(client)
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
            child.label = "Timeout!"
            child.emoji = "⏰"
        await self.response.edit(view = self)

    # TODO: handle "update user"
    @discord.ui.button(label = "Verify Me!", style = discord.ButtonStyle.primary)
    async def call_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        assert interaction.user.id == self.user_id
        await interaction.response.defer(thinking = True)
        user_info = LC_utils.get_user_profile(self.username)
        if len(user_info['profile']['summary']) >= 5 and user_info['profile']['summary'][0:5] == self.code:
            user_obj = {
                'discordId': str(interaction.user.id),
                'leetcodeUsername': self.username,
                'mostRecentSubId': -1,
                'userSolvedProblems': []
            }

            # append missing info:
            recent_info = LC_utils.get_recent_ac(self.username, 20)
            if len(recent_info) > 0:
                user_obj['mostRecentSubId'] = recent_info[0]['id']
                for info in recent_info:
                    user_obj['userSolvedProblems'].append(info['titleSlug'])
            member = await interaction.guild.fetch_member(interaction.user.id)

            # TODO: refactor to lc_config in db
            verified_role_id = 1087761988068855890
            unverified_role_id = 1157694438152347758
            verified_role = discord.utils.get(interaction.guild.roles, id = verified_role_id)
            unverified_role = discord.utils.get(interaction.guild.roles, id = unverified_role_id)
            try:
                await self.db_api.create_user(user_obj)
            except:
                await interaction.followup.send(content = f"{Assets.red_tick} **There's a problem when verifying. Someone in this server might have already linked with this account**")
            else: 
                await member.add_roles(verified_role)
                await member.remove_roles(unverified_role)
                await interaction.followup.send(content = f"{Assets.green_tick} **Account linked successfully.**")
        else: await interaction.followup.send(content = f"{Assets.red_tick} **Unmatched code. Please try again.**")
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        await interaction.followup.send(error)
        
class verify(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db_api = DatabaseAPILayer(client)

    @app_commands.command(name = 'link', description = "Links your Discord with a LeetCode account")
    @app_commands.describe(username = "Specify a username")
    async def _link(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer(thinking = True)
        user_profile = self.db_api.read_profile(str(interaction.user.id))
        if user_profile != None:
            await interaction.followup.send(f"You've already linked your profile.\
                Please contact Core members for support if you want to re-link to another profile!")
            return

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