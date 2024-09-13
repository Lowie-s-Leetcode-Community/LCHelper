import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from typing import Optional

class Profile(commands.Cog):
    def __init__(self, client):
        self.client = client

    # will add feature to get from username next!
    @app_commands.command(name = 'profile', description = "Returns a Leetcode profile")
    @app_commands.describe(member = "Specify a member. Left empty if you want to check yours")
    async def _profile(self, interaction: discord.Interaction, member: Optional[discord.Member] = None, username : str = None):
        await interaction.response.defer(thinking = True)
        if member == None and username == None:
           discord_id = interaction.user.id
           embed = await self._find_profile_by_member(self, member=member, discord_id=discord_id)
           await interaction.followup.send(embed = embed)
           return
              
        if member != None:
           discord_id = member.id
           embed = await self._find_profile_by_member(self, member = member, discord_id = discord_id)
           await interaction.followup.send(embed = embed)
           return
        
        discord_id = interaction.user.id
        embed = await Profile._find_profile_by_username(self, username = username, discord_id = discord_id)
        await interaction.followup.send(embed = embed)
        return
  
    async def _find_profile_by_member(self, member: Optional[discord.Member], discord_id = None):
        result = None
        embed = discord.Embed(
            description = f"""
            Type `/help profile` to further understand how this feature works!
            """,
            color = 0xffffff
        )
        result = self.client.db_api.read_profile(memberDiscordId = str(discord_id))
        if result == None:
            embed = discord.Embed(
                title = "Error",
                description = "This account (or your account) is not verified yet. Please use /verify to verify if it's your account",
                color = 0xef4743
            )
        # Will wait for leetcode layer to add more info
        # missing: streak
        if result != None:
            # Get Discord user by ID
            discord_user = await self.client.fetch_user(result['discordId'])
            embed.set_thumbnail(url=discord_user.display_avatar)
            embed.add_field(
                name = "🏡 Server Profile",
                value = f"""
                ▸ **Leetcode ID**: {result['leetcodeUsername']}
                ▸ **Date Joined**: {result['createdAt'].strftime("%b %d, %Y")}

                ▸ **Current month**:
                {Assets.blank} ▸ **Score:** {result['monthly']['scoreEarned']}
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
                name = f"LeetCode profile for {discord_user.display_name}",
                icon_url = "https://assets.leetcode.com/users/leetcode/avatar_1568224780.png",
                url = result['link']
            )
        return embed



    async def _find_profile_by_username(self, username : str, discord_id):
        embed = discord.Embed(
            description = f"""
            Type '/help profile' to further understand how this feature works!'
            """,
            color = 0xffffff
        )
        result = LC_utils.get_user_profile(username = username)

        if result == None:
            #Invalid username case
            embed = discord.Embed(
                title = "Error",
                description = "The user you seek doesn't exist",
                color = 0xef4743
            )
        else:
            #Return the information
            discord_user = await self.client.fetch_user(str(discord_id))
            embed.set_thumbnail(url=result['profile']['avatar'])
            embed.add_field(
                name = "🏡 Leetcode profile",
                value = f"""
                ▸ **Leetcode ID**: {username}
                {Assets.blank} ▸ **Name**: {result['profile']['name']}
                {Assets.blank} ▸ **Ranking**: {result['profile']['rank']}
                {Assets.blank} ▸ **Country**: {result['profile']['country']}
                """,
                inline = False
            )
            embed.set_author(
                name = f"LeetCode profile requested from {discord_user.display_name}",
                icon_url = "https://assets.leetcode.com/users/leetcode/avatar_1568224780.png",
                url = result['profile']['link']
            )
        return embed
    

async def setup(client):
    await client.add_cog(Profile(client), guilds=[discord.Object(id=client.config['serverId'])])
