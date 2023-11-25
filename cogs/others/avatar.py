import discord
from discord import app_commands
from discord.ext import tasks, commands

import asyncio
import traceback

class avatar(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @app_commands.command(name = 'avatar', description = "[BETA] get the avatar")
    async def asking(self, member: Optional[discord.Member] = None ):
        if member == None:
            member = interaction.user
        embed = discord.Embed(
                title = member,
                color = discord.Colour.blue()
                ).set_image(url = member.avatar.url)
        await interaction.followup.send(embed = embed)
        # print(interaction.data)
        # print(question)
        # original_mes = await interaction.original_response()
        # await original_mes.add_reaction("👍")

async def setup(client):
    await client.add_cog(
                ask(client),
                guilds=[discord.Object(id=1085444549125611530)])
