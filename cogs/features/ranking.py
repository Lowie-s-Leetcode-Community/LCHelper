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

duration_type_list = ['current_month', 'all_time']
duration_frontend_list = [f"{datetime.datetime.now().strftime('%B')}'s", "All-time"]
rank_type_list = ['score', 'current_daily_streak', 'max_daily_streak']
rank_frontend_list = ['score', 'current streak', 'max streak']
color_list = [Assets.easy, Assets.medium, Assets.hard]
medal_list = ["🥇", "🥈", "🥉"]

def get_discord_username(interaction, discord_id: int):
    member = discord.utils.find(lambda m: m.id == discord_id, interaction.guild.members)
    if member: 
        return member.name 
    else:
        return None
   
def purify_members(interaction, lc_users: list):
    res_list = []
    for user in lc_users:
        username = get_discord_username(interaction, user['discord_id'])
        if username:
            value_list = []
            for duration_type in range(2):
                value_list.append([])
                for rank_type in range(3):
                    value_list[duration_type].append(user[duration_type_list[duration_type]][rank_type_list[rank_type]])

            res_list.append({
                "lc_username": user['lc_username'],
                "discord_username": username,
                "link": f"https://leetcode.com/{user['lc_username']}",
                "value": value_list,  
            })
    return res_list

def get_user_list(interaction, DBClient, lc_users = None):
    if lc_users == None:
        lc_col = DBClient['LC_db']['LC_users']
        lc_users = list(lc_col.find())

    # Removes members that have already left and sorts
    user_list = purify_members(
        interaction = interaction, 
        lc_users = lc_users
    ) 

    return user_list

def get_index(user_list: list, expected_discord_username: str):
    idx = 1
    for user in user_list:
        if user['discord_username'] == expected_discord_username:
            return idx
        idx += 1

    return None

def get_ranking_embed(interaction, user_list, duration_type: int, rank_type: int, page_number: int, page_number_limit: int, embed_limit: int):
    # Removes members that have already left and sorts
    user_list.sort(key = lambda x: -x['value'][duration_type][rank_type])

    # The embed disscription content
    response = ""
    for idx in range(embed_limit * (page_number - 1) + 1, min(embed_limit * page_number, len(user_list)) + 1):
        user = user_list[idx - 1]
        rank_idx = medal_list[idx - 1] if idx < 4 else f"``#{idx}``"
        response += f"{rank_idx} [``{user['lc_username']}``]({user['link']} '{user['discord_username']}'): {user['value'][duration_type][rank_type]}\n"

    response += "---\n"

    # interaction author's ranking
    interaction_author_ranking = get_index(user_list = user_list, expected_discord_username = interaction.user.name)
    rank_idx = medal_list[interaction_author_ranking - 1] if interaction_author_ranking < 4 else f"``#{interaction_author_ranking}``"
    response += f"{rank_idx} [``{user_list[interaction_author_ranking - 1]['lc_username']}``]({user_list[interaction_author_ranking - 1]['link']} '{user_list[interaction_author_ranking - 1]['discord_username']}'): {user_list[interaction_author_ranking - 1]['value'][duration_type][rank_type]}"

    embed = discord.Embed(
        title = f"{duration_frontend_list[duration_type]} {rank_frontend_list[rank_type]} ranking",
        description = response,
        color = color_list[rank_type]
    )
        
    embed.set_thumbnail(
        url = interaction.guild.icon.url
    )
    embed.set_footer(text = f"Hover for Discord usernames • Page {page_number}/{page_number_limit}")
    return embed

class DurationDropdown(discord.ui.Select['RankingView']):
    def __init__(self):
        options = [
            discord.SelectOption(label='Current month', value = "0", description="Current month's leaderboard", emoji='📅', default=True),
            discord.SelectOption(label='All time', value = "1", description="All time's leaderboard", emoji='🗓️'),
        ]
        super().__init__(min_values = 1, max_values = 1, options = options)

    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        chosen_idx = int(self.values[0])
        self.options[chosen_idx].default = True
        self.options[1 - chosen_idx].default = False

        self.view.duration_type = chosen_idx
        self.view.current_page_number = 1
        self.view.adjust_buttons()

        await interaction.edit_original_response(
            embed = get_ranking_embed(
                interaction = interaction,
                user_list = self.view.user_list,
                duration_type = self.view.duration_type,
                rank_type = self.view.rank_type,
                page_number = 1,
                page_number_limit = self.view.page_number_limit,
                embed_limit = self.view.embed_limit
            ), 
            view = self.view
        )
    
class RankDropdown(discord.ui.Select['RankingView']):
    def __init__(self):
        options = [
            discord.SelectOption(label='Score', value = "0", description="Score leaderboard", emoji='🏆', default=True),
            discord.SelectOption(label='Current streak', value = "1", description="Current streak leaderboard", emoji='🏅'),
            discord.SelectOption(label="Max streak", value = "2", description="Max streak leaderboard", emoji='🎖️')
        ]
        super().__init__(min_values = 1, max_values = 1, options = options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        chosen_idx = int(self.values[0])
        for i in range(0, 3):
            self.options[i].default = False
        self.options[chosen_idx].default = True

        self.view.rank_type = chosen_idx
        self.view.current_page_number = 1
        self.view.adjust_buttons()

        await interaction.edit_original_response(
            embed = get_ranking_embed(
                interaction = interaction,
                user_list = self.view.user_list,
                duration_type = self.view.duration_type,
                rank_type = self.view.rank_type,
                page_number = 1,
                page_number_limit = self.view.page_number_limit,
                embed_limit = self.view.embed_limit
            ), 
            view = self.view
        )

class NavModal(discord.ui.Modal):
    def __init__(self, inherited_view = discord.ui.View): 
        super().__init__(title = "")
        self.view = inherited_view
        self.nav_response = discord.ui.TextInput(
            label = f"Enter page number",
            placeholder = f"Number must be between 1 - {self.view.page_number_limit}",
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
            if new_page_number >= 1 and new_page_number <= self.view.page_number_limit:
                self.view.current_page_number = new_page_number
        else:
            await interaction.response.defer(thinking = False)
        
        if self.button_type == 0: self.view.current_page_number = 1
        if self.button_type == 1: self.view.current_page_number = max(1, self.view.current_page_number - 1)
        if self.button_type == 3: self.view.current_page_number = min(self.view.page_number_limit, self.view.current_page_number + 1)
        if self.button_type == 4: self.view.current_page_number = self.view.page_number_limit

        self.view.adjust_buttons()

        await interaction.edit_original_response(
            embed = get_ranking_embed(
                interaction = interaction,
                user_list = self.view.user_list,
                duration_type = self.view.duration_type,
                rank_type = self.view.rank_type,
                page_number = self.view.current_page_number,
                page_number_limit = self.view.page_number_limit,
                embed_limit = self.view.embed_limit
            ), 
            view = self.view
        )
    

class RankingView(discord.ui.View):
    # Type hinting for IDE
    children: typing.List[typing.Union[RankDropdown, DurationDropdown, NavButton]]

    def __init__(self, user_list: list, page_number_limit: int, embed_limit: int):
        super().__init__(timeout = 120)
        self.user_list = user_list
        self.rank_type = 0
        self.duration_type = 0
        self.current_page_number = 1
        self.page_number_limit = page_number_limit
        self.embed_limit = embed_limit
        self.response = None
        last_page = (page_number_limit == 1)
        self.add_item(NavButton(button_type = 0, style = discord.ButtonStyle.gray, emoji = "⏮️", is_disabled = True))
        self.add_item(NavButton(button_type = 1, style = discord.ButtonStyle.gray, emoji = "◀️", is_disabled = True))
        self.add_item(NavButton(button_type = 2, style = discord.ButtonStyle.gray if last_page else discord.ButtonStyle.green, label = "1", is_disabled = False))
        self.add_item(NavButton(button_type = 3, style = discord.ButtonStyle.gray if last_page else discord.ButtonStyle.blurple, emoji = "▶️", is_disabled = (page_number_limit == 1)))
        self.add_item(NavButton(button_type = 4, style = discord.ButtonStyle.gray if last_page else discord.ButtonStyle.blurple, emoji = "⏭", is_disabled = (page_number_limit == 1)))
        self.add_item(DurationDropdown())
        self.add_item(RankDropdown())

    def toggle_disable_button(ids, state):
        for id in ids:
            self.children[id].disabled = state
            if (state):
                self.children[id].style = discord.ButtonStyle.gray
            else:
                self.children[id].style = discord.ButtonStyle.blurple

    def adjust_buttons(self):
        if self.current_page_number == 1:
            # self.children[0].disabled = True
            # self.children[0].style = discord.ButtonStyle.gray
            # self.children[1].disabled = True
            # self.children[1].style = discord.ButtonStyle.gray
            self.toggle_disable_button([0, 1], True)
        else:
            # self.children[0].disabled = False
            # self.children[0].style = discord.ButtonStyle.blurple
            # self.children[1].disabled = False
            # self.children[1].style = discord.ButtonStyle.blurple
            self.toggle_disable_button([0, 1], False)

        if self.current_page_number == self.page_number_limit:
            # self.children[3].disabled = True
            # self.children[3].style = discord.ButtonStyle.gray
            # self.children[4].disabled = True
            # self.children[4].style = discord.ButtonStyle.gray
            self.toggle_disable_button([3, 4], True)
        else:
            # self.children[3].disabled = False
            # self.children[3].style = discord.ButtonStyle.blurple
            # self.children[4].disabled = False
            # self.children[4].style = discord.ButtonStyle.blurple
            self.toggle_disable_button([3, 4], False)

        self.children[2].label = self.current_page_number
        
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.response.edit(view = self)
        
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        await interaction.followup.send(f"{item} - {error}")
    

class ranking(commands.Cog):
    def __init__(self, client):
        self.client = client

    rank_group = app_commands.Group(name = "rank", description = "Ranking Group")
    @rank_group.command(name = "view", description = "Take a look at LLC's Hall of Fame")
    async def _rank_view(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        
        # Update current month name
        global duration_frontend_list
        duration_frontend_list = [f"{datetime.datetime.now().strftime('%B')}'s", "All-time"]
        user_list = get_user_list(interaction = interaction, DBClient = self.client.DBClient)
        embed_limit = 10
        page_number_limit = (len(user_list) + (embed_limit - 1)) // embed_limit
        view = RankingView(user_list, page_number_limit, embed_limit)
        await interaction.followup.send(
            embed = get_ranking_embed(
                interaction = interaction, 
                user_list = user_list,
                duration_type = 0,
                rank_type = 0,
                page_number = 1,
                page_number_limit = page_number_limit,
                embed_limit = embed_limit
            ),
            view = view
        )
        view.response = await interaction.original_response()

    @rank_group.command(name = "backup", description = "View rankings from a backup file")
    async def _rank_backup(self, interaction: discord.Interaction, backup_message_id: str):
        await interaction.response.defer(thinking = True)
        
        backup_message_id = int(backup_message_id)

        lc_query = self.client.DBClient['LC_db']['LC_config'].find_one({})
        backup_channel_id = lc_query['backup_channel_id']
        backup_channel = await interaction.guild.fetch_channel(backup_channel_id)
        backup_message = await backup_channel.fetch_message(backup_message_id)
        backup_attachment_link = backup_message.attachments[0].url

        print(backup_attachment_link)
        async with aiohttp.ClientSession() as cs:
            async with cs.get(backup_attachment_link) as res:
                await res.read()
        
        backup_file = open("backup.json")
        data = json.load(backup_file)
        user_list = data['LC_users']

        # And everything below is (almost) the same as the above command
        global duration_frontend_list
        duration_frontend_list = [f"{datetime.datetime.now().strftime('%B')}'s", "All-time"]
        user_list = get_user_list(interaction = interaction, DBClient = self.client.DBClient, lc_users = user_list)
        embed_limit = 10
        page_number_limit = (len(user_list) + (embed_limit - 1)) // embed_limit
        view = RankingView(user_list, page_number_limit, embed_limit)
        await interaction.followup.send(
            embed = get_ranking_embed(
                interaction = interaction, 
                user_list = user_list,
                duration_type = 0,
                rank_type = 0,
                page_number = 1,
                page_number_limit = page_number_limit,
                embed_limit = embed_limit
            ),
            view = view
        )
        view.response = await interaction.original_response()

    
async def setup(client):
    await client.add_cog(ranking(client), guilds=[discord.Object(id=1085444549125611530)])
    #await client.add_cog(lc(client))
