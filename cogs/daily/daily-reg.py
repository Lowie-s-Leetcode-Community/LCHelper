import discord
from discord import app_commands
from discord.ext import commands
import datetime
import textwrap
from typing import Optional

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: 
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def get_next_LLC_week_and_month():
    d = datetime.date.today()
    next_mon = next_weekday(d, 0)
    week_no = int((next_mon.day - 1) / 7) + 1
    month_no = next_mon.month

    return week_no, month_no

def get_registration_announce_msg(message):
    d = datetime.date.today()
    weekdays = []
    next_mon = next_weekday(d, 0)
    weekdays.append(next_mon)
    for i in range(6):
        weekdays.append(next_mon + datetime.timedelta(days = i + 1))
    # next_mon = next_weekday(d, 0)
    # next_tue = next_mon + datetime.timedelta(days=1)
    # next_wed = next_mon + datetime.timedelta(days=2)
    # next_thu = next_mon + datetime.timedelta(days=3)
    # next_fri = next_mon + datetime.timedelta(days=4)
    # next_sat = next_mon + datetime.timedelta(days=5)
    # next_sun = next_mon + datetime.timedelta(days=6)

    reg_msg = f"""
    Xin chào buổi tối, các thành viên LLC <@&1087761988068855890>,
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
    
    return textwrap.dedent(reg_msg)

class daily_reg(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'start_daily_reg', description = "Khởi tạo một thread đăng ký Chữa Daily của tuần tiếp theo")
    @app_commands.describe(message = "Tin nhắn kèm theo thread đăng ký")
    @app_commands.checks.has_permissions(administrator = True)
    async def _start_daily_reg(self, interaction: discord.Interaction, message: Optional[str] = None):
        if message == None:
            week, month = get_next_LLC_week_and_month()
            message = f"Form đăng ký chữa Daily tuần {week} tháng {month} đã chính thức mở. Mọi người đăng ký nhiệt tình nhé. Chúc các bạn một tuần giải thuật vui vẻ."

        msg = get_registration_announce_msg(message)
        await interaction.response.send_message(content = msg, allowed_mentions = discord.AllowedMentions(roles=True))
        reg_mes = await interaction.original_response()
        await reg_mes.add_reaction("2️⃣")
        await reg_mes.add_reaction("3️⃣")
        await reg_mes.add_reaction("4️⃣")
        await reg_mes.add_reaction("5️⃣")
        await reg_mes.add_reaction("6️⃣")
        await reg_mes.add_reaction("7️⃣")
        await reg_mes.add_reaction("8️⃣")
        

async def setup(client):
    await client.add_cog(daily_reg(client), guilds=[discord.Object(id=1085444549125611530)])