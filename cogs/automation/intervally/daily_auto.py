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
from cogs.automation.intervally.weekly_auto import WeeklyAutomation
from cogs.cmd_interface.admin import score

COG_START_TIMES = [
    datetime.time(hour=0, minute=5, tzinfo=datetime.timezone.utc)
]

REMINDER_TIMES = [
    datetime.time(hour=8, minute=00, tzinfo=datetime.timezone.utc),
    datetime.time(hour=10, minute=00, tzinfo=datetime.timezone.utc),
    datetime.time(hour=12, minute=00, tzinfo=datetime.timezone.utc)
]

class DailyReminder(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.task_completed = False
        # self.reminder_task.start()
        self.daily_thread = None
        self.problem = None

    # @tasks.loop(minutes=1)
    # async def reminder_task(self):
    #     now = datetime.datetime().now()
    #     for reminder_time in REMINDER_TIMES:
    #         if now.hour == reminder_time.hour and now.minute == reminder_time.minute:
    #             if not self.task_completed:
    #                 await self.send_reminder()

    # async def send_reminder(self):
    #     weekday = datetime.date.today().weekday()
    #     # assignee_list = await WeeklyAutomation.get_member_solve_problem(self.client)
    #     # assignee = assignee_list[weekday]
    #     assignee = interaction.user
    #     print(assignee) # Debug
    #     if assignee:
    #         await self.daily_thread.send(f"{assignee.mention}, Please complete your daily task!")

    async def run_score_add(self, interaction: discord.Interaction, assignee):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['dailyThreadChannelId'])
        if self.problem['difficulty'] == 'Easy':
            score_value = 8
        elif self.problem['difficulty'] == 'Medium':
            score_value = 10
        else:
            score_value = 12

        today = datetime.date.today().strftime("%B %d")
        reason = f"{today} Daily Editorial ({self.problem['difficulty']})"

        # Add score
        await interaction.response.defer(thinking = True)
        if score_value <= 0:
            await interaction.followup.send(f"{Assets.red_tick} **`Score` should be positive. Use `/score deduct` instead.**")
            return
        daily_obj = await self.client.db_api.update_score(str(assignee.id), score_value, reason)
        await interaction.followup.send(f"{Assets.green_tick} **Score added.**")

        # if command:
        #     ctx = await self.client.get_context(interaction)
        #     await command.callback(self, ctx, assignee, score_value, reason)
        # else:
        #     await interaction.response.send_message(f"Command `score add` not found.", ephemeral=True)



class DailyAutomation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.daily_reminder = DailyReminder(client)
        if os.getenv('START_UP_TASKS') == "True":
            self.daily.start()
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
        self.daily_reminder.problem = problem
        embed = ProblemEmbed(problem)

        display_date = daily_obj['generatedDate'].strftime("%b %d, %Y")
        await thread.send(f"Daily Challenge - {display_date}", embed = embed)

        self.daily_reminder.daily_thread = thread

        return thread


    @tasks.loop(time=COG_START_TIMES)
    async def daily(self):
        await self.logger.on_automation_event("Daily", "start-daily")
        await self.logger.on_automation_event("Daily", "create_new_daily_object()")
        daily_challenge_info = await self.create_new_daily_object()
        await self.logger.on_automation_event("Daily", "create_daily_thread()")
        await self.create_daily_thread(daily_challenge_info)
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

    @app_commands.command(name = 'turn_in_daily_editorial', description = "Turn in your editorial for the daily challenge.")
    async def _turn_in_daily_editorial(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        expert_role = discord.utils.get(interaction.guild.roles, name="Community Expert")
        if expert_role:
            await interaction.followup.send(f"{interaction.user.mention} has turned in their solution. , please review it.")

    @app_commands.command(name = 'accept_editorial', description = "Accept the editorial")
    async def _accept_editorial(self, interaction: discord.Interaction):
        weekday = datetime.date.today().weekday()
        assignee = interaction.user
        # assignee_list = await WeeklyAutomation.get_member_solve_problem()
        # assignee = assignee_list[weekday]
        if assignee:
            print(assignee)
            self.task_completed = True
            await self.daily_reminder.run_score_add(interaction, assignee)
            await interaction.response.send_message(f"{assignee.mention}'s editorial has been accepted and scored.")
        else:
            await interaction.response.send_message("The assignee is nowhere to be found!")

async def setup(client):
    await client.add_cog(DailyAutomation(client), guilds=[discord.Object(id=client.config['serverId'])])
