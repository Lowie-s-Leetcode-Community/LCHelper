import discord
from discord import app_commands
from discord.ext import tasks, commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
import os
import asyncio
import traceback
import datetime
from utils.llc_datetime import get_today
from utils.logger import Logger
from lib.embed.problem import ProblemEmbed

import random

iconKey = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫']

COG_START_TIMES = [
    datetime.time(hour=0, minute=5, tzinfo=datetime.timezone.utc)
]

last_quiz = None
last_quiz_message = None

class DailyAutomation(commands.Cog):
    def __init__(self, client):
        self.client = client
        if os.getenv('START_UP_TASKS') == "True":
            self.daily.start
        self.logger = Logger(client)

    def cog_unload(self):
        self.daily.cancel()

    async def create_new_daily_object(self):
        # {'date': '2024-02-09', 'link': 'https://leetcode.com/problems/largest-divisible-subset/', 'title': 'Largest Divisible Subset', 'title_slug': 'largest-divisible-subset', 'id': '368'}
        daily_challenge_info = LC_utils.get_daily_challenge_info()
        await self.client.db_api.create_or_keep_daily_object(daily_challenge_info['id'], get_today())
        return daily_challenge_info

    async def create_daily_thread(self, daily_challenge_info):
        # Creating daily thread
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['dailyThreadChannelId'])
        name = f"[{daily_challenge_info['date']}] LeetCode P{daily_challenge_info['id']}"
        thread = await channel.create_thread(name = name, type = discord.ChannelType.public_thread)

        # Calling /daily automatically
        daily_obj = self.client.db_api.read_latest_daily_object()
        problem = daily_obj['problem']
        embed = ProblemEmbed(problem)

        display_date = daily_obj['generatedDate'].strftime("%b %d, %Y")
        
        await thread.send(f"Daily Challenge - {display_date}", embed = embed)
        return 
    
    async def create_daily_quiz(self): 
        global last_quiz
        global last_quiz_message
        quiz_detail = {}
        quiz_result = self.client.db_api.read_quiz(quiz_detail)

        guild = await self.client.fetch_guild(self.client.config['serverId'])
        # đang để tạm id channel cần gửi dailyquiz
        log_channel = await guild.fetch_channel(1258083345133207635)
        quiz_message = await log_channel.send(embed = self.createEmbed(quiz_result[0], quiz_result[1]))
        answers = quiz_result[1]
        for i in range(len(answers)):
            await quiz_message.add_reaction(iconKey[i])
        
        last_quiz = quiz_result
        last_quiz_message = quiz_message
        
    async def handle_preQuiz_answers(self): 
        global correct_users
        global last_quiz_message
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        # đang để tạm id channel cần gửi dailyquiz
        channel = await guild.fetch_channel(1258083345133207635)
        
        if (last_quiz == None):
            print("No quiz before!")
            return
        correct_answer = last_quiz[0].correctAnswerId - last_quiz[1][0].id
        correct_emoji = iconKey[correct_answer]
        last_quiz_message = await channel.fetch_message(last_quiz_message.id)

        for reaction in last_quiz_message.reactions:
            if reaction.emoji == correct_emoji:
                async for user in reaction.users():
                    if user != self.client.user:
                        # who answers the quiz correctly gets 1 point
                        await self.client.db_api.update_score(str(user.id), 1, "Correct answer daily quiz")

    def createEmbed(self,_question, _answer):
        question = _question
        answers = _answer

        embed = discord.Embed(
            color= getattr(Assets, question.difficulty.lower())
        )
        embed.set_author(
            name="Quiz:",
            icon_url="https://assets.leetcode.com/users/leetcode/avatar_1568224780.png"
        )
        embed.add_field(
            name=question.question,
            value="",
            inline=False
        )

        embed.add_field(
            name="Difficulty",
            value=question.difficulty,
            inline=True
        )

        embed.add_field(
            name="Topic",
            value=f"||{question.category}||",
            inline=True
        )
        answer_view = ""

        for i in range(len(answers)):
            answer_view += f"```\n{iconKey[i] + answers[i].answer}\n```"
        
        embed.add_field(
            name="Answer",
            value=answer_view,
            inline=False
        )
        return embed

    @tasks.loop(time=COG_START_TIMES)
    async def daily(self):
        await self.logger.on_automation_event("Daily", "start-daily")
        await self.logger.on_automation_event("Daily", "create_new_daily_object()")
        daily_challenge_info = await self.create_new_daily_object()
        await self.logger.on_automation_event("Daily", "create_daily_thread()")
        await self.create_daily_thread(daily_challenge_info)
        await self.logger.on_automation_event("Daily", "handle_preQuiz_answers()")
        await self.handle_preQuiz_answers()
        await self.logger.on_automation_event("Daily", "create_daily_quiz()")
        await self.create_daily_quiz()
        
        # await self.prune_unverified_members()
        await self.logger.on_automation_event("Daily", "end-daily")

    @daily.error
    async def on_error(self, exception):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['serverId'])
        await channel.send(f"Daily initiate error:\n```py\n{traceback.format_exc()[:800]}```\nPlease re-start.")
        await self.logger.on_automation_event("Daily", "error found")

        self.daily.restart()

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def stop_daily(self, ctx):
        self.daily.stop()
        await ctx.send(f"{Assets.green_tick} **Daily task stopped.**")

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def start_daily(self, ctx):
        self.daily.start()
        await ctx.send(f"{Assets.green_tick} **Daily task started.**")

    @app_commands.command(name="daily_simulate", description="Simulate a daily crawl cycle.")
    @app_commands.checks.has_permissions(administrator = True)
    async def _daily_simulate(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        await self.daily()
        await interaction.followup.send(f"{Assets.green_tick} **Daily Task finished**")

async def setup(client):
    await client.add_cog(DailyAutomation(client), guilds=[discord.Object(id=client.config['serverId'])])
