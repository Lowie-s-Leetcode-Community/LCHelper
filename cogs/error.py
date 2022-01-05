import discord
from discord.ext import commands
from datetime import datetime
import random
import json
from utils.asset import Assets
class bot_related(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the permission to execute this command")
        elif isinstance(error, commands.CommandNotFound):
            return
        else: await ctx.send(f"{Assets.red_tick} **`{error}` ({ctx.command})**")
        print(error)

def setup(client):
    client.add_cog(bot_related(client))
