import asyncio
import random
from enum import Enum
from typing import Dict, Union

import discord
from discord import app_commands
from discord.ext import commands

from lib.embed.problem import ProblemEmbed
from utils.lc_utils import LC_utils


class PlayerStatus(Enum):
    UNFINISHED = 0
    LOST = 1
    WON = 2


class DuelButton(discord.ui.Button["DuelView"]):
    def __init__(
        self,
        label: str,
        style: discord.ButtonStyle,
        opponent: discord.Member,
        is_disabled: bool = False,
        emoji: Union[str, discord.Emoji, discord.PartialEmoji, None] = None,
    ):
        super().__init__(style=style, label=label, disabled=is_disabled, emoji=emoji)
        self.opponent = opponent

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.opponent:
            await interaction.response.send_message(
                "Only the person challenged can interact with this button.",
                ephemeral=True,
            )
            return
        await interaction.response.defer(ephemeral=True)
        await self.view.handle_choice(accept=(self.label == "Accept"))


class DuelView(discord.ui.View):
    VIEW_TIMEOUT = 120  # seconds

    def __init__(self, opponent: discord.Member):
        super().__init__(timeout=self.VIEW_TIMEOUT)
        self.accepted = None
        self.add_item(
            DuelButton(
                label="Accept", style=discord.ButtonStyle.green, opponent=opponent
            )
        )
        self.add_item(
            DuelButton(
                label="Decline", style=discord.ButtonStyle.red, opponent=opponent
            )
        )

    async def handle_choice(self, accept: bool):
        self.accepted = accept
        self.stop()


class Duel(commands.Cog):
    DUEL_DURATION = 600  # seconds

    def __init__(self, client):
        self.client = client

        self.problem_list = [
            problem
            for problem in self.client.db_api.read_problems_all()
            if problem["difficulty"] in ["Easy", "Medium"] and not problem["isPremium"]
        ]

        # Duel ID syntax: f"{player_0.id} {player_1.id}"
        # If the value (problemid) is None, the duel is in the Request state.
        # Otherwise it is in the Active state.
        self.duelid_to_problemid: Dict[str, int] = {}
        self.problemid_to_problem: Dict[int, dict] = {}
        self.userid_to_duelid: Dict[int, str] = {}
        self.duelid_to_timeout: Dict[str, asyncio.Task] = {}

    duel_group = app_commands.Group(name="duel", description="Duel commands")

    @duel_group.command(name="start", description="I challenge you to a duel!")
    async def duel(self, interaction: discord.Interaction, opponent: discord.Member):
        if not await self.__check_verify(interaction, opponent):
            return

        if await self.__check_existing_duel(interaction, opponent):
            return

        duel_id = f"{interaction.user.id} {opponent.id}"
        self.duelid_to_problemid[duel_id] = None
        self.userid_to_duelid[interaction.user.id] = duel_id
        self.userid_to_duelid[opponent.id] = duel_id

        view = DuelView(opponent)
        await interaction.response.send_message(
            f"{opponent.mention}, you have been challenged to a duel by {interaction.user.mention}. Do you accept?",
            view=view,
        )
        await view.wait()

        if view.accepted is None:
            await interaction.followup.send("Duel request timed out.")
            self.__reset_duel(duel_id)
        elif view.accepted:
            problem = random.choice(self.problem_list)
            self.problemid_to_problem[int(problem["id"])] = problem
            self.duelid_to_problemid[duel_id] = int(problem["id"])

            embed = ProblemEmbed(problem)
            await interaction.followup.send(
                f"**Duel between {interaction.user.mention} and {opponent.mention} has started.**\n\n"
                f"Solve this problem: **{problem['id']}. {problem['title']}**\n",
                embed=embed,
            )
            # Start the timer
            self.duelid_to_timeout[duel_id] = asyncio.create_task(
                self.__duel_timeout_coro(interaction=interaction, duel_id=duel_id)
            )
        else:
            await interaction.followup.send(
                f"{opponent.mention} has declined the duel request."
            )
            self.__reset_duel(duel_id)

    async def __check_existing_duel(
        self, interaction: discord.Interaction, opponent: discord.Member
    ) -> bool:
        """
        Check if either the challenger or the opponent is already in a duel (Request or Active state).
        """
        if (
            interaction.user.id in self.userid_to_duelid
            or opponent.id in self.userid_to_duelid
        ):
            duel_id = (
                self.userid_to_duelid[opponent.id]
                if opponent.id in self.userid_to_duelid
                else self.userid_to_duelid[interaction.user.id]
            )
            player_0, player_1 = self.__get_players(duel_id)
            problem_id = self.duelid_to_problemid[duel_id]

            if not problem_id:  # Request state
                await interaction.response.send_message(
                    f"A duel request between {player_0.mention} and {player_1.mention} "
                    f"is already in progress. Try again later."
                )
            else:  # Active state
                current_problem = self.problemid_to_problem[problem_id]
                embed = ProblemEmbed(current_problem)
                await interaction.response.send_message(
                    "**A duel between the following players is already in progress.**\n\n"
                    f"**Current Duel Details:**\n"
                    f"**Players Involved**: {player_0.mention} vs {player_1.mention}\n"
                    f"**Problem**: {current_problem['id']}. {current_problem['title']}\n",
                    embed=embed,
                )

            return True

        return False

    async def __duel_timeout_coro(self, interaction: discord.Interaction, duel_id: str):
        """
        Coroutine to handle the timeout of an Active duel.
        """
        await asyncio.sleep(self.DUEL_DURATION)
        if duel_id in self.duelid_to_problemid:
            player_0, player_1 = self.__get_players(duel_id)
            announce_msg = f"The duel between {player_0.mention} and {player_1.mention} has ended due to timeout."
            player_0_status = self.__check_solution(interaction)

            if player_0_status == PlayerStatus.UNFINISHED:
                announce_msg += "\nThe duel ended in a draw!"
            elif player_0_status == PlayerStatus.WON:
                announce_msg += f"\n{player_0.mention} wins the duel!"
            else:
                announce_msg += f"\n{player_1.mention} wins the duel!"

            await interaction.followup.send(announce_msg)
            self.__reset_duel(duel_id)

    async def __is_active_player(self, interaction: discord.Interaction):
        if not self.duelid_to_problemid:
            await interaction.response.send_message("No duel is currently active.")
            return False

        if not any(
            interaction.user.id in duel
            for duel in (
                map(int, duel_id.split())
                for duel_id, problem_id in self.duelid_to_problemid.items()
                if problem_id is not None  # Check only active duels
            )
        ):
            await interaction.response.send_message(
                "You are not part of any active duel."
            )
            return False

        return True

    async def __check_verify(
        self, interaction: discord.Interaction, opponent: discord.Member
    ):
        """
        Check if the challenger and the opponent are Verified members.
        """
        if not self.client.db_api.read_profile(
            memberDiscordId=str(interaction.user.id)
        ):
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

    def __get_players(self, duel_id: str) -> tuple[discord.Member, discord.Member]:
        player_0, player_1 = map(
            lambda x: self.client.get_user(int(x)), duel_id.split()
        )
        return player_0, player_1

    def __get_opponent(self, player_id: int) -> discord.Member:
        player_0, player_1 = self.__get_players(self.userid_to_duelid[player_id])
        return player_1 if player_id == player_0.id else player_0

    async def __check_solution(self, interaction: discord.Interaction) -> PlayerStatus:
        """
        Check if the player has solved the problem. Also checks if the opponent has
        also solved the problem, in which case compare the submission time.
        """
        # Get recent AC submissions of the player
        duel_id = self.userid_to_duelid[interaction.user.id]
        problem = self.problemid_to_problem[self.duelid_to_problemid[duel_id]]

        player = self.client.db_api.read_profile(
            memberDiscordId=str(interaction.user.id)
        )
        opponent = self.client.db_api.read_profile(
            memberDiscordId=str(self.__get_opponent(interaction.user.id).id)
        )

        player_recent_ac = LC_utils.get_recent_ac(player["leetcodeUsername"], limit=1)
        opponent_recent_ac = LC_utils.get_recent_ac(
            opponent["leetcodeUsername"], limit=1
        )

        # Opponent has not solved the problem
        if not opponent_recent_ac or opponent_recent_ac[0]["title"] != problem["title"]:
            if not player_recent_ac or player_recent_ac[0]["title"] != problem["title"]:
                return PlayerStatus.UNFINISHED
            return PlayerStatus.WON

        # Opponent has solved the problem
        if not player_recent_ac or player_recent_ac[0]["title"] != problem["title"]:
            return PlayerStatus.LOST

        if int(opponent_recent_ac[0]["timestamp"]) < int(
            player_recent_ac[0]["timestamp"]
        ):
            return PlayerStatus.LOST

        return PlayerStatus.WON

    def __reset_duel(self, duel_id: str):
        """
        End the duel and clean up the data structures.
        """
        player_0_id, player_1_id = map(int, duel_id.split())

        del self.userid_to_duelid[player_0_id]
        del self.userid_to_duelid[player_1_id]
        del self.duelid_to_problemid[duel_id]

        # Duel can either be in Request or Active state
        if duel_id in self.duelid_to_timeout:
            self.duelid_to_timeout[duel_id].cancel()
            del self.duelid_to_timeout[duel_id]

    @duel_group.command(name="submit", description="Submit your solution!")
    async def submit(self, interaction: discord.Interaction):
        if not await self.__is_active_player(interaction):
            return

        opponent = self.__get_opponent(interaction.user.id)
        player_status = await self.__check_solution(interaction)

        if player_status == PlayerStatus.WON:
            await interaction.response.send_message(
                f"Sorry {opponent.mention}, your opponent has solved the problem first."
                f"\nCongratulations {interaction.user.mention}, you have won the duel!"
            )
            self.__reset_duel(self.userid_to_duelid[interaction.user.id])
        elif player_status == PlayerStatus.UNFINISHED:
            await interaction.response.send_message(
                f"Sorry {interaction.user.mention}, you have not solved the problem yet."
            )
        else:  # PlayerStatus.LOST
            await interaction.response.send_message(
                f"Sorry {interaction.user.mention}, your opponent has solved the problem "
                f"first.\n{opponent.mention} wins the duel!"
            )
            self.__reset_duel(self.userid_to_duelid[interaction.user.id])

    @duel_group.command(name="propose_draw", description="Propose a draw.")
    async def propose_draw(self, interaction: discord.Interaction):
        if not await self.__is_active_player(interaction):
            return

        duel_id = self.userid_to_duelid[interaction.user.id]
        player_0, player_1 = self.__get_players(duel_id)

        opponent = player_1 if interaction.user == player_0 else player_0

        view = DuelView(opponent)
        await interaction.response.send_message(
            f"{opponent.mention}, {interaction.user.mention} has proposed a draw. Do you accept?",
            view=view,
        )
        await view.wait()

        if view.accepted is None:
            await interaction.followup.send("Draw request timed out.")
        elif view.accepted:
            await interaction.followup.send(
                f"The duel between {interaction.user.mention} and {opponent.mention} "
                f"has ended in a draw!"
            )
            self.__reset_duel(duel_id)
        else:
            await interaction.followup.send(
                f"{opponent.mention} has declined the draw request. The duel continues!"
            )

    @duel_group.command(name="surrender", description="Surrender the duel.")
    async def surrender(self, interaction: discord.Interaction):
        if not await self.__is_active_player(interaction):
            return

        duel_id = self.userid_to_duelid[interaction.user.id]
        player_0, player_1 = self.__get_players(duel_id)

        opponent = player_1 if interaction.user == player_0 else player_0

        await interaction.response.send_message(
            f"{interaction.user.mention} has surrendered. {opponent.mention} wins the duel!"
        )

        self.__reset_duel(duel_id)


async def setup(client):
    await client.add_cog(
        Duel(client), guilds=[discord.Object(id=client.config["serverId"])]
    )
