import discord
from discord.ext import commands, tasks
from discord.utils import get
import os
import asyncio
import json
from datetime import datetime
import requests


intent = discord.Intents.all()
client = commands.Bot(command_prefix = "*", case_insensitive = True, intents = intent)
activity = discord.Activity(name='Lowie', type = discord.ActivityType.playing)

@client.event
async def on_ready():
    print("Hi!")
    await client.change_presence(activity = activity)

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                client.load_extension(f'cogs.{filename[:-3]}')
                print(f"{filename}: ok!")
            except Exception as e:
                print(f"{filename}: not ok!! - {e}")

    client.load_extension("jishaku")

client.run('ODg3MDE4MjE5NzMzNDE4MDE2.YT-CFw.wcUp2ScumYGa3JGrBtS7wE1NdtE')
