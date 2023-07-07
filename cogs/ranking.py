import discord
from discord import app_commands
from discord.ext import commands
import datetime
from utils.asset import Assets

duration_type_list = ['current_month', 'all_time']
duration_frontend_list = [f"{datetime.datetime.now().strftime('%B')}'s", "All-time"]
rank_type_list = ['score', 'current_daily_streak']
rank_frontend_list = ['score', 'current streak']
color_list = [Assets.easy, Assets.hard]
medal_list = ["🥇", "🥈", "🥉"]

def get_discord_username(interaction, discord_id: int):
    member = discord.utils.find(lambda m: m.id == discord_id, interaction.guild.members)
    if member: 
        return member.name 
    else:
        return None
   
def purify_members(interaction, lc_users: list, duration_type: int, rank_type: int):
    res_list = []
    for user in lc_users:
        username = get_discord_username(interaction, user['discord_id'])
        if username:
            res_list.append({
                "lc_username": user['lc_username'],
                "discord_username": username,
                "link": f"https://leetcode.com/{user['lc_username']}",
                "value": user[duration_type_list[duration_type]][rank_type_list[rank_type]],  
            })
    return res_list
    
def get_ranking_embed(interaction, DBClient, duration_type: int, rank_type: int, page_number: int):
    lc_col = DBClient['LC_db']['LC_users']
    lc_users = list(lc_col.find())

    # Removes members that have already left
    user_list = purify_members(
        interaction = interaction, 
        lc_users = lc_users, 
        duration_type = duration_type,
        rank_type = rank_type
    ) 
    user_list.sort(key = lambda x: -x['value'])
    response = ""
    idx = 1
    for user in user_list:
        rank_idx = medal_list[idx - 1]  if idx < 4 else f"``#{idx}``"
        response += f"{rank_idx} [``{user['lc_username']}``]({user['link']} '{user['discord_username']}'): {user['value']}\n"
        idx += 1
        
        if idx > 10: break

    embed = discord.Embed(
        title = f"{duration_frontend_list[duration_type]} {rank_frontend_list[rank_type]} ranking",
        description = response,
        color = color_list[rank_type]
    )
        
    embed.set_thumbnail(
        url = interaction.guild.icon.url
    )
    embed.set_footer(text = "Hover for Discord usernames • Page 1/5")
    return embed

class DurationDropdown(discord.ui.Select):
    def __init__(self, DBclient):
        options = [
            discord.SelectOption(label='Current month', value = "0", description="Current month's leaderboard", emoji='📅', default=True),
            discord.SelectOption(label='All time', value = "1", description="All time's leaderboard", emoji='🗓️'),
        ]
        self.DBclient = DBclient
        super().__init__(min_values = 1, max_values = 1, options = options)

    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        chosen_idx = int(self.values[0])
        self.options[chosen_idx].default = True
        self.options[1 - chosen_idx].default = False
        self.view.duration_type = chosen_idx
    
        await interaction.edit_original_response(
            embed = get_ranking_embed(
                interaction = interaction,
                DBClient = self.DBclient,
                duration_type = self.view.duration_type,
                rank_type = self.view.rank_type,
                page_number = self.view.page_number
            ), 
            view = self.view
        )
    
class RankDropdown(discord.ui.Select):
    def __init__(self, DBclient):
        options = [
            discord.SelectOption(label='Score', value = "0", description="Score leaderboard", emoji='🏆', default=True),
            discord.SelectOption(label='Current streak', value = "1", description="Current streak leaderboard", emoji='🏅'),
        ]
        self.DBclient = DBclient
        super().__init__(min_values = 1, max_values = 1, options = options)

    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        chosen_idx = int(self.values[0])
        self.options[chosen_idx].default = True
        self.options[1 - chosen_idx].default = False
        self.view.rank_type = chosen_idx
    
        await interaction.edit_original_response(
            embed = get_ranking_embed(
                interaction = interaction,
                DBClient = self.DBclient,
                duration_type = self.view.duration_type,
                rank_type = self.view.rank_type,
                page_number = self.view.page_number
            ), 
            view = self.view
        )
        

class DropdownView(discord.ui.View):
    def __init__(self, DBclient):
        super().__init__(timeout = 120)
        self.DBclient = DBclient
        self.rank_type = 0
        self.duration_type = 0
        self.page_number = 1
        self.add_item(DurationDropdown(DBclient))
        self.add_item(RankDropdown(DBclient))

class ranking(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = "rank")
    async def _rank(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)

        # Update current month name
        global duration_frontend_list
        duration_frontend_list = [f"{datetime.datetime.now().strftime('%B')}'s", "All-time"]

        view = DropdownView(self.client.DBClient)
        await interaction.followup.send(
            embed = get_ranking_embed(
                interaction = interaction, 
                DBClient = self.client.DBClient, 
                duration_type = 0,
                rank_type = 0,
                page_number = 1
            ),
            view = view
        )

    
async def setup(client):
    await client.add_cog(ranking(client), guilds=[discord.Object(id=1085444549125611530)])
    #await client.add_cog(lc(client))
