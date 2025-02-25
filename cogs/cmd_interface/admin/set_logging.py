import discord
from discord import app_commands
from discord.ext import commands

from utils.asset import Assets


class SetLogging(commands.Cog):
    def __init__(self, client):
        self.client = client

    logging_group = app_commands.Group(name="set_logging", description="Logging Group")

    @logging_group.command(
        name="submission", description="Sets a channel to track recent AC submissions"
    )
    @app_commands.describe(channel="Choose a channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def _logging_submission(
        self, interaction: discord.Interaction, channel: discord.channel.TextChannel
    ):
        await interaction.response.defer(thinking=True)
        await self.client.db_api.update_submission_channel(str(channel.id))
        await interaction.followup.send(
            f"{Assets.green_tick} **Tracking channel has been set to {channel.mention}**"
        )

    @logging_group.command(
        name="score", description="Sets a channel to track score updates"
    )
    @app_commands.describe(channel="Choose a channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def _logging_score(
        self, interaction: discord.Interaction, channel: discord.channel.TextChannel
    ):
        await interaction.response.defer(thinking=True)
        await self.client.db_api.update_score_channel(str(channel.id))
        await interaction.followup.send(
            f"{Assets.green_tick} **Tracking channel has been set to {channel.mention}**"
        )


async def setup(client):
    await client.add_cog(
        SetLogging(client), guilds=[discord.Object(id=client.config["serverId"])]
    )
