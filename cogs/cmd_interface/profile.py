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
    async def _profile(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        await interaction.response.defer(thinking = True)

        result = None
        embed = discord.Embed(
            description = f"""
            Type `/help profile` to further understand how this feature works!
            """,
            color = 0xffffff
        )
        if member == None:
            discord_id = interaction.user.id
            result = self.client.db_api.read_profile(memberDiscordId = str(discord_id))
            if result == None:
                embed = discord.Embed(
                    title = "Error",
                    description = "Are *you* verified? Type `/verify` to (re)verify yourself immediately!",
                    color = 0xef4743
                )
        else:
            result = self.client.db_api.read_profile(memberDiscordId = str(member.id))
            if result == None:
                embed = discord.Embed(
                    title = "Error",
                    description = "Is this person verified?",
                    color = 0xef4743
                )
        # Will wait for leetcode layer to add more info
        # missing: streak
        if result != None:
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
                name = f"LeetCode profile for {interaction.user}",
                icon_url = "https://assets.leetcode.com/users/leetcode/avatar_1568224780.png",
                url = result['link']
            )
        await interaction.followup.send(embed = embed)

async def setup(client):
    await client.add_cog(Profile(client), guilds=[discord.Object(id=1085444549125611530)])
