import textwrap
import discord
from discord import app_commands
from discord.ext import tasks, commands
import os
import traceback
import datetime
from utils.asset import Assets
from utils.logger import Logger
from utils.llc_datetime import next_weekday, get_next_LLC_week_and_month
import random

COG_START_TIMES = [
    datetime.time(hour=12, minute=00, tzinfo=datetime.timezone.utc)
]

class WeeklyAutomation(commands.Cog):
    def __init__(self, client):
        self.client = client
        if os.getenv('START_UP_TASKS') == "True":
            self.weekly.start()
            self.weekend.start()
        self.logger = Logger(client)
        self.thread_id = None
        self.message_id = None

    def backtrack_get_member(self, candidates_in_day: list,
                             current_list: list,
                             result: list,
                             frequency: dict,
                             day: int,
                             min_empty: list):
        if day == 7:
            empty = current_list.count({})
            min_empty[0] = min(min_empty[0], empty)
            result.append(current_list.copy())
            return
        if len(candidates_in_day[day]) == 0:
            current_list.append({})
            self.backtrack_get_member(candidates_in_day, current_list, result, frequency, day + 1, min_empty)
            current_list.pop()
            return

        for candidate in candidates_in_day[day]:
            if candidate == current_list[-1] or frequency.get(candidate['id'], 0) >= 2:
                current_list.append({})
                self.backtrack_get_member(candidates_in_day, current_list, result, frequency, day + 1, min_empty)
                current_list.pop()
            else:
                current_list.append(candidate)
                frequency[candidate['id']] = frequency.get(candidate['id'], 0) + 1
                self.backtrack_get_member(candidates_in_day, current_list, result, frequency, day + 1, min_empty)
                frequency[candidate['id']] -= 1
                current_list.pop()

    def cog_unload(self):
        self.weekly.cancel()
        self.weekend.cancel()

    async def create_weekly_thread(self):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        ## Id for Discussion Channel, You should create a column in Config table
        channel = await guild.fetch_channel("1085456207067762738")
        week, month = get_next_LLC_week_and_month()
        message = (f"Form đăng ký chữa Daily tuần {week} tháng {month} đã chính thức mở. "
                   f"Form đăng ký chữa sẽ được mở đến trước 19h ngày Chủ nhật tuần này, "
                   f"mọi người hãy nhanh tay đăng ký để có một tuần hoạt động sôi nổi nhé !!!")
        content, firstday, lastday = self.get_registration_announce_msg(message)
        name = f"Đăng ký chữa Daily tuần {week} tháng {month} ({firstday}/{month} - {lastday}/{month})"
        if firstday > lastday:
            name = f"Đăng ký chữa Daily tuần {week} tháng {month} ({firstday}/{month} - {lastday}/{month + 1})"

        thread = await channel.create_thread(name=name, type=discord.ChannelType.public_thread)
        reg_mes = await thread.send(content)
        await reg_mes.add_reaction("2️⃣")
        await reg_mes.add_reaction("3️⃣")
        await reg_mes.add_reaction("4️⃣")
        await reg_mes.add_reaction("5️⃣")
        await reg_mes.add_reaction("6️⃣")
        await reg_mes.add_reaction("7️⃣")
        await reg_mes.add_reaction("8️⃣")

        self.thread_id = thread.id
        self.message_id = reg_mes.id

        return

    def get_registration_announce_msg(self, message):
        d = datetime.date.today()
        weekdays = []
        next_mon = next_weekday(d, 0)
        weekdays.append(next_mon)
        for i in range(6):
            weekdays.append(next_mon + datetime.timedelta(days=i + 1))

        reg_msg = f"""
        Xin chào buổi tối, các thành viên LLC <@&{self.client.config['verifiedRoleId']}>,
        {message}

        2️⃣: Thứ 2, {weekdays[0]}
        3️⃣: Thứ 3, {weekdays[1]} 
        4️⃣: Thứ 4, {weekdays[2]}
        5️⃣: Thứ 5, {weekdays[3]}
        6️⃣: Thứ 6, {weekdays[4]}
        7️⃣: Thứ 7, {weekdays[5]}
        8️⃣: Chủ Nhật, {weekdays[6]}

        Sincerely,
        """
        return textwrap.dedent(reg_msg), weekdays[0].day, weekdays[6].day


    async def get_candidate(self, user_id, user_name, user_role, guild):
        candidate = {}
        priority = await self.client.db_api.read_priority_candidate(str(user_id))
        role = 0

        #Check role
        CoreMember = discord.utils.get(guild.roles, name = "Core Members")
        if CoreMember in user_role:
            role = 1

        candidate['id'] = user_id
        candidate['name'] = user_name
        candidate['role'] = role
        candidate['score'] = priority['monthScore']
        return candidate

    async def get_member_solve_problem(self):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel("1085456207067762738")
        if self.thread_id is None:
            self.thread_id = channel.last_message_id
        thread = await guild.fetch_channel(self.thread_id)
        if self.message_id is None:
            self.message_id = thread.last_message_id
        message = await thread.fetch_message(self.message_id)

        reactions = message.reactions
        candidates_for_day = [[] for _ in range (7)]
        candidates = {}
        candidates_frequent = {}
        result = []
        idx = 0
        for reaction in reactions:
            async for user in reaction.users():
                if user.bot:
                    continue
                if user.id in candidates:
                    candidates_for_day[idx].append(candidates[user.id])
                else:
                    member = await guild.fetch_member(user.id)
                    member_roles = member.roles

                    if user.id not in candidates_frequent:
                        candidates_frequent[user.id] = 0
                    candidate = await self.get_candidate(user.id,
                                                         user.name,
                                                         member_roles,
                                                         guild)
                    candidates[user.id] = candidate
                    candidates_for_day[idx].append(candidate)
            if len(candidates_for_day[idx]) >= 5:
                candidates_for_day[idx] = random.sample(candidates_for_day[idx], 5)
            idx += 1

        current_list = [{}]
        frequency = {}
        min_empty = [7]
        self.backtrack_get_member(candidates_for_day, current_list, result, frequency, 0, min_empty)
        suitable_list = [lis for lis in result if lis.count({}) == min_empty[0]]
        return random.choice(suitable_list)[1:]


    async def get_announce_form(self):
        candidate = await self.get_member_solve_problem()
        week, month = get_next_LLC_week_and_month()
        EXPERT = 1085445503858249740
        message = f"""
        Danh sách chữa Daily tuần {week} tháng {month}: người chữa + người hỗ trợ (nếu có)

        2️⃣: Thứ 2, <@{candidate[0]['id'] if len(candidate[0]) > 0 else EXPERT}>
        3️⃣: Thứ 3, <@{candidate[1]['id'] if len(candidate[1]) > 0 else EXPERT}>
        4️⃣: Thứ 4, <@{candidate[2]['id'] if len(candidate[2]) > 0 else EXPERT}>
        5️⃣: Thứ 5, <@{candidate[3]['id'] if len(candidate[3]) > 0 else EXPERT}>
        6️⃣: Thứ 6, <@{candidate[4]['id'] if len(candidate[4]) > 0 else EXPERT}>
        7️⃣: Thứ 7, <@{candidate[5]['id'] if len(candidate[5]) > 0 else EXPERT}>
        8️⃣: Chủ Nhật, <@{candidate[6]['id'] if len(candidate[6]) > 0 else EXPERT}>

        Sincerely,
        """

        with open("resrc/weekly.txt", "w+") as wf:
            for i in range(7):
                if len(candidate[i]) > 0:
                    wf.write(f"{candidate[i]['id']}\n")
                else:
                    wf.write(f"EXPERT\n")

        return message

    async def create_weekend_form(self):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel("1085446257847308308")
        message = await self.get_announce_form()
        await channel.send(message)
    @tasks.loop(time=COG_START_TIMES)
    async def weekly(self):
        if datetime.date.today().weekday() != 4:
            return
        await self.logger.on_automation_event("Weekly ", "create_weekly_form")
        await self.create_weekly_thread()

    @weekly.error
    async def on_error(self, exception):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['serverId'])
        await channel.send(f"Weekly initiate error:\n```py\n{traceback.format_exc()[:800]}```\nPlease re-start.")
        await self.logger.on_automation_event("Weekly", "error found")

        self.weekly.restart()

    @tasks.loop(time=COG_START_TIMES)
    async def weekend(self):
        if datetime.date.today().weekday() != 6:
            return

        await self.logger.on_automation_event("Weekend ", "create_weekend_form")
        await self.create_weekend_form()

    @weekend.error
    async def on_error(self, exception):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['serverId'])
        await channel.send(f"Weekend initiate error:\n```py\n{traceback.format_exc()[:800]}```\nPlease re-start.")
        await self.logger.on_automation_event("Weekend", "error found")

        self.weekend.restart()

    @app_commands.command(name="weekly_simulate", description="Simulate a weekly crawl cycle.")
    @app_commands.checks.has_permissions(administrator=True)
    async def _weekly_simulate(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        await self.weekly()
        await interaction.followup.send(f"{Assets.green_tick} **Weekly Task finished**")

    @app_commands.command(name="gen_weekly_member", description="Simulate a weekly crawl cycle.")
    @app_commands.checks.has_permissions(administrator=True)
    async def _gen_mem(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        await self.weekend()
        await interaction.followup.send(f"{Assets.green_tick} **Weekly Task 2 finished**")


async def setup(client):
    await client.add_cog(WeeklyAutomation(client), guilds=[discord.Object(id=client.config['serverId'])])
