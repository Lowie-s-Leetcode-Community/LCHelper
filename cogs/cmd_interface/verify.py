import random
import string
import traceback

import discord
from discord import app_commands
from discord.ext import commands

from utils.asset import Assets
from utils.lc_utils import LC_utils

ACCOUNT_USED_MSG = "Có vấn đề trong việc xác minh tài khoản. Rất có thể một người khác ở server này đã sử dụng tài khoản này của bạn!"
UNMATCHED_CODE_MSG = "Code chưa đúng. Vui lòng thử lại theo hướng dẫn trên."
INSTRUCTION_MSG = "**Hãy nhập đoạn serie này: `{}` vào mục [profile summary](https://leetcode.com/profile/) của bạn trên Leetcode, sau đó bấm nút 'Xác minh tôi!' bên dưới trong 5 phút tới.**"


class ConfirmView(discord.ui.View):
    def __init__(self, client, code, username, user_id):
        super().__init__(timeout=300)
        self.code = code
        self.client = client
        self.username = username
        self.user_id = user_id
        self.response = None

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
            child.label = "Quá thời gian!"
            child.emoji = "⏰"
        await self.response.edit(view=self)

    @discord.ui.button(label="Xác minh tôi!", style=discord.ButtonStyle.primary)
    async def call_back(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        assert interaction.user.id == self.user_id
        await interaction.response.defer(thinking=True)
        user_info = LC_utils.get_user_profile(self.username)
        if (
            len(user_info["profile"]["summary"]) >= 5
            and user_info["profile"]["summary"][0:5] == self.code
        ):
            user_obj = {
                "discordId": str(interaction.user.id),
                "leetcodeUsername": self.username,
                "mostRecentSubId": -1,
            }

            member = await interaction.guild.fetch_member(interaction.user.id)

            verified_role_id = self.client.config["verifiedRoleId"]
            unverified_role_id = self.client.config["unverifiedRoleId"]
            verified_role = discord.utils.get(
                interaction.guild.roles, id=int(verified_role_id)
            )
            unverified_role = discord.utils.get(
                interaction.guild.roles, id=int(unverified_role_id)
            )
            print(verified_role_id, unverified_role_id, verified_role, unverified_role)
            try:
                await self.client.db_api.create_user(user_obj)
            except Exception:
                await interaction.followup.send(
                    content=f"{Assets.red_tick} **{ACCOUNT_USED_MSG}**"
                )
            else:
                await member.add_roles(verified_role)
                await member.remove_roles(unverified_role)
                await interaction.followup.send(
                    content=f"{Assets.green_tick} **Tài khoản đã được kết nối thành công.**"
                )
        else:
            await interaction.followup.send(
                content=f"{Assets.red_tick} **{UNMATCHED_CODE_MSG}**"
            )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item
    ):
        print(traceback.format_exc())
        await interaction.followup.send(error)


class ReConfirmView(discord.ui.View):
    def __init__(self, client, code, username, user_id):
        super().__init__(timeout=300)
        self.code = code
        self.client = client
        self.username = username
        self.user_id = user_id
        self.response = None

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
            child.label = "Quá thời gian!"
            child.emoji = "⏰"
        await self.response.edit(view=self)

    @discord.ui.button(label="Re-verify now!", style=discord.ButtonStyle.primary)
    async def call_back(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        assert interaction.user.id == self.user_id
        await interaction.response.defer(thinking=True)
        user_info = LC_utils.get_user_profile(self.username)
        if (
            len(user_info["profile"]["summary"]) >= 5
            and user_info["profile"]["summary"][0:5] == self.code
        ):
            user_obj = {
                "discordId": str(interaction.user.id),
                "leetcodeUsername": self.username,
            }

            try:
                await self.client.db_api.update_one(user_obj)
            except Exception:
                await interaction.followup.send(
                    content=f"{Assets.red_tick} **{ACCOUNT_USED_MSG}**"
                )
            else:
                await interaction.followup.send(
                    content=f"{Assets.green_tick} **Tài khoản đã được kết nối lại thành công.**"
                )
        else:
            await interaction.followup.send(
                content=f"{Assets.red_tick} **{UNMATCHED_CODE_MSG}**"
            )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item
    ):
        print(traceback.format_exc())
        await interaction.followup.send(error)


class DeleteOldAccountView(discord.ui.View):
    def __init__(self, client, user_lc_id, user_discord_id):
        super().__init__(timeout=300)
        self.client = client
        self.user_lc_id = user_lc_id
        self.user_discord_id = user_discord_id
        self.response = None

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
            child.label = "Quá thời gian!"
            child.emoji = "⏰"
        await self.response.edit(view=self)

    @discord.ui.button(label="Gỡ liên kết ngay!", style=discord.ButtonStyle.primary)
    async def call_back(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        assert interaction.user.id == self.user_discord_id
        await interaction.response.defer(thinking=True)

        try:
            await self.client.db_api.delete_old_account(self.user_lc_id)
        except Exception:
            await interaction.followup.send(
                content=f"{Assets.red_tick} Có vấn đề xảy ra. Vui lòng thử lại!"
            )
        await interaction.followup.send(
            content=f"{Assets.green_tick} **Gỡ liên kết tài khoản thành công.**\n"
            f"Giờ bạn có thể kết nối tài khoản mới bằng lệnh </link:1206907242784235523>."
        )


class verify(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="link", description="Kết nối tài khoản Leetcode của bạn")
    @app_commands.describe(username="Username của bạn")
    async def _link(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer(thinking=True)
        user_profile = self.client.db_api.read_profile(str(interaction.user.id))
        if user_profile is not None:
            await interaction.followup.send(
                "Bạn đã xác minh tài khoản của mình rồi!\n"
                "Hãy sử dụng `/change_leetcode_username` nếu bạn muốn thay đổi tài khoản Leetcode của mình."
            )
            return

        user_info = LC_utils.get_user_profile(username)
        if user_info:
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
            view = ConfirmView(
                code=code,
                username=username,
                user_id=interaction.user.id,
                client=self.client,
            )
            await interaction.followup.send(INSTRUCTION_MSG.format(code), view=view)
            view.response = await interaction.original_response()
        else:
            await interaction.followup.send(
                f"{Assets.red_tick} **Tài khoản không tồn tại. Vui lòng kiểm tra lại.**\nLưu ý: nếu URL tài khoản của bạn là `https://leetcode.com/u/lowie_/`, thì username bạn cần nhập là `lowie_`."
            )

    @app_commands.command(
        name="change_leetcode_username",
        description="Chỉ sử dụng để xác minh lại sau khi đổi tên tài khoản Leetcode.",
    )
    @app_commands.describe(username="Username Leetcode của bạn")
    async def _change_leetcode_username(
        self, interaction: discord.Interaction, username: str
    ):
        await interaction.response.defer(thinking=True)

        user_profile = self.client.db_api.read_profile(str(interaction.user.id))
        if user_profile is not None:
            await interaction.followup.send(
                "Bạn chưa từng kết nối tài khoản. Hãy sử dụng </link:1206907242784235523> nhé!"
            )
            return

        user_leetcode_old_info = LC_utils.get_user_profile(
            user_profile["leetcodeUsername"]
        )
        if user_leetcode_old_info is not None:
            view = DeleteOldAccountView(
                client=self.client,
                user_lc_id=user_profile["id"],
                user_discord_id=interaction.user.id,
            )
            await interaction.followup.send(
                "Tài khoản Discord của bạn đang được kết nối với một tài khoản khác.\n"
                "Bạn có muốn **GỠ LIÊN KẾT** khỏi tài khoản hiện thời?\n\n"
                ":warning:**Cảnh báo**: hành động này sẽ xóa toàn bộ tiến độ của bạn đã lưu trữ trên cộng đồng, bao gồm điểm số, chuỗi, các lần nộp bài, "
                "và chúng mình không ủng hộ việc các bạn sử dụng nhiều tài khoản. "
                "Chỉ nên sử dụng `/change_leetcode_username` khi bạn đã thay đổi username của mình trên Leetcode.",
                view=view,
            )
            return
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        view = ReConfirmView(
            code=code,
            username=username,
            user_id=interaction.user.id,
            client=self.client,
        )
        await interaction.followup.send(INSTRUCTION_MSG.format(code), view=view)
        return


async def setup(client):
    await client.add_cog(
        verify(client), guilds=[discord.Object(id=client.config["serverId"])]
    )
