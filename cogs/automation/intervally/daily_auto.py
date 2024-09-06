import datetime
import os
import random
import traceback

import discord
from discord import app_commands
from discord.ext import commands, tasks

from lib.embed.contest_embed import ContestEmbed
from lib.embed.problem import ProblemEmbed
from utils.asset import Assets
from utils.lc_utils import LC_utils
from utils.llc_datetime import get_today
from utils.logger import Logger

COG_START_TIMES = [
    datetime.time(hour=0, minute=5, tzinfo=datetime.timezone.utc)
]

REMINDER_MESSAGES = {
    datetime.time(hour=8, minute=30, tzinfo=datetime.timezone.utc): f"Hi {{mention}}, it's your turn to write the editorial today! Please complete it by 6pm to help other community members in need! {Assets.blob_victory}",
    datetime.time(hour=15, minute=00, tzinfo=datetime.timezone.utc): f"Hi {{mention}}, remember to turn in your editorial by 6PM today! {Assets.blob_maman}",
    datetime.time(hour=18, minute=30, tzinfo=datetime.timezone.utc): f"Hi {{mention}}, please turn in your editorial immediately! If you need help, please contact Community members for help! {Assets.blob_taco}"
}


class DailyReminder(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.task_completed = False
        self.reminder_task.start()
        self.daily_thread = None
        self.problem = None
        self.assignee_id = None

    @tasks.loop(minutes=1)
    async def reminder_task(self):
        now = datetime.datetime.now()
        current_time = datetime.time(hour=now.hour, minute=now.minute, tzinfo=datetime.timezone.utc)

        if current_time not in REMINDER_MESSAGES.keys():
            return

        if not self.task_completed:
            await self.send_reminder(current_time)

            if current_time == max(REMINDER_MESSAGES.keys()) and not self.task_completed:
                await self.notify_experts()

    async def send_reminder(self, reminder_time):
        if not self.daily_thread:
            return

        guild = await self.client.fetch_guild(self.client.config['serverId'])
        assignee = None
        message = REMINDER_MESSAGES.get(reminder_time)

        if self.assignee_id == "EXPERT":
            expert_role = discord.utils.get(guild.roles, name="Community Expert")
            if expert_role:
                await self.daily_thread.send(message.format(mention=expert_role.mention))
        else:
            result = self.client.db_api.read_profile(memberDiscordId=str(self.assignee_id))
            assignee = await self.client.fetch_user(result['discordId'])
            if assignee:
                await self.daily_thread.send(message.format(mention=assignee.mention))

    async def notify_experts(self):
        expert_channel = await self.client.fetch_channel("1085446453230571520")
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        expert_role = discord.utils.get(guild.roles, name="Community Expert")

        if self.assignee_id and expert_channel:
            if self.assignee_id == "EXPERT":
                await expert_channel.send(
                    f"{expert_role.mention}: Attention all Community Experts!\n\n"
                    f"Today's editorial task has been assigned to an expert, but we need to make sure it's done on time. "
                    f"Please review the work or step in if necessary, ASAP. Thank you!"
                )
            else:
                result = await self.client.db_api.read_profile(memberDiscordId=str(self.assignee_id))
                assignee = await self.client.fetch_user(result['discordId'])

                await expert_channel.send(
                    f"{expert_role.mention}: Houston, we've got a problem!\n\n"
                    f"Seems like {assignee.mention} needs our help on turning in the solution for the daily problem today. " 
                    f"Please contact them directly to help, and assign substitution if needed!"
                )

    async def get_assignee_id_today(self):
        weekday = datetime.date.today().weekday()  # 0 = Monday, 6 = Sunday
        with open("resrc/weekly.txt", "r") as file:
            assignees = [line.strip() for line in file if line.strip()]

        if weekday >= len(assignees):
            return None

        assignee_id = assignees[weekday]

        if assignee_id == "EXPERT":
            return assignee_id
        else:
            result = self.client.db_api.read_profile(memberDiscordId = str(assignee_id))
            assignee = await self.client.fetch_user(result['discordId'])
            if assignee:
                return assignee_id

        return None

    async def run_score_add(self, interaction: discord.Interaction, assignee):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        difficulty_scores = {
            'Easy': 8,
            'Medium': 10,
            'Hard': 12
        }
        score_value = difficulty_scores.get(self.problem['difficulty'])

        today = datetime.date.today().strftime("%B %d")
        reason = f"{today} Daily Editorial ({self.problem['difficulty']})"

        # Add score
        await interaction.response.defer(thinking = True)
        await self.client.db_api.update_score(str(assignee), score_value, reason)
        await interaction.followup.send(f"{Assets.green_tick} **Score added.**")


class DailyAutomation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.daily_reminder = DailyReminder(client)
        if os.getenv('START_UP_TASKS') == "True":
            self.daily.start()
        self.logger = Logger(client)

    async def cog_unload(self):
        self.daily.cancel()

    async def create_new_daily_object(self):
        # {'date': '2024-02-09', 'link': 'https://leetcode.com/problems/largest-divisible-subset/', 'title': 'Largest Divisible Subset', 'title_slug': 'largest-divisible-subset', 'id': '368'}
        daily_challenge_info = LC_utils.get_daily_challenge_info()
        await self.client.db_api.create_or_keep_daily_object(daily_challenge_info['id'], get_today())
        return daily_challenge_info

    async def create_daily_thread(self, daily_challenge_info):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['dailyThreadChannelId'])
        name = f"[{daily_challenge_info['date']}] LeetCode P{daily_challenge_info['id']}"
        thread = await channel.create_thread(name=name, type=discord.ChannelType.public_thread)

        daily_obj = self.client.db_api.read_latest_daily_object()
        self.daily_reminder.problem = daily_obj['problem']
        embed = ProblemEmbed(daily_obj['problem'])

        display_date = daily_obj['generatedDate'].strftime("%b %d, %Y")
        await thread.send(f"Daily Challenge - {display_date}", embed=embed)

        self.daily_reminder.daily_thread = thread
        self.daily_reminder.assignee_id = await self.daily_reminder.get_assignee_id_today()

        return thread
    
    async def remind_unverified(self):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel("1090084731560927274")
        random_prompts = [
            f"{Assets.blob_victory} {Assets.blob_victory} Hãy sử dụng lệnh {Assets.link_command} để kết nối tài khoản Leetcode của mình và khám phá những tính năng độc đáo của chúng mình nhé!",
            f"Hãy {Assets.link_command} tài khoản bằng LLC Assistant để luyện tập cùng chúng mình nào! {Assets.blob_taco} {Assets.blob_taco}",
            f"Ồ, chào bạn. Có vẻ bạn quên {Assets.link_command} tài khoản Leetcode nè! {Assets.blob_maman} {Assets.blob_taco}",
            f":eyes: :eyes: Bạn có biết, {Assets.link_command} tài khoản Leetcode với chúng mình sẽ giúp bạn đạt mục tiêu dễ dàng hơn?",
            f":100: :100: :100: :100: :100: Đã có trên 200 người {Assets.link_command} tài khoản với chúng mình. Một phần không nhỏ đã đạt được mục tiêu 500 bài. Liệu bạn có phải người tiếp theo? {Assets.blob_taco} {Assets.blob_taco}",
            f":beers: :game_die: {Assets.link_command} tài khoản, tham gia cùng server, để không bỏ lỡ thông báo mới nhất về các buổi offline nhé! {Assets.blob_taco} {Assets.blob_taco} {Assets.blob_taco}",
            f":eyes: {Assets.blob_taco} {Assets.blob_taco} Chúng mình có bí kíp code khủng mà vẫn được chạm cỏ thường xuyên. :eyes: :eyes: -> {Assets.link_command}",
        ]
        prompt = random.choice(random_prompts)
        await channel.send(f"<@&{self.client.config['unverifiedRoleId']}> {prompt}")

    async def contest_remind(self):
        next_contests = LC_utils.get_next_contests_info()
        current_time = datetime.datetime.now()
        time_in_24h = current_time + datetime.timedelta(days=1)
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['dailyThreadChannelId'])
        embeds = []
        for contest in next_contests:
            if current_time.timestamp() <= contest["timestamp"] <= time_in_24h.timestamp():
                embeds.append(ContestEmbed(contest))

        if len(embeds) == 0:
            return

        message = f"<@&{self.client.config['verifiedRoleId']}> :bangbang: :ninja: There is a contest today!"
        await channel.send(message, embeds=embeds)

    @tasks.loop(time=COG_START_TIMES)
    async def daily(self):
        await self.logger.on_automation_event("Daily", "start-daily")
        await self.logger.on_automation_event("Daily", "create_new_daily_object()")
        daily_challenge_info = await self.create_new_daily_object()
        await self.logger.on_automation_event("Daily", "create_daily_thread()")
        await self.create_daily_thread(daily_challenge_info)
        await self.logger.on_automation_event("Daily", "contest_remind()")
        await self.contest_remind()
        await self.logger.on_automation_event("Daily", "remind_unverified()")
        await self.remind_unverified()
        await self.logger.on_automation_event("Daily", "end-daily")

    @daily.error
    async def on_error(self):
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
        if self.daily_reminder.task_completed:
            await interaction.response.send_message("Solution have been accepted!")
            return

        assignee_id = self.daily_reminder.assignee_id
        guild = interaction.guild
        expert_role = discord.utils.get(guild.roles, name="Community Expert")

        if assignee_id == "EXPERT":
            if expert_role in interaction.user.roles:
                await interaction.response.send_message(
                    f"{interaction.user.mention}, as a Community Expert, you've turned in the solution. "
                    f"Other experts, please review it."
                )
            else:
                await interaction.response.send_message(
                    f"{interaction.user.mention}, you do not have the Community Expert role and cannot turn in this editorial."
                )
            return

        result = self.client.db_api.read_profile(memberDiscordId = str(assignee_id))
        assignee = await self.client.fetch_user(result['discordId'])

        await interaction.response.defer(thinking=True)

        if interaction.user == assignee:
            await interaction.followup.send(
                f"{assignee.mention} has turned in their solution. Experts, please review it."
            )
        else:
            await interaction.followup.send(
                f"{interaction.user.mention}, you are not the assignee for today's editorial. Please wait for your turn."
            )

    @app_commands.command(name = 'accept_editorial', description = "Accept the editorial")
    async def _accept_editorial(self, interaction: discord.Interaction):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        expert_role = discord.utils.get(guild.roles, name="Community Expert")

        if self.daily_reminder.task_completed:
            await interaction.response.send_message("Solution have been accepted!")
            return

        assignee_id = self.daily_reminder.assignee_id
        if not assignee_id:
            await interaction.response.send_message("There is no assignee found for today's editorial.")
            return

        if assignee_id == "EXPERT":
            self.daily_reminder.task_completed = True
            await interaction.response.send_message(
                "Editorial has been accepted. The score will be handled manually."
            )
            return

        if expert_role not in interaction.user.roles:
            await interaction.response.send_message(
                "You are not a Community Expert and don't have the privilege to accept the editorial."
            )
            return

        self.daily_reminder.task_completed = True
        await self.daily_reminder.run_score_add(interaction, assignee_id)

async def setup(client):
    await client.add_cog(DailyAutomation(client), guilds=[discord.Object(id=client.config['serverId'])])
