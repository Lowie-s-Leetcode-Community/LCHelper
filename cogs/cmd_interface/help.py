import discord
from discord import app_commands
from discord.ext import commands


class help_command(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'help', description = "Các câu lệnh của LCHelper")
    async def _help(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        
        embed = discord.Embed(
            color = 0xff822e,
        )
        embed.set_author(
            name = "Những câu lệnh để tương tác với hệ thống LCHelper",
            icon_url = "https://assets.leetcode.com/users/leetcode/avatar_1568224780.png"
        )
        embed.add_field(
            name = "🗃️  Xem thông tin LLC membership",
            value = f"""
            </profile:1206907242784235522>: Các dữ liệu điểm số của thành viên CLB trên hệ thống LLC.
            </task:1206907242784235521>: Các nhiệm vụ để có thể kiếm điểm trong LLC.
            """,
            inline = False
        )
        embed.add_field(
            name = "📊  Xem các bảng xếp hạng",
            value = f"""
            </leaderboard current:1206907242784235526>: Bảng xếp hạng điểm số của các thành viên trong CLB.
            """,
            inline = False
        )
        embed.add_field(
            name = "📝  LeetCode Problems",
            value = f"""
            </daily:1206907242784235525>: Trả về bài Daily trên LeetCode của ngày hôm nay.
            </gimme:1206907242784235528>: Chọn một bài LeetCode ngẫu nhiên trên CSDL của LeetCode. Member có thể chọn độ khó và chủ đề mong muốn qua các tham số, và loại những chủ đề không mong muốn.
            """,
            inline = False
        )
        embed.add_field(
            name = "\u200b",
            value = "[Chi tiết các câu lệnh có thể được xem tại đây](https://lowie-writes.notion.site/LCHelper-Documentation-d85de63f31144bc383136ab9f5804527?pvs=4)",
        )

        await interaction.followup.send(embed = embed)


async def setup(client):
    await client.add_cog(help_command(client), guilds=[discord.Object(id=client.config['serverId'])])