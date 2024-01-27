import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from typing import Optional

# really need better ways to place this arg :)
from database_api_layer.api import DatabaseAPILayer
db_api = DatabaseAPILayer()

class Profile(commands.Cog):
    def __init__(self, client):
        self.client = client

    # will add feature to get from username next!
    @app_commands.command(name = 'profile', description = "Returns a Leetcode profile")
    @app_commands.describe(member = "Specify a member. Left empty if you want to check yours")
    async def _profile(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        await interaction.response.defer(thinking = True)

        result = None
        if member == None:
            discord_id = str(interaction.user.id)
            result = db_api.getProfile(member = str(discord_id))
            # What if result is not available?
        else:
            result = db_api.getProfile(member = str(member.id))
            # This also?
        
        # Will wait for leetcode layer to add more info
        # missing: streak, server rank
        embed = discord.Embed(
            description = f"""
            Type `/help profile` to further understand how this feature works!
            """,
            color = 0xffffff
        )
        embed.add_field(
            name = "🏡 Server Profile",
            value = f"""
            ▸ **Leetcode ID**: {result['leetcodeUsername']}
            ▸ **Date Joined**: {result['createdAt'].strftime("%b %d, %Y")}

            ▸ **Current month**:
            {Assets.blank} ▸ **Score:** {result['monthly']['score']}
            {Assets.blank} ▸ **Rank:** {result['monthly']['rank']}

            ▸ **Today progress**:
            {Assets.blank} ▸ **Score:** {result['daily']['scoreEarned']}
            {Assets.blank} ▸ **Solved Daily:** {result['daily']['solvedDaily']}
            {Assets.blank} ▸ **Practiced Easy:** {result['daily']['solvedEasy']}
            {Assets.blank} ▸ **Practiced Medium:** {result['daily']['solvedMedium']}
            {Assets.blank} ▸ **Practiced Hard:** {result['daily']['solvedHard']}
            {Assets.blank} ▸ **Rank:** {result['daily']['rank']}
            """,
            inline = False
        )
        embed.set_author(
            name = f"LeetCode profile for {interaction.user}",
            icon_url = "https://assets.leetcode.com/users/leetcode/avatar_1568224780.png",
            url = result['link']
        )
        # embed.set_thumbnail(
        #     url = info['profile']['avatar']
        # )
        await interaction.followup.send(embed = embed)

    @app_commands.command(name = 'verify', description = "Sets a role for verified members")
    @app_commands.describe(role = "Choose a role")
    @app_commands.checks.has_permissions(administrator = True)
    async def _verify(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer(thinking = True)

        lc_db = self.client.DBClient['LC_db']
        lc_col = lc_db['LC_config']
        lc_query = {}
        lc_result = lc_col.find_one(lc_query)
        if lc_result:
            lc_update = {'$set': {'verified_role_id': role.id}}
            lc_col.update_one(lc_query, lc_update)
        else:
            lc_col.insert_one({'server_id': interaction.guild_id, 'verified_role_id': role.id})
        await interaction.followup.send(f"{Assets.green_tick} **Verified role has been set to {role.mention}**")

    @app_commands.command(name = 'serverstats', description = "Server statistics fof LLC")
    @app_commands.checks.has_permissions(administrator = True)
    async def _serverstats(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)

        lc_db = self.client.DBClient['LC_db']
        lc_col = lc_db['LC_users']
        embed = discord.Embed(
            title = "Server stats",
            color = discord.Color.blue()
        )
        embed.add_field(
            name = "Total members", 
            value = f"{interaction.guild.member_count}"
        )
        role = discord.utils.find(lambda m: m.id == 1087761988068855890, interaction.guild.roles)
        embed.add_field(
            name = "Verified members",
            value = len(role.members)
        )
        lc_member = list(lc_col.find())
        active_member_count = 0
        for member in lc_member:
            if member['current_month']['score'] > 0: active_member_count += 1
        
        embed.add_field(
            name = "Active members",
            value = f"{active_member_count}"
        )
    
        await interaction.followup.send(embed = embed)

async def setup(client):
    await client.add_cog(Profile(client), guilds=[discord.Object(id=1085444549125611530)])
