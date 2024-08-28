import discord
import random
import typing
import asyncio
from discord import app_commands
from discord.ext import commands
from utils.lc_utils import LC_utils
from lib.embed.problem import ProblemEmbed

class DuelButton(discord.ui.Button['DuelView']):
    def __init__(
        self,
        label: str,
        style: discord.ButtonStyle,
        opponent: discord.Member,
        is_disabled: bool = False,
        emoji: typing.Union[str, discord.Emoji, discord.PartialEmoji, None] = None,
    ):
        super().__init__(style=style, label=label, disabled=is_disabled, emoji=emoji)
        self.opponent = opponent

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.opponent:
            await interaction.response.send_message(
                "Only the person challenged can interact with this button.",
                ephemeral=True
            )
            return
        await interaction.response.defer(ephemeral=True)
        await self.view.handle_choice(accept=(self.label == "Accept"))

class DuelView(discord.ui.View):
    def __init__(self, opponent: discord.Member):
        max_wait_time = 120 # seconds
        super().__init__(timeout=max_wait_time)
        self.response = None
        self.add_item(DuelButton(label="Accept", style=discord.ButtonStyle.green, opponent=opponent))
        self.add_item(DuelButton(label="Decline", style=discord.ButtonStyle.red, opponent=opponent))

    async def handle_choice(self, accept: bool):
        self.response = accept
        self.stop()

class Duel(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.is_duel_active = False
        self.problem_list = [
            problem for problem in self.client.db_api.read_problems_all()
            if problem['difficulty'] in ['Easy', 'Medium']
        ]
        self.current_problem = None
        self.players = []
        self.max_duel_timeout = 600  # seconds
        self.duel_timeout_task: asyncio.Task = None

    rank_group = app_commands.Group(name="duel", description="Ranking Group")

    @rank_group.command(name='start', description="I challenge you to a duel!")
    async def duel(self, interaction: discord.Interaction, opponent: discord.Member):
        if not await self.__check_verify(interaction, opponent):
            return

        if self.is_duel_active:
            if self.current_problem == None:
                await interaction.response.send_message(
                    f"A duel request between"
                    f"{self.players[0].mention} and {self.players[1].mention}"
                    f"is already in progress."
                    f"Try again later."
                )
                return
            else:
                embed = ProblemEmbed(self.current_problem)
                await interaction.response.send_message(
                    "**A duel is already in progress!**\n\n"
                    f"**Current Duel Details:**\n "
                    f"**Players Involved**: {self.players[0].mention} vs {self.players[1].mention}\n"
                    f"**Problem**: {self.current_problem['title']}\n"
                    f"**Status:** Solving...",
                    embed=embed
                )
                return

        self.is_duel_active = True

        view = DuelView(opponent)
        await interaction.response.send_message(
            f"{opponent.mention}, you have been challenged to a duel by {interaction.user.mention}. Do you accept?", 
            view=view
        )
        await view.wait()

        if view.response is None:
            await interaction.followup.send("Duel request timed out.")
            self.is_duel_active = False
        elif view.response:
            self.players = [interaction.user, opponent]
            self.current_problem = random.choice(self.problem_list)
            embed = ProblemEmbed(self.current_problem)
            await interaction.followup.send(
                f"**Duel between {self.players[0].mention} and {self.players[1].mention} has started.**\n\n"
                f"Solve this problem: **{self.current_problem['title']}**\n",
                embed=embed
            )
            # Start the timer
            self.duel_timeout_task = asyncio.create_task(self.__duel_timeout_coro(interaction=interaction))
        else:
            await interaction.followup.send(f"{opponent.mention} has declined the duel request.")
            self.is_duel_active = False

    async def __duel_timeout_coro(self, interaction: discord.Interaction):
        await asyncio.sleep(self.max_duel_timeout)
        if self.is_duel_active:
            await interaction.followup.send("The duel has ended due to timeout.")
            self.__reset_duel()

    async def __is_active_player(self, interaction: discord.Interaction):
        if not self.current_problem or not self.is_duel_active:
            await interaction.response.send_message("No duel is currently active.")
            return False
        if interaction.user not in self.players:
            await interaction.response.send_message("You are not part of the current duel.")
            return False
        return True

    async def __check_verify(self, interaction: discord.Interaction, opponent: discord.Member):
        if not self.client.db_api.read_profile(memberDiscordId=str(interaction.user.id)):
            await interaction.response.send_message(
                "Only verified member can duel. Type `/verify` to (re)verify yourself immediately!"
            )
            return False
        if not self.client.db_api.read_profile(memberDiscordId=str(opponent.id)):
            await interaction.response.send_message(
                f"The opponent {opponent.mention} is not verified and cannot participate in the duel."
            )
            return False
        if interaction.user == opponent:
            await interaction.response.send_message("You cannot duel yourself.")
            return False
        return True

    async def __check_solution(self, interaction: discord.Interaction):
        # Get recent AC submissions of the player
        result = self.client.db_api.read_profile(memberDiscordId=str(interaction.user.id))
        crawl_results = LC_utils.get_recent_ac(result['leetcodeUsername'], limit=1)

        if crawl_results is None or len(crawl_results) == 0:
            return False

        if crawl_results[0]['title'] == self.current_problem['title']:
            return True

        return False

    def __reset_duel(self):
        self.is_duel_active = False
        self.current_problem = None
        self.players = []
        self.duel_timeout_task.cancel()

    @rank_group.command(name='submit', description="Submit your solution!")
    async def submit(self, interaction: discord.Interaction):
        if not await self.__is_active_player(interaction):
            return

        if await self.__check_solution(interaction):
            await interaction.response.send_message(f"Congratulations {interaction.user.mention}, you have won the duel!")
            self.__reset_duel()
        else:
            await interaction.response.send_message(f"Sorry {interaction.user.mention}, you have not solved the problem yet.")

    @rank_group.command(name='propose_draw', description="Propose a draw.")
    async def propose_draw(self, interaction: discord.Interaction):
        if not await self.__is_active_player(interaction):
            return

        proposer = self.players[0] if interaction.user == self.players[0] else self.players[1]
        opponent = self.players[1] if interaction.user == self.players[0] else self.players[0]

        view = DuelView(opponent)
        await interaction.response.send_message(
            f"{opponent.mention}, {proposer.mention} has proposed a draw. Do you accept?", 
            view=view
        )
        await view.wait()

        if view.response is None:
            await interaction.followup.send("Draw request timed out.")
        elif view.response:
            await interaction.followup.send(
                f"The duel between {proposer.mention} and {opponent.mention} has been drawn. End the duel!"
            )
            self.__reset_duel()
        else:
            await interaction.followup.send(f"{opponent.mention} has declined the draw request. The duel continues!")

    @rank_group.command(name='surrender', description="Surrender the duel.")
    async def surrender(self, interaction: discord.Interaction):
        if not await self.__is_active_player(interaction):
            return

        surrenderer = self.players[0] if interaction.user == self.players[0] else self.players[1]
        winner = self.players[1] if interaction.user == self.players[0] else self.players[0]

        await interaction.response.send_message(f"{surrenderer.mention} has surrendered. {winner.mention} wins the duel!")

        self.__reset_duel()

async def setup(client):
    await client.add_cog(Duel(client), guilds=[discord.Object(id=client.config['serverId'])])
