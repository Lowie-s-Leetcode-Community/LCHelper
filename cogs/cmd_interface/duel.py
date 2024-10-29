import asyncio
import random
import time
from enum import Enum
from typing import Awaitable, Callable, Dict, List, Union

import discord
from discord import app_commands
from discord.ext import commands

from lib.embed.problem import ProblemEmbed
from utils.lc_utils import LC_utils
from utils.roles import Roles


class PlayerStatus(Enum):
    UNFINISHED = 0
    LOST = 1
    WON = 2


class DuelDuration:  # seconds
    EASY = 600
    MEDIUM = 1200


class DuelProblemButtonType:
    SUBMIT = "Submit"
    PROPOSE_DRAW = "Propose Draw"
    SURRENDER = "Surrender"


class DuelProblemButton(discord.ui.Button["DuelProblemView"]):
    def __init__(
        self,
        label: str,
        style: discord.ButtonStyle,
        players: List[discord.Member],
        is_disabled: bool = False,
        emoji: Union[str, discord.Emoji, discord.PartialEmoji, None] = None,
    ):
        super().__init__(style=style, label=label, disabled=is_disabled, emoji=emoji)
        self.players = players

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in self.players:
            await interaction.response.send_message(
                "Only the players involved in this duel can interact with these buttons.",
                ephemeral=True,
            )
            return
        await interaction.response.defer(ephemeral=True)
        await self.view.handle_button_press(interaction, self.label)


class DuelProblemView(discord.ui.View):
    def __init__(
        self,
        players: List[discord.Member],
        submit: Callable[[discord.Interaction], Awaitable[bool]],
        propose_draw: Callable[[discord.Interaction], Awaitable[bool]],
        surrender: Callable[[discord.Interaction], Awaitable[bool]],
        duel_duration: int = DuelDuration.EASY,
    ):
        super().__init__(timeout=duel_duration)
        self.submit_handler = submit
        self.propose_draw_handler = propose_draw
        self.surrender_handler = surrender

        self.add_item(
            DuelProblemButton(
                label=DuelProblemButtonType.SUBMIT,
                style=discord.ButtonStyle.green,
                players=players,
            )
        ).add_item(
            DuelProblemButton(
                label=DuelProblemButtonType.PROPOSE_DRAW,
                style=discord.ButtonStyle.blurple,
                players=players,
            )
        ).add_item(
            DuelProblemButton(
                label=DuelProblemButtonType.SURRENDER,
                style=discord.ButtonStyle.red,
                players=players,
            )
        )

    async def handle_button_press(
        self, interaction: discord.Interaction, button_type: DuelProblemButtonType
    ) -> None:
        handler: Callable[[discord.Interaction], Awaitable[bool]] = None

        if button_type == DuelProblemButtonType.SUBMIT:
            handler = self.submit_handler
        elif button_type == DuelProblemButtonType.PROPOSE_DRAW:
            handler = self.propose_draw_handler
        else:  # DuelProblemButtonType.SURRENDER:
            handler = self.surrender_handler

        if not await handler(interaction):
            return
        self.stop()


class DuelRequestButton(discord.ui.Button["DuelRequestView"]):
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


class DuelRequestView(discord.ui.View):
    REQUEST_TIMEOUT = 120  # seconds

    def __init__(self, opponent: discord.Member):
        super().__init__(timeout=self.REQUEST_TIMEOUT)
        self.accepted = None
        self.add_item(
            DuelRequestButton(
                label="Accept", style=discord.ButtonStyle.green, opponent=opponent
            )
        ).add_item(
            DuelRequestButton(
                label="Decline", style=discord.ButtonStyle.red, opponent=opponent
            )
        )

    async def handle_choice(self, accept: bool):
        self.accepted = accept
        self.stop()


class DuelAssignButton(discord.ui.Button["DuelAssignView"]):
    def __init__(
        self,
        label: str,
        style: discord.ButtonStyle,
        players: List[discord.Member],
        is_disabled: bool = False,
        emoji: Union[str, discord.Emoji, discord.PartialEmoji, None] = None,
    ):
        super().__init__(style=style, label=label, disabled=is_disabled, emoji=emoji)
        self.players = players

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in self.players:
            await interaction.response.send_message(
                "Only the players assigned to this duel can interact with these buttons.",
                ephemeral=True,
            )
            return
        await interaction.response.defer(ephemeral=True)
        await self.view.handle_choice(
            interaction=interaction, accept=(self.label == "Accept")
        )


class DuelAssignView(discord.ui.View):
    ASSIGN_TIMEOUT = 120  # seconds

    def __init__(self, players: List[discord.Member]):
        super().__init__(timeout=self.ASSIGN_TIMEOUT)
        self.players = players
        self.accepted: List[bool | None] = [None, None]
        self.add_item(
            DuelAssignButton(
                label="Accept", style=discord.ButtonStyle.green, players=players
            )
        ).add_item(
            DuelAssignButton(
                label="Decline", style=discord.ButtonStyle.red, players=players
            )
        )

    async def handle_choice(self, interaction: discord.Interaction, accept: bool):
        player_index = self.players.index(interaction.user)

        if self.accepted[player_index]:
            await interaction.followup.send(
                "You have already accepted to the duel assignment.", ephemeral=True
            )
            return

        self.accepted[player_index] = accept

        if accept:
            if all(self.accepted):
                self.stop()
                return
            await interaction.followup.send(
                f"{interaction.user.mention} have accepted the duel assignment. "
                f"Waiting for the other player to accept."
            )
        else:  # not accept
            other_index = 1 - player_index
            self.accepted[other_index] = True
            self.stop()


class Duel(commands.Cog):
    ALLOWED_TOPICS = [
        "Array",
        "Backtracking",
        "Binary Search",
        "Binary Tree",
        "Breadth-First Search",
        "Counting",
        "Depth-First Search",
        "Dynamic Programming",
        "Graph",
        "Greedy",
        "Hash Table",
        "Heap (Priority Queue)",
        "Linked List",
        "Math",
        "Matrix",
        "Prefix Sum",
        "Queue",
        "Recursion",
        "Simulation",
        "Sliding Window",
        "Sorting",
        "Stack",
        "String",
        "Tree",
        "Two Pointers",
    ]
    TOPICS_BLACKLIST = [
        "Binary Indexed Tree",
        "Binary Search Tree",
        "Bitmask",
        "Brainteaser",
        "Combinatorics",
        "Concurrency",
        "Data Stream",
        "Database",
        "Design",
        "Divide and Conquer",
        "Enumeration",
        "Game Theory",
        "Hash Function",
        "Interactive",
        "Iterator",
        "Line Sweep",
        "Minimum Spanning Tree",
        "Monotonic Queue",
        "Monotonic Stack",
        "Number Theory",
        "Ordered Set",
        "Probability and Statistics",
        "Quickselect",
        "Randomized",
        "Reservoir Sampling",
        "Rolling Hash",
        "Segment Tree",
        "Shell",
        "Topological Sort",
        "Strongly Connected Component",
    ]

    def __init__(self, client):
        self.client = client

        self.problem_list = [
            problem
            for problem in self.client.db_api.read_problems_all_with_topics()
            if problem["difficulty"] in ["Easy", "Medium"]
            and not problem["isPremium"]
            and any(topic in self.ALLOWED_TOPICS for topic in problem["topics"])
            and all(topic not in self.TOPICS_BLACKLIST for topic in problem["topics"])
        ]

        # Duel ID syntax: f"{player_0.id} {player_1.id}"
        # If the value (problemid) is None, the duel is in the Request state.
        # Otherwise it is in the Active state.
        self.duelid_to_problemid: Dict[str, int] = {}
        self.problemid_to_problem: Dict[int, dict] = {}
        self.userid_to_duelid: Dict[int, str] = {}
        self.duelid_to_timeout: Dict[str, asyncio.Task] = {}

        # Maps duel_id to player_id that proposed the draw
        self.duels_proposing_draw: Dict[str, int] = {}

        # start_time is a timestamp when the duel was activated
        self.duelid_to_start_time: Dict[str, int] = {}

    duel_group = app_commands.Group(name="duel", description="Commands for dueling.")

    @duel_group.command(
        name="request", description="Challenge another verified member to a duel."
    )
    @app_commands.describe(
        difficulty="Choose a difficulty for the problem (default is both Easy and Medium)"
    )
    @app_commands.choices(
        difficulty=[
            app_commands.Choice(name="Easy", value="Easy"),
            app_commands.Choice(name="Medium", value="Medium"),
        ]
    )
    async def duel(
        self,
        interaction: discord.Interaction,
        opponent: discord.Member,
        difficulty: str | None = None,
    ):
        if not await self.__check_verify(interaction, interaction.user, opponent):
            return

        if await self.__check_existing_duel(interaction, interaction.user, opponent):
            return

        duel_id = self.__initialize_duel(interaction.user, opponent)

        view = DuelRequestView(opponent)
        await interaction.response.send_message(
            f"{opponent.mention}, you have been challenged to a duel by {interaction.user.mention}. Do you accept?"
            + (
                "" if difficulty is None else f"\n\nChosen difficulty: **{difficulty}**"
            ),
            view=view,
        )
        await view.wait()

        if view.accepted is None:
            await interaction.followup.send("Duel request timed out.")
            self.__reset_duel(duel_id)
        elif view.accepted:
            await self.__activate_duel(
                interaction, interaction.user, opponent, difficulty, duel_id
            )
        else:
            await interaction.followup.send(
                f"{opponent.mention} has declined the duel request."
            )
            self.__reset_duel(duel_id)

    @duel_group.command(
        name="assign", description="Assign a duel between two verified members."
    )
    @commands.has_any_role(Roles.LLCLASS_TA)
    @app_commands.describe(
        difficulty="Choose a difficulty for the problem (default is both Easy and Medium)"
    )
    @app_commands.choices(
        difficulty=[
            app_commands.Choice(name="Easy", value="Easy"),
            app_commands.Choice(name="Medium", value="Medium"),
        ]
    )
    async def duel_assign(
        self,
        interaction: discord.Interaction,
        player_0: discord.Member,
        player_1: discord.Member,
        difficulty: str | None = None,
    ):
        if not await self.__check_verify(interaction, player_0, player_1):
            return

        if await self.__check_existing_duel(interaction, player_0, player_1):
            return

        duel_id = self.__initialize_duel(player_0, player_1)

        view = DuelAssignView([player_0, player_1])
        await interaction.response.send_message(
            f"{player_0.mention} {player_1.mention}, you have been assigned to duel"
            f" each other. Do you accept?"
            + ("" if difficulty is None else f"\n\nChosen difficulty: **{difficulty}**")
            + "\n\nFor the duel to start, **both players must accept**",
            view=view,
        )
        await view.wait()

        if any(accepted is None for accepted in view.accepted):
            await interaction.followup.send("Duel assignment timed out.")
            self.__reset_duel(duel_id)
        elif all(view.accepted):
            await self.__activate_duel(
                interaction, player_0, player_1, difficulty, duel_id
            )
        else:  # One of the players declined
            for i in range(2):
                if view.accepted[i] is False:
                    await interaction.followup.send(
                        f"{view.players[i].mention} has declined the duel assignment."
                    )
                    break
            self.__reset_duel(duel_id)

    def __initialize_duel(
        self, player_0: discord.Member, player_1: discord.Member
    ) -> str:
        duel_id = f"{player_0.id} {player_1.id}"
        self.duelid_to_problemid[duel_id] = None
        self.userid_to_duelid[player_0.id] = duel_id
        self.userid_to_duelid[player_1.id] = duel_id
        return duel_id

    async def __activate_duel(
        self,
        interaction: discord.Interaction,
        player_0: discord.Member,
        player_1: discord.Member,
        difficulty: str | None,
        duel_id: str,
    ) -> None:
        problem = random.choice(self.problem_list)

        if difficulty:
            while problem["difficulty"] != difficulty:
                problem = random.choice(self.problem_list)

        self.problemid_to_problem[int(problem["id"])] = problem
        self.duelid_to_problemid[duel_id] = int(problem["id"])
        self.duelid_to_start_time[duel_id] = int(time.time())
        duel_duration = (
            DuelDuration.EASY
            if problem["difficulty"] == "Easy"
            else DuelDuration.MEDIUM
        )

        embed = ProblemEmbed(problem)
        view = DuelProblemView(
            [player_0, player_1],
            self.submit,
            self.propose_draw,
            self.surrender,
            duel_duration=duel_duration,
        )
        await interaction.followup.send(
            f"**Duel between {player_0.mention} and {player_1.mention} has started.**\n\n"
            f"**Duel ends <t:{int(time.time() + duel_duration)}:R>**\n\n"
            f"Solve this problem: **{problem['id']}. {problem['title']}**\n",
            embed=embed,
            view=view,
        )
        # Start the timer
        self.duelid_to_timeout[duel_id] = asyncio.create_task(
            self.__duel_timeout_coro(
                interaction=interaction, duel_id=duel_id, duel_duration=duel_duration
            )
        )

    async def __check_existing_duel(
        self,
        interaction: discord.Interaction,
        player_0: discord.Member,
        player_1: discord.Member,
    ) -> bool:
        """
        Check if either the challenger or the opponent is already in a duel (Request or Active state).
        """
        if player_0.id in self.userid_to_duelid or player_1.id in self.userid_to_duelid:
            duel_id = (
                self.userid_to_duelid[player_1.id]
                if player_1.id in self.userid_to_duelid
                else self.userid_to_duelid[player_0.id]
            )
            duel_player_0, duel_player_1 = self.__get_players(duel_id)
            problem_id = self.duelid_to_problemid[duel_id]

            if not problem_id:  # Request state
                await interaction.response.send_message(
                    f"A duel request between {duel_player_0.mention} and {duel_player_1.mention} "
                    f"is already in progress. Try again later."
                )
            else:  # Active state
                current_problem = self.problemid_to_problem[problem_id]
                embed = ProblemEmbed(current_problem)
                await interaction.response.send_message(
                    f"**A duel between the following players is already in progress.**\n\n"
                    f"**Current Duel Details:**\n"
                    f"**Players Involved**: {duel_player_0.mention} vs {duel_player_1.mention}\n"
                    f"**Problem**: {current_problem['id']}. {current_problem['title']}\n",
                    embed=embed,
                )

            return True

        return False

    async def __duel_timeout_coro(
        self,
        interaction: discord.Interaction,
        duel_id: str,
        duel_duration: int = DuelDuration.EASY,
    ):
        """
        Coroutine to handle the timeout of an Active duel.
        """
        await asyncio.sleep(duel_duration)
        if duel_id in self.duelid_to_problemid:
            player_0, player_1 = self.__get_players(duel_id)
            announce_msg = f"The duel between {player_0.mention} and {player_1.mention} has ended due to timeout."
            player_0_status = self.__check_solution(interaction)

            if player_0_status == PlayerStatus.UNFINISHED:
                announce_msg += "\nThe duel ended in a draw!"
            elif player_0_status == PlayerStatus.WON:
                announce_msg += (
                    f"\n{player_0.mention} wins the duel!"
                    + self.__get_submit_stats(duel_id)
                )
            else:
                announce_msg += (
                    f"\n{player_1.mention} wins the duel!"
                    + self.__get_submit_stats(duel_id)
                )

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
        self,
        interaction: discord.Interaction,
        player_0: discord.Member,
        player_1: discord.Member,
    ):
        """
        Check if the challenger and the opponent are Verified members.
        """
        if not self.client.db_api.read_profile(memberDiscordId=str(player_0.id)):
            await interaction.response.send_message(
                f"The player {player_0.mention} is not verified and cannot participate in the duel."
            )
            return False

        if not self.client.db_api.read_profile(memberDiscordId=str(player_1.id)):
            await interaction.response.send_message(
                f"The player {player_1.mention} is not verified and cannot participate in the duel."
            )
            return False

        if player_0 == player_1:
            await interaction.response.send_message("A member cannot duel themselves.")
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

    def __check_solution(self, interaction: discord.Interaction) -> PlayerStatus:
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
        if not self.__has_solved(problem, opponent_recent_ac, duel_id):
            if not self.__has_solved(problem, player_recent_ac, duel_id):
                return PlayerStatus.UNFINISHED
            return PlayerStatus.WON

        # Opponent has solved the problem
        if not self.__has_solved(problem, player_recent_ac, duel_id):
            return PlayerStatus.LOST

        if int(opponent_recent_ac[0]["timestamp"]) < int(
            player_recent_ac[0]["timestamp"]
        ):
            return PlayerStatus.LOST

        return PlayerStatus.WON

    def __has_solved(self, problem: dict, player_recent_ac: dict, duel_id: str) -> bool:
        return (
            player_recent_ac
            and player_recent_ac[0]["title"] == problem["title"]
            and int(player_recent_ac[0]["timestamp"])
            > self.duelid_to_start_time[duel_id]
        )

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
            del self.duelid_to_start_time[duel_id]

    def __get_submit_stats(self, duel_id: str) -> str:
        problem = self.problemid_to_problem[self.duelid_to_problemid[duel_id]]
        player_0, player_1 = self.__get_players(duel_id)

        player_0_profile = self.client.db_api.read_profile(
            memberDiscordId=str(player_0.id)
        )
        player_1_profile = self.client.db_api.read_profile(
            memberDiscordId=str(player_1.id)
        )

        player_0_recent_ac = LC_utils.get_recent_ac(
            player_0_profile["leetcodeUsername"], limit=1
        )
        player_1_recent_ac = LC_utils.get_recent_ac(
            player_1_profile["leetcodeUsername"], limit=1
        )

        return (
            "\n\n**Statistics:**\n"
            + (
                f"{player_0.mention} has not submitted a solution yet."
                if not self.__has_solved(problem, player_0_recent_ac, duel_id)
                else f"{player_0.mention} solved the problem in {int(player_0_recent_ac[0]['timestamp']) - self.duelid_to_start_time[duel_id]} seconds. **[LeetCode Submission](https://leetcode.com/submissions/detail/{player_0_recent_ac[0]['id']})**"
            )
            + "\n"
            + (
                f"{player_1.mention} has not submitted a solution yet."
                if not self.__has_solved(problem, player_1_recent_ac, duel_id)
                else f"{player_1.mention} solved the problem in {int(player_1_recent_ac[0]['timestamp']) - self.duelid_to_start_time[duel_id]} seconds. **[LeetCode Submission](https://leetcode.com/submissions/detail/{player_1_recent_ac[0]['id']})**"
            )
        )

    async def submit(self, interaction: discord.Interaction) -> bool:
        if not await self.__is_active_player(interaction):
            return False

        opponent = self.__get_opponent(interaction.user.id)
        player_status = self.__check_solution(interaction)
        interaction_send: Callable[[str], Awaitable[None]] = (
            interaction.response.send_message
            if interaction.type == discord.InteractionType.application_command
            else interaction.followup.send
        )

        if player_status == PlayerStatus.WON:
            await interaction_send(
                f"Sorry {opponent.mention}, your opponent has solved the problem first.\n"
                f":confetti_ball: Congratulations {interaction.user.mention}, you have won the duel! :confetti_ball:"
                + self.__get_submit_stats(self.userid_to_duelid[interaction.user.id])
            )
            self.__reset_duel(self.userid_to_duelid[interaction.user.id])
            return True
        elif player_status == PlayerStatus.UNFINISHED:
            await interaction_send(
                f"Sorry {interaction.user.mention}, you have not solved the problem yet."
            )
            return False
        else:  # PlayerStatus.LOST
            await interaction_send(
                f"Sorry {interaction.user.mention}, your opponent has solved the problem first.\n"
                f":confetti_ball: {opponent.mention} wins the duel! :confetti_ball:"
                + self.__get_submit_stats(self.userid_to_duelid[interaction.user.id])
            )
            self.__reset_duel(self.userid_to_duelid[interaction.user.id])
            return True

    async def propose_draw(self, interaction: discord.Interaction) -> bool:
        if not await self.__is_active_player(interaction):
            return False

        duel_id = self.userid_to_duelid[interaction.user.id]
        player_0, player_1 = self.__get_players(duel_id)
        interaction_send: Callable[[str], Awaitable[None]] = (
            interaction.response.send_message
            if interaction.type == discord.InteractionType.application_command
            else interaction.followup.send
        )

        if duel_id in self.duels_proposing_draw:
            if self.duels_proposing_draw[duel_id] == interaction.user.id:
                await interaction_send(
                    "You have already proposed a draw. Please wait for your opponent to respond.",
                    ephemeral=True,
                )
            else:
                await interaction_send(
                    "Your opponent has already proposed a draw. Please respond to their request.",
                    ephemeral=True,
                )
            return False

        opponent = player_1 if interaction.user == player_0 else player_0

        view = DuelRequestView(opponent)
        await interaction_send(
            f"{opponent.mention}, {interaction.user.mention} has proposed a draw. Do you accept?",
            view=view,
        )
        await view.wait()

        if view.accepted is None:
            await interaction.followup.send("Draw request timed out.")
            return False
        elif view.accepted:
            await interaction.followup.send(
                f"The duel between {interaction.user.mention} and {opponent.mention} "
                f"has ended in a draw!"
            )
            self.__reset_duel(duel_id)
            return True
        else:
            await interaction.followup.send(
                f"{opponent.mention} has declined the draw request. The duel continues!"
            )
            return False

    async def surrender(self, interaction: discord.Interaction) -> bool:
        if not await self.__is_active_player(interaction):
            return False

        duel_id = self.userid_to_duelid[interaction.user.id]
        player_0, player_1 = self.__get_players(duel_id)
        interaction_send: Callable[[str], Awaitable[None]] = (
            interaction.response.send_message
            if interaction.type == discord.InteractionType.application_command
            else interaction.followup.send
        )

        opponent = player_1 if interaction.user == player_0 else player_0

        await interaction_send(
            f"{interaction.user.mention} has surrendered. {opponent.mention} wins the duel!"
        )

        self.__reset_duel(duel_id)
        return True

    @duel_group.command(
        name="submit",
        description="Submit to your current duel after you have submitted on LeetCode.",
    )
    async def duel_submit(self, interaction: discord.Interaction):
        await self.submit(interaction)

    @duel_group.command(
        name="propose_draw", description="Propose a draw to your opponent in the duel."
    )
    async def duel_propose_draw(self, interaction: discord.Interaction):
        await self.propose_draw(interaction)

    @duel_group.command(
        name="surrender", description="Surrender from your current duel."
    )
    async def duel_surrender(self, interaction: discord.Interaction):
        await self.surrender(interaction)


async def setup(client):
    await client.add_cog(
        Duel(client), guilds=[discord.Object(id=client.config["serverId"])]
    )
