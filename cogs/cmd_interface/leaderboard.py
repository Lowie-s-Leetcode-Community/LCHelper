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
from database_api_layer.api import db_api

color_list = [Assets.easy, Assets.medium, Assets.hard]
medal_list = ["🥇", "🥈", "🥉"]

# will recover this feature to get hovering back
def get_discord_username(interaction, discord_id: str):
    member = discord.utils.find(lambda m: str(m.id) == discord_id, interaction.guild.members)
    if member: 
        return member.name 
    else:
        return None

def get_user_list(interaction, DBClient, lc_users = None):
    user_list = db_api.getCurrentMonthLeaderboard()
    return user_list

def get_index(user_list: list, expected_discord_username: str):
    idx = 1
    for user in user_list:
        if user['discordId'] == expected_discord_username:
            return idx
        idx += 1
    return 1

def get_ranking_embed(interaction, user_list, page_number: int, pages_count: int, embed_limit: int):
    # The embed description content
    def format_display_string(user, idx):
        rank_idx = medal_list[idx - 1] if idx <= len(medal_list) else f"``#{idx}``"
        discord_username = get_discord_username(interaction, user['discordId'])
        leetcode_url = f"https://leetcode.com/{user['leetcodeUsername']}"
        return f"{rank_idx} [``{user['leetcodeUsername']}``]({leetcode_url} '{discord_username}'): {user['scoreEarned']}\n"
    response = ""
    for idx in range(embed_limit * (page_number - 1) + 1, min(embed_limit * page_number, len(user_list)) + 1):
        user = user_list[idx - 1]
        response += format_display_string(user, idx)

    response += "---\n"

    # interaction author's ranking
    caller_ranking = get_index(user_list = user_list, expected_discord_username = str(interaction.user.id))
    response += format_display_string(user_list[caller_ranking - 1], caller_ranking)

    embed = discord.Embed(
        title = f"Current month ranking",
        description = response,
        color = color_list[0]
    )
        
    embed.set_thumbnail(
        url = interaction.guild.icon.url
    )
    embed.set_footer(text = f"Hover on each user for their Discord username • Page {page_number}/{pages_count}")
    return embed

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

        await interaction.edit_original_response(
            embed = get_ranking_embed(
                interaction = interaction,
                user_list = self.view.user_list,
                page_number = self.view.current_page_number,
                pages_count = self.view.pages_count,
                embed_limit = self.view.embed_limit
            ), 
            view = self.view
        )

class RankingView(discord.ui.View):
    # Type hinting for IDE
    children: typing.List[typing.Union[NavButton]]

    def __init__(self, user_list: list, pages_count: int, embed_limit: int):
        super().__init__(timeout = 120)
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
    

class Leaderboard(commands.Cog):
    def __init__(self, client):
        self.client = client

    rank_group = app_commands.Group(name = "leaderboard", description = "Ranking Group")
    @rank_group.command(name = "current", description = "Take a look at LLC's Hall of Fame")
    async def _leaderboard_current(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        # Update current month name
        user_list = db_api.getCurrentMonthLeaderboard()
        embed_limit = 10
        pages_count = (len(user_list) + (embed_limit - 1)) // embed_limit
        view = RankingView(user_list, pages_count, embed_limit)
        await interaction.followup.send(
            embed = get_ranking_embed(
                interaction = interaction, 
                user_list = user_list,
                page_number = 1,
                pages_count = pages_count,
                embed_limit = embed_limit
            ),
            view = view
        )
        view.response = await interaction.original_response()
    
    @rank_group.command(name = "previous", description = "Ranking Group")
    async def _leaderboard_previous(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        # Update current month name
        user_list = db_api.getLastMonthLeaderboard()
        embed_limit = 10
        pages_count = (len(user_list) + (embed_limit - 1)) // embed_limit
        view = RankingView(user_list, pages_count, embed_limit)
        await interaction.followup.send(
            embed = get_ranking_embed(
                interaction = interaction, 
                user_list = user_list,
                page_number = 1,
                pages_count = pages_count,
                embed_limit = embed_limit
            ),
            view = view
        )
        view.response = await interaction.original_response()
    # will definitely need a help guide. Also streak count, ...

async def setup(client):
    await client.add_cog(Leaderboard(client), guilds=[discord.Object(id=1085444549125611530)])
