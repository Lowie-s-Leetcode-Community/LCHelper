import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets

OPERATING_MODEL_MSG = """
Lowie’s Leetcode Club là CLB hoạt động theo mô hình Study group (nhóm học tập). CLB hoạt động phi lợi nhuận, và mở cho bất kỳ ai nhiệt tình tham gia, học hỏi, trao đổi. Trước mắt, CLB không chịu sự quản lý của VNU hay bất kỳ tổ chức hay cơ quan quản lý nào. CLB có hoạt động hàng tuần, có ban điều hành, và có các sự kiện, lớp tập huấn, luyện tập interview hàng tuần/cách tuần/hàng tháng.
"""
CLUB_ACTIVITY_MSG_1 = """
Leetcode có một “bài toán của ngày” (gọi là Daily), thường ở mức độ Medium. 99.99% trong CLB sẽ có ít nhất 1 người giải được.

Tất cả mọi người đều có thể đăng ký, hoặc được assign để chữa bài một ngày nào đó. Đơn đăng ký chữa bài của tuần X sẽ được mở vào thứ Ba của tuần (X - 1), và chốt danh sách vào thứ Bảy cùng tuần. Các thành viên được assign sẽ có trách nhiệm code AC bài ngày hôm đó, và diễn giải bằng lời cách làm để cho các thành viên trong CLB có thể hiểu được.
"""
CLUB_ACTIVITY_MSG_2 = """
CLB tổ chức Mock Whiteboard Interview hàng tuần/cách tuần. Các bạn sẽ được training trong một bài phỏng vấn thực tế, học cách diễn giải, trao đổi ý tưởng của mình với người phỏng vấn.

Các buổi mock sẽ được thực hiện online hoặc offline, tùy vào điều kiện thực tế. Độ khó các bài sẽ khó hơn bài Daily, yêu cầu các bạn sẽ phải nghĩ nhiều hơn, và làm tốt việc diễn giải ý tưởng một cách chau chuốt nhất.
"""
CLUB_ACTIVITY_MSG_3 = """
Dựa vào nhu cầu của các thành viên trong CLB, Core team sẽ tổ chức các buổi dạy về Giải thuật. Các bạn sẽ được học lý thuyết, thực hành, và lắng nghe một số mẹo nhỏ để có thể dễ dàng vượt qua những bài toán đó nếu như có được gặp lại.

Các cán bộ trong CLB sẽ lắng nghe ý kiến của các bạn và theo dõi nhu cầu trên Discord. Nên càng hỏi nhiều, càng bàn tán nhiều trên đó, các bạn sẽ nhận lại được càng nhiều sự hỗ trợ. Ngoài ra, sẽ có form để lấy ý kiến, cũng như đề nghị lecture để các bạn đăng ký chủ đề.
"""
CLUB_ACTIVITY_MSG_4 = """
Đã có một số bạn đề xuất với anh Lowie rằng muốn viết blog để chia sẻ kiến thức về một chủ đề, hay một kinh nghiệm phỏng vấn nào đó. Lowie hoàn toàn hoan nghệnh.

Những bài viết với ý tưởng hay sẽ được các thành viên ban Chuyên Môn kiểm duyệt và sẽ được up vào blog nội bộ, cũng như kho tài liệu chung của CLB. Nếu lượng bài viết đủ nhiều, đủ cuốn hút, CLB chúng ta sẽ thành lập page facebook + làm web blog công khai.
"""
CLUB_CORE_TEAM_MSG_1 = """
Trên tinh thần đam mê, hiếu học, tự do trong nghiên cứu, trao đổi: bất kỳ thành viên nào cũng có thể tham gia LLC để củng cố và nâng cao kỹ năng làm coding interview của mình.

Khi tham gia vào CLB, các bạn có trách nhiệm tham gia vào các hoạt động hàng ngày, hàng tuần cùng các hội viên khác. Cho đến ngày các bạn rời khỏi CLB, hoặc bị kick ra khỏi UET (cùng cái bằng), các bạn sẽ phải cảm thấy kỹ năng của các bạn phải được cải thiện rõ rệt, so với ngày các bạn join vào. CLB sẽ tạo mọi điều kiện trong khả năng để các bạn đạt được điều đó.

Vì thế, để đảm bảo các hoạt động được thông suốt, cần một nhóm core nhiệt tình, có trách nhiệm, và đam mê với CLB. Dưới đây, anh xin công bố các ban trong CLB của mình như sau:
"""
CLUB_CORE_TEAM_MSG_2 = """
Tô Tuấn Dũng - <@318049602160951297>
"""
CLUB_CORE_TEAM_MSG_3 = """
- **Trưởng ban**: Lê Vũ Minh - <@683328026943160464>

Là Admin của các group, owner của repo tài liệu nội bộ, LVM sẽ quản lý các tài nguyên của CLB, và theo dõi tương tác của các bạn tham gia trong CLB. Trong giai đoạn đầu, LVM cùng anh sẽ giúp cho các giao tiếp nội bộ được thông suốt, và mọi người có môi trường tốt để học tập, trao đổi chiêu thức.
"""
CLUB_CORE_TEAM_MSG_4 = """
- **Trưởng ban**: Vũ Quý Đạt - <@888055463059537983>
- **Phó ban**: Tạ Xuân Duy - <@418256822902718465>

Các bạn này đều là các bạn đã có thành tích ở các giải lập trình trong quá khứ. Đây là những đầu mối đáng tin cậy để các bạn tham khảo, và nhận được sự giúp đỡ trong quá trình rèn luyện kỹ năng trong CLB.
"""
CLUB_CORE_TEAM_MSG_5 = """
- **Trưởng ban**: Trần Nam Dân - <@641562953862086657>
- **Phó ban**: Nguyễn Duy Chiến - <@633872635411038209>

Các bạn này sẽ chịu trách nhiệm tổ chức các hoạt động trong CLB: Mock interview, hay tổ chức phòng học. Đây là đầu mối để các bạn nhận thông tin về các sự kiện trong CLB, cũng như nhận ý kiến đóng góp, phản hổi có tính xây dựng để các thành viên trong CLB có trải nghiệm tốt hơn.
"""
HOW_TO_VERIFY_MSG_1 = """
Để tham gia vào các hoạt động CLB, bạn cần phải link tài khoản LeetCode của bạn với bot của server.

⚠️ Lưu ý, sau 7 ngày kể từ khi gia nhập mà bạn chưa link tài khoản, bạn sẽ tự động bị kick khỏi server. Hãy làm ngay và luôn để tránh bỏ lỡ những điều hay ho ✨
"""
HOW_TO_VERIFY_MSG_2 = """
Đăng nhâp vào tài khoản LeetCode của bạn và vào phần profile.
"""
HOW_TO_VERIFY_MSG_3 = """
Sau khi vào phần profile, bạn hãy nhìn lên cái đường dẫn URL của leetcode. Username ID của bạn sẽ là phần của đường link. Copy cái user ID đó.
"""
HOW_TO_VERIFY_MSG_4 = """
Trong kênh chat <#1090084731560927274>, bạn hãy gõ lệnh </link:1113100702886141993>  của <@738713416914567198>. Paste cái mã user ID của bạn vào tham số username.

Con bot sẽ generate ra một chuỗi kí tự dài 5 chữ. Bạn hãy copy chuỗi kí tự này và thực hiện các bước tiếp theo trong vòng 120 giây.
"""
HOW_TO_VERIFY_MSG_5 = """
Quay trở lại LeetCode, vào `Edit Profile`. Duới mục **Summary**, vào edit và paste cái mã 5 chữ đó vào rồi ấn `Save`.
"""
HOW_TO_VERIFY_MSG_6 = """
Quay trở lại Discord, bấm nút `Verify Me!` trên dòng tin nhắn của con bot. 

Nếu bạn làm các bước trên chính xác, thì bot sẽ báo thành công và bạn sẽ được nhận role <@&1087761988068855890>, chính thức xác nhận bạn là thành viên CLB 🎉🎉🎉.
"""

class gl(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = "gl-init", description = "Sends initial embeds for info channels")
    @app_commands.checks.has_permissions(administrator = True)
    async def _gl_init(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)

        # Embeds in #giới-thiệu-clb
        embed1 = discord.Embed(
            title = "🏭 Mô hình hoat động",
            description = OPERATING_MODEL_MSG,
            color = discord.Color.red()
        )
        
        embed1.set_thumbnail(
            url = interaction.guild.icon.url
        )

        embed2 = discord.Embed(
            title = "🏃 Các hoạt động trong CLB",
            color = discord.Color.blue()
        )
        embed2.add_field(
            name = "1️⃣ Chữa Daily",
            value = CLUB_ACTIVITY_MSG_1,
            inline = False
        )
        embed2.add_field(
            name = "2️⃣ Mock Whiteboard Interview",
            value = CLUB_ACTIVITY_MSG_2,
            inline = False
        )
        embed2.add_field(
            name = "3️⃣ Algorithm Lecture",
            value = CLUB_ACTIVITY_MSG_3,
            inline = False
        )
        embed2.add_field(
            name = "4️⃣ Viết Blog",
            value = CLUB_ACTIVITY_MSG_4,
            inline = False
        )

        embed3 = discord.Embed(
            title = "🧑‍🏭 Nhân sự CLB",
            description = CLUB_CORE_TEAM_MSG_1,
            color = discord.Color.green()
        )
        embed3.add_field(
            name = "1️⃣ Chủ tịch - Club owner",
            value = CLUB_CORE_TEAM_MSG_2,
            inline = False
        )
        embed3.add_field(
            name = "2️⃣ Ban Admin",
            value = CLUB_CORE_TEAM_MSG_3,
            inline = False
        )
        embed3.add_field(
            name = "3️⃣ Ban Chuyên Môn",
            value = CLUB_CORE_TEAM_MSG_4,
            inline = False
        )
        embed3.add_field(
            name = "4️⃣ Ban Sự Kiện",
            value = CLUB_CORE_TEAM_MSG_5,
            inline = False
        )
        channel = await interaction.guild.fetch_channel(1139158245391474800)
        await channel.send(embeds = [embed1, embed2, embed3])

        # Embeds in #hướng-dẫn-verify
        embed4 = discord.Embed(
            title = "📜 Hướng dẫn verify",
            description = HOW_TO_VERIFY_MSG_1,
            color = discord.Color.gold()
        )

        embed5 = discord.Embed(
            description = HOW_TO_VERIFY_MSG_2,
            color = 0xcdb4db
        )
        embed5.set_author(
            name = "Bước 1"
        )
        embed5.set_image(
            url = "https://media.discordapp.net/attachments/1092451759890374747/1092452461748424784/image.png"
        )

        embed6 = discord.Embed(
            description = HOW_TO_VERIFY_MSG_3,
            color = 0xffc8dd
        )
        embed6.set_author(
            name = "Bước 2"
        )
        embed6.set_image(
            url = "https://cdn.discordapp.com/attachments/1092451759890374747/1092453040465903616/image.png"
        )

        embed7 = discord.Embed(
            description = HOW_TO_VERIFY_MSG_4,
            color = 0xffafcc,
        )
        embed7.set_author(
            name = "Bước 3"
        )
        embed7.set_image(
            url = "https://cdn.discordapp.com/attachments/1092451759890374747/1092453850121777243/image.png"
        )

        embed8 = discord.Embed(
            description = HOW_TO_VERIFY_MSG_5,
            color = 0xbde0fe
        )
        embed8.set_author(
            name = "Bước 4"
        )
        embed8.set_image(
            url = "https://cdn.discordapp.com/attachments/1092451759890374747/1092454978926419988/image.png"
        )
        
        embed9 = discord.Embed(
            description = HOW_TO_VERIFY_MSG_6,
            color = 0xa2d2ff
        )
        embed9.set_author(
            name = "Bước 5"
        )
        embed9.set_image(
            url = "https://cdn.discordapp.com/attachments/1092451759890374747/1092455415150809158/image.png"
        )
        
        channel = await interaction.guild.fetch_channel(1139158370926993499)
        await channel.send(embeds = [embed4, embed5, embed6, embed7, embed8, embed9])
        await interaction.followup.send(f"{Assets.green_tick} **All embeds sent**")

    
async def setup(client):
    await client.add_cog(gl(client), guilds=[discord.Object(id=1085444549125611530)])
    #await client.add_cog(gl(client))
