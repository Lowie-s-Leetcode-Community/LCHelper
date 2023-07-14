import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
import traceback

class QModal(discord.ui.Modal):
    def __init__(self, DBClient): 
        super().__init__(title = "Sending a question")
        self.DBClient = DBClient

    question_response = discord.ui.TextInput(
        label = 'Question', 
        style = discord.TextStyle.paragraph,          
        placeholder = 'Type your question here, as detailed as possible...',
        required = True,
        max_length = 3000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        qa_id = self.DBClient['LC_db']['LC_tracking'].find_one()['qa_id'] + 1
        embed = discord.Embed(
            description = self.question_response.value,
            timestamp = interaction.created_at,
            color = discord.Color.blue()
        )
        embed.set_author(
            name = f"🤔 #{qa_id}",
        )
        embed.set_footer(
            text = "Annoymous",
            icon_url = interaction.user.default_avatar.url
        )
        
        fb_channel = await interaction.guild.fetch_channel(1107851817347461120)
        msg = await fb_channel.send(embed = embed)
        await interaction.followup.send(f'Your question has been sent, check back frequently for answers, {interaction.user.display_name}!', ephemeral = True)
        await msg.create_thread(name = f"Question #{qa_id}")
        await msg.add_reaction("<:pepe_love:1087411917603221627>")
        self.DBClient['LC_db']['LC_tracking'].update_one({'qa_id': qa_id - 1}, {'$set': {'qa_id': qa_id}})

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral = True)
        traceback.print_exception(type(error), error, error.__traceback__)

class FBModal(discord.ui.Modal):
    def __init__(self, DBClient): 
        super().__init__(title = "Sending a feedback")
        self.DBClient = DBClient

    feedback_title = discord.ui.TextInput(
        label = "Title",
        placeholder = "Summarize your feedback here...",
        required = True
    )

    feedback_response = discord.ui.TextInput(
        label = 'Feedback', 
        style = discord.TextStyle.paragraph,          
        placeholder = 'Type your feedback here, as detailed as possible...',
        required = True,
        max_length = 3000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        feedback_id = self.DBClient['LC_db']['LC_tracking'].find_one()['feedback_id'] + 1
        embed = discord.Embed(
            title = self.feedback_title.value,
            description = self.feedback_response.value,
            timestamp = interaction.created_at,
            color = discord.Color.blue()
        )
        embed.set_author(
            name = f"💡 #{feedback_id}",
        )
        embed.set_footer(
            text = interaction.user,
            icon_url = interaction.user.avatar.url
        )
        
        fb_channel = await interaction.guild.fetch_channel(1107844996507390042)
        msg = await fb_channel.send(embed = embed)
        await interaction.followup.send(f'Your feedback has been sent, thank you for your contribution, {interaction.user.display_name}!', ephemeral = True)
        await msg.create_thread(name = f"Feedback #{feedback_id}")
        await msg.add_reaction("<:pepe_yes:1087411960737439804>")
        await msg.add_reaction("<:pepe_nope:1087411932979527720>")
        self.DBClient['LC_db']['LC_tracking'].update_one({'feedback_id': feedback_id - 1}, {'$set': {'feedback_id': feedback_id}})

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral = True)
        traceback.print_exception(type(error), error, error.__traceback__)

class QAView(discord.ui.View):
    def __init__(self, DBClient): 
        super().__init__(timeout = None)
        self.DBClient = DBClient

    @discord.ui.button(label = "Send a feedback (publicly)", style = discord.ButtonStyle.secondary, emoji = "💡", custom_id = 'persistent_view:fb')
    async def fb_call_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FBModal(self.DBClient))
    
    @discord.ui.button(label = "Ask a question (anonymously)", style = discord.ButtonStyle.primary, emoji = "🙋‍♂️", custom_id = 'persistent_view:ask')
    async def ask_call_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(QModal(self.DBClient))

class qa(commands.Cog):
    def __init__(self, client):
        self.client = client

        global DBClient
        DBclient = self.client.DBClient

    @app_commands.command(name = "qa-init", description = "Sends the initial 2-button message")
    @app_commands.checks.has_permissions(administrator = True)
    async def _qa_init(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        embed = discord.Embed(
            title = ":information_source: Info",
            description = """
            Feedback? Questions? Confessions? Sending out an anonymous love letter? :eyes:
            """,
            color = discord.Color.blue()
        )
        channel = await interaction.guild.fetch_channel(1107844406683389952)
        await channel.send(embed = embed, view = QAView(self.client.DBClient))
        await interaction.followup.send(f"{Assets.green_tick} **Embed sent!**")

    
async def setup(client):
    await client.add_cog(qa(client), guilds=[discord.Object(id=1085444549125611530)])
    #await client.add_cog(qa(client))
