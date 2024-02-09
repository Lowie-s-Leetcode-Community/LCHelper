import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets

class SetLogging(commands.Cog):
    def __init__(self, client):
        self.client = client

    logging_group = app_commands.Group(name = "set_logging", description = "Logging Group")
    @logging_group.command(name = 'submission', description = "Sets a channel to track recent AC submissions")
    @app_commands.describe(channel = "Choose a channel")
    @app_commands.checks.has_permissions(administrator = True)
    async def _logging_submission(self, interaction: discord.Interaction, channel: discord.channel.TextChannel):
        await interaction.response.defer(thinking = True)

        lc_db = self.client.DBClient['LC_db']
        lc_col = lc_db['LC_config']
        lc_query = {}
        lc_result = lc_col.find_one(lc_query)
        if lc_result:
            lc_update = {'$set': {'tracking_channel_id': channel.id}}
            lc_col.update_one(lc_query, lc_update)
        else:
            lc_col.insert_one({'server_id': interaction.guild_id, 'tracking_channel_id': channel.id})
        await interaction.followup.send(f"{Assets.green_tick} **Tracking channel has been set to {channel.mention}**")

    @logging_group.command(name = 'score', description = "Sets a channel to track score updates")
    @app_commands.describe(channel = "Choose a channel")
    @app_commands.checks.has_permissions(administrator = True)
    async def _logging_score(self, interaction: discord.Interaction, channel: discord.channel.TextChannel):
        await interaction.response.defer(thinking = True)

        lc_db = self.client.DBClient['LC_db']
        lc_col = lc_db['LC_config']
        lc_query = {}
        lc_result = lc_col.find_one(lc_query)
        if lc_result:
            lc_update = {'$set': {'score_log_channel_id': channel.id}}
            lc_col.update_one(lc_query, lc_update)
        else:
            lc_col.insert_one({'server_id': interaction.guild_id, 'score_log_channel_id': channel.id})
        await interaction.followup.send(f"{Assets.green_tick} **Score updates channel has been set to {channel.mention}**")

async def setup(client):
    await client.add_cog(SetLogging(client), guilds=[discord.Object(id=client.config['serverId'])])
