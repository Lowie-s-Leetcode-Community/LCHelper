import discord
from discord.ext import commands, tasks
from discord.utils import get
from discord import Interaction, app_commands
from discord.app_commands import AppCommandError
import os
import asyncio
from dotenv import load_dotenv
from utils.asset import Assets
import traceback
from pathlib import Path
import logging
from database_api_layer.api import DatabaseAPILayer

load_dotenv()

intent = discord.Intents.all()
client = commands.Bot(command_prefix = os.getenv('BOT_PREFIX'), case_insensitive = True, intents = intent)
activity = discord.Activity(name = 'Lowie', type = discord.ActivityType.playing)
token = os.getenv('BOT_TOKEN')
tree = client.tree
log_handler = logging.FileHandler(filename = "discord.log", encoding = "utf-8", mode = "w")

db_api = DatabaseAPILayer(client)
client.db_api = db_api
client.config = db_api.read_latest_configs()

async def main():
    async with client:
        # Loading extensions
        for (dirpath, dirnames, filenames) in os.walk(r"./cogs"):
            for filename in filenames:
                if filename.endswith('.py'):
                    try:
                        path = f"{dirpath[2:]}\{filename[:-3]}".replace('\\', '.').replace('/', '.')
                        await client.load_extension(path)
                        print(f"{filename}: ok!")
                    except Exception as e:
                        print(f"{filename}: not ok!! - {e}")
        await client.load_extension("jishaku")

        # Loading Discord client
        await client.start(token)


@tree.error
async def on_app_command_error(interaction: Interaction, error: AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.followup.send("You don't have the permission to execute this command")
    elif isinstance(error, app_commands.CommandNotFound):
        return
    else:
        await interaction.followup.send(f"```py\n{traceback.format_exc()[:800]}```")
    print(error)

@tree.error
async def on_error(interaction: Interaction, error: AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.followup.send("You don't have the permission to execute this command")
    elif isinstance(error, app_commands.CommandNotFound):
        return
    else:
        print(traceback.format_exc())
        await interaction.followup.send(f"```py\n{traceback.format_exc()[:800]}```")

asyncio.run(main())