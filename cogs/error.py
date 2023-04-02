import discord
from discord.ext import commands
from datetime import datetime
import random
import json
from utils.asset import Assets
class error(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{Assets.red_tick} **You don't have the permission to execute this command.**")
        elif isinstance(error, commands.CommandNotFound):
            return
        else: await ctx.send(f"{Assets.red_tick} **`{error}` ({ctx.command})**")
        print(error)
    

async def setup(client):
    await client.add_cog(error(client))
