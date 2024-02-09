import discord
import asyncio
import datetime 
import time
from discord.ext import commands, tasks
from utils.asset import Assets
from utils.logger import Logger
import os
import traceback
import json

class PublicLogForwarding(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.logger = Logger(client)

    @commands.Cog.listener()
    async def on_message(self, message):
      if not message.content.startswith(f"{os.getenv('LOGGING_PREFIX')}db_log"):
        return

      if len(message.embeds) < 1:
        return
      try:
        json_log = json.loads(message.embeds[0].description)
      except:
        print(f"Not json :( {traceback.format_exc()}")
        return

      content = json_log["content"]
      if json_log["type"] == "Score":
        mention = content["member_mention"]
        delta = content["delta"]
        reason = content["reason"]
        if delta > 0:
          await self.logger.on_score_add(mention, delta, reason)
        elif delta < 0:
          await self.logger.on_score_deduct(mention, delta, reason)
      elif json_log["type"] == "Submission":
        userId = content["userId"]
        problemId = content["problemId"]
        is_daily = content["is_daily"]
        await self.logger.on_submission(userId, problemId, is_daily)

async def setup(client):
    await client.add_cog(PublicLogForwarding(client))
