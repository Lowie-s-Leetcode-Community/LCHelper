import discord
from discord import app_commands, Embed
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
from cogs.cmd_interface.quiz import createEmbed

iconKey = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫']
keyAns = ['A. ', 'B. ', 'C. ', 'D. ', 'E. ', 'F. ']
quiz_bonus = 1
test_quiz_channel_id = 1258083345133207635
COG_START_TIMES = [
    datetime.time(hour=0, minute=5, tzinfo=datetime.timezone.utc)
]

class DailyAutomation(commands.Cog):
    def __init__(self, client):
        self.client = client
        if os.getenv('START_UP_TASKS') == "True":
            self.daily.start()
        self.logger = Logger(client)
        self.last_quiz = None
        self.last_quiz_message = None
        self.correct_users = set()

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
        quiz_detail = {}
        quiz_result = self.client.db_api.read_quiz(quiz_detail)

        guild = await self.client.fetch_guild(self.client.config['serverId'])
        log_channel = await guild.fetch_channel(test_quiz_channel_id)
        quiz_message = await log_channel.send(embed = createEmbed(quiz_result[0], quiz_result[1]))
        answers = quiz_result[1]
        for i in range(len(answers)):
            await quiz_message.add_reaction(iconKey[i])
        
        self.last_quiz = quiz_result
        self.last_quiz_message = quiz_message
        
    async def handle_prev_quiz_answers(self): 
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        log_channel = await guild.fetch_channel(test_quiz_channel_id)
        self.correct_users.clear()
        if (self.last_quiz == None):
            await log_channel.send("There is no previous daily quiz.")
            return
        correct_answer = self.last_quiz[0].correctAnswerId - self.last_quiz[1][0].id
        correct_emoji = iconKey[correct_answer]
        self.last_quiz_message = await log_channel.fetch_message(self.last_quiz_message.id)

        answered_members = set()
        for reaction in self.last_quiz_message.reactions:
            async for user in reaction.users():
                if user != self.client.user:
                    if user not in answered_members and reaction.emoji != correct_emoji:
                        answered_members.add(user)
                    # Who answers the quiz correctly gets 1 point
                    elif user not in self.correct_users and reaction.emoji == correct_emoji: 
                        self.correct_users.add(user)
                    await self.client.db_api.update_score(str(user.id), quiz_bonus, "Correct answer for the daily quiz.")
        answered_members = answered_members & self.correct_users
        self.correct_users = self.correct_users - answered_members

        await self.send_correct_users_list(log_channel)

    async def send_correct_users_list(self, channel):
        if self.correct_users:
            x = len(self.correct_users)
            if x == 1: 
                description = "There is only one member who answered the previous quiz correctly"
            else:
                description = f"There are {x} members who answered the previous daily quiz correctly"
            embed = Embed(colour = discord.Colour.dark_teal(), description = description,
                          title="Daily Quiz - List of users answering correctly")
            i = 1
            for user in self.correct_users:
                embed.add_field(name = "", value = f"**{i}.** {user.name}", inline = False)
                i = i + 1
                # print(user.name)
            await channel.send(embed=embed)
            
        else:
            # print("No one answered the previous daily quiz correctly.")
            await channel.send("No one answered the previous daily quiz correctly.")

    # def createEmbed(self,_question, _answer):
    #     question = _question
    #     answers = _answer

    #     embed = discord.Embed(
    #         color= getattr(Assets, question.difficulty.lower())
    #     )
    #     embed.set_author(
    #         name="Quiz:",
    #         icon_url="https://assets.leetcode.com/users/leetcode/avatar_1568224780.png"
    #     )
    #     embed.add_field(
    #         name=question.question,
    #         value="",
    #         inline=False
    #     )

    #     embed.add_field(
    #         name="Difficulty",
    #         value=question.difficulty,
    #         inline=True
    #     )

    #     embed.add_field(
    #         name="Topic",
    #         value=f"||{question.category}||",
    #         inline=True
    #     )
    #     answer_view = ""

    #     for i in range(len(answers)):
    #         answer_view += f"```\n{keyAns[i] + answers[i].answer}\n```"
        
    #     embed.add_field(
    #         name="Answer",
    #         value=answer_view,
    #         inline=False
    #     )
    #     return embed

    @tasks.loop(time=COG_START_TIMES)
    async def daily(self):
        await self.logger.on_automation_event("Daily", "handle_prev_quiz_answers()")
        await self.handle_prev_quiz_answers()
        await self.logger.on_automation_event("Daily", "start-daily")
        await self.logger.on_automation_event("Daily", "create_new_daily_object()")
        daily_challenge_info = await self.create_new_daily_object()
        await self.logger.on_automation_event("Daily", "create_daily_thread()")
        await self.create_daily_thread(daily_challenge_info)
        
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
        # await self.logger.on_automation_event("Daily", "handle_prev_quiz_answers()")
        # await self.handle_prev_quiz_answers()
        # await self.logger.on_automation_event("Daily", "create_daily_quiz()")
        # await self.create_daily_quiz()

async def setup(client):
    await client.add_cog(DailyAutomation(client), guilds=[discord.Object(id=client.config['serverId'])])
