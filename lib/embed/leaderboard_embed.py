import discord
import sys
from discord import app_commands
from discord.ext import commands
import datetime
import typing
from utils.asset import Assets
import traceback
import aiohttp
import json

color_list = [Assets.easy, Assets.medium, Assets.hard]
medal_list = ["🥇", "🥈", "🥉"]

class LeaderboardEmbed(discord.Embed):
    def __init__(self, title: str, user_list: list, page_number: int, pages_count: int, embed_limit: int, interaction: discord.Interaction):
        super().__init__(
            title=title,
            color=color_list[0]
        )
        self.user_list = user_list
        self.page_number = page_number
        self.pages_count = pages_count
        self.embed_limit = embed_limit
        self.interaction = interaction
        self.get_ranking_embed()

    def get_discord_username(self, discord_id: str):
        member = discord.utils.find(lambda m: str(m.id) == discord_id, self.interaction.guild.members)
        if member:
            return member.name
        else:
            return None
        
    def get_index(self, expected_discord_username: str):
        idx = 1
        for user in self.user_list:
            if user['discordId'] == expected_discord_username:
                return idx
            idx += 1
        return 1

    def get_ranking_embed(self):
        # The embed description content
        def format_display_string(user, idx):
            rank_idx = medal_list[idx - 1] if idx <= len(medal_list) else f"``#{idx}``"
            discord_username = self.get_discord_username(user['discordId'])
            leetcode_url = f"https://leetcode.com/{user['leetcodeUsername']}"
            return f"{rank_idx} [``{user['leetcodeUsername']}``]({leetcode_url} '{discord_username}'): {user['scoreEarned']}\n"
        response = ""
        for idx in range(self.embed_limit * (self.page_number - 1) + 1, min(self.embed_limit * self.page_number, len(self.user_list)) + 1):
            user = self.user_list[idx - 1]
            response += format_display_string(user, idx)

        response += "---\n"

        # interaction author's ranking
        caller_ranking = self.get_index(expected_discord_username = str(self.interaction.user.id))
        response += format_display_string(self.user_list[caller_ranking - 1], caller_ranking)

        self.description = response  
        self.set_thumbnail(
            url = self.interaction.guild.icon.url
        )
        self.set_footer(text = f"Hover on each user for their Discord username • Page {self.page_number}/{self.pages_count}")
        return self

class NavModal(discord.ui.Modal):
    def __init__(self, inherited_view = discord.ui.View): 
        super().__init__(title = "")
        self.view = inherited_view
        self.nav_response = discord.ui.TextInput(
            label = f"Enter page number",
            placeholder = f"Number must be between 1 - {self.view.pages_count}",
            required = True
        )
        self.add_item(self.nav_response)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = False)

class NavButton(discord.ui.Button['RankingView']):
    def __init__(self, button_type: int, style: discord.ButtonStyle, is_disabled: bool = False, emoji: typing.Union[str, discord.Emoji, discord.PartialEmoji, None] = None, label: str = None):
        super().__init__(style = style, label = label, disabled = is_disabled, emoji = emoji)
        self.button_type = button_type
    
    async def callback(self, interaction: discord.Interaction):
        if self.button_type == 2:
            modal = NavModal(self.view)
            await interaction.response.send_modal(modal)
            await modal.wait()
            new_page_number = int(modal.nav_response.value)
            if new_page_number >= 1 and new_page_number <= self.view.pages_count:
                self.view.current_page_number = new_page_number
        else:
            await interaction.response.defer(thinking = False)
        
        if self.button_type == 0: self.view.current_page_number = 1
        if self.button_type == 1: self.view.current_page_number = max(1, self.view.current_page_number - 1)
        if self.button_type == 3: self.view.current_page_number = min(self.view.pages_count, self.view.current_page_number + 1)
        if self.button_type == 4: self.view.current_page_number = self.view.pages_count

        self.view.adjust_buttons()

        embed = LeaderboardEmbed(self.view.title, self.view.user_list, self.view.current_page_number, self.view.pages_count, self.view.embed_limit, interaction)
        await interaction.edit_original_response(embed=embed.get_ranking_embed(), view=self.view)

class RankingView(discord.ui.View):
    # Type hinting for IDE
    children: typing.List[typing.Union[NavButton]]

    def __init__(self, title: str, user_list: list, pages_count: int, embed_limit: int):
        super().__init__(timeout = 120)
        self.title = title
        self.user_list = user_list
        self.current_page_number = 1
        self.pages_count = pages_count
        self.embed_limit = embed_limit
        self.response = None
        last_page = (pages_count == 1)
        self.add_item(NavButton(button_type = 0, style = discord.ButtonStyle.gray, emoji = "⏮️", is_disabled = True)) 
        self.add_item(NavButton(button_type = 1, style = discord.ButtonStyle.gray, emoji = "◀️", is_disabled = True))
        self.add_item(NavButton(button_type = 2, style = discord.ButtonStyle.gray if last_page else discord.ButtonStyle.green, label = "1", is_disabled = False))
        self.add_item(NavButton(button_type = 3, style = discord.ButtonStyle.gray if last_page else discord.ButtonStyle.blurple, emoji = "▶️", is_disabled = (pages_count == 1)))
        self.add_item(NavButton(button_type = 4, style = discord.ButtonStyle.gray if last_page else discord.ButtonStyle.blurple, emoji = "⏭", is_disabled = (pages_count == 1)))

    def toggle_disable_button(self, ids, state):
        for id in ids:
            self.children[id].disabled = state
            if (state):
                self.children[id].style = discord.ButtonStyle.gray
            else:
                self.children[id].style = discord.ButtonStyle.blurple

    def adjust_buttons(self):
        if self.current_page_number == 1:
            self.toggle_disable_button([0, 1], True)
        else:
            self.toggle_disable_button([0, 1], False)

        if self.current_page_number == self.pages_count:
            self.toggle_disable_button([3, 4], True)
        else:
            self.toggle_disable_button([3, 4], False)

        self.children[2].label = self.current_page_number
        
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.response.edit(view = self)
        
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        await interaction.followup.send(f"{item} - {error}")