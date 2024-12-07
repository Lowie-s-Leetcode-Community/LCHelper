import asyncio
import typing

import discord
from discord import app_commands
from discord.ext import commands

from utils.asset import Assets

option_labels = ["A. ", "B. ", "C. ", "D. ", "E. ", "F. ", "Unanswered"]
choice_emojis = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫"]
SCORE_FOR_DIFFICULTY = {"Easy": 1, "Medium": 2, "Hard": 3}
NUMS_OF_QUIZ = 5
UNANSWERED = -1
CANNOT_ANSWER = -2
PREV = 1
NEXT = 3
END = 4


def create_embed(
    _question: dict, _answer: dict, score, idx_quiz, num_quiz, choice: int = UNANSWERED
):
    question = _question
    answers = _answer

    correct_answer = question.correctAnswerId - answers[0].id

    embed = discord.Embed(color=getattr(Assets, question.difficulty.lower()))
    embed.set_author(
        name="Quiz:",
        icon_url="https://assets.leetcode.com/users/leetcode/avatar_1568224780.png",
    )
    embed.add_field(name=question.question, value="", inline=False)

    embed.add_field(
        name="Score", value=f"{SCORE_FOR_DIFFICULTY[question.difficulty]}", inline=True
    )

    embed.add_field(name="Question", value=f"{idx_quiz + 1}/{num_quiz}", inline=True)

    embed.add_field(name="Difficulty", value=question.difficulty, inline=True)

    embed.add_field(name="Topic", value=f"||{question.category}||", inline=True)

    embed.add_field(name="Question ID", value=question.id, inline=True)

    embed.add_field(name="Total point", value=f"{score}", inline=True)

    answer_view = ""
    if choice == -1:
        for i in range(len(answers)):
            answer_view += f"```\n{option_labels[i] + answers[i].answer}\n```"
    else:
        for i in range(len(answers)):
            if i == correct_answer:
                answer_view += f"```diff\n+{option_labels[i] + answers[i].answer}\n```"
                continue
            if i == choice:
                answer_view += f"```diff\n-{option_labels[i] + answers[i].answer}\n```"
                continue
            answer_view += f"```\n{option_labels[i] + answers[i].answer}\n```"

    embed.add_field(name="Answer", value=answer_view, inline=False)

    return embed


def create_result_embed(score, list_quiz, his_answer):
    embed = discord.Embed(color=0xFFFFFF)
    embed.set_author(
        name="Result",
        icon_url="https://assets.leetcode.com/users/leetcode/avatar_1568224780.png",
    )
    embed.add_field(name=f"Your score: {score}", value="", inline=False)
    for i in range(len(list_quiz)):
        if his_answer[i] == CANNOT_ANSWER or his_answer[i] == UNANSWERED:
            his_answer[i] = UNANSWERED
            result = Assets.red_tick + "Unanswered"
        elif his_answer[i] == list_quiz[i][0].correctAnswerId - list_quiz[i][1][0].id:
            result = Assets.green_tick + "Correct"
        else:
            result = Assets.red_tick + "Incorrect"
        embed.add_field(
            name=f"Question {i + 1}",
            value=f"Id: **{list_quiz[i][0].id}**\n"
            f"Topic: **{list_quiz[i][0].category}**\n"
            f"Difficulty: *{list_quiz[i][0].difficulty}*\n"
            f"Result: {result}\n",
            inline=False,
        )
    return embed


async def disable_all_quiz(view, interaction):
    view.disable_answers()
    view.end_quiz = True
    await interaction.edit_original_response(view=view)


class NavButton(discord.ui.Button["MultiQuizView"]):
    def __init__(
        self,
        button_type: int,
        style: discord.ButtonStyle,
        is_disabled: bool = False,
        emoji: typing.Union[str, discord.Emoji, discord.PartialEmoji, None] = None,
        label: str = None,
    ):
        super().__init__(style=style, label=label, disabled=is_disabled, emoji=emoji)
        self.button_type = button_type

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)
        if interaction.user != self.view.user:
            return
        if self.button_type == NEXT:
            if self.view.idx_quiz != len(self.view.list_quiz) - 1:
                self.view.idx_quiz = self.view.idx_quiz + 1
        elif self.button_type == PREV:
            if self.view.idx_quiz != 0:
                self.view.idx_quiz = self.view.idx_quiz - 1
        elif self.button_type == END:
            await interaction.followup.send(
                embed=create_result_embed(
                    self.view.score, self.view.list_quiz, self.view.answer_his
                )
            )
            for i in range(len(self.view.answer_his)):
                if self.view.answer_his[i] == UNANSWERED:
                    self.view.answer_his[i] = CANNOT_ANSWER
        choice = UNANSWERED
        if self.view.answer_his[self.view.idx_quiz] != UNANSWERED:
            choice = self.view.answer_his[self.view.idx_quiz]
        embed = create_embed(
            _question=self.view.list_quiz[self.view.idx_quiz][0],
            _answer=self.view.list_quiz[self.view.idx_quiz][1],
            score=self.view.score,
            idx_quiz=self.view.idx_quiz,
            num_quiz=len(self.view.list_quiz),
            choice=choice,
        )
        view = MultiQuizView(
            list_quiz=self.view.list_quiz,
            idx_quiz=self.view.idx_quiz,
            score=self.view.score,
            end_quiz=self.view.end_quiz,
            answer_his=self.view.answer_his,
            user=self.view.user,
        )
        await interaction.edit_original_response(embed=embed, view=view)


class AnswerButton(discord.ui.Button["MultiQuizView"]):
    def __init__(
        self,
        button_type: int,
        is_correct: bool,
        style: discord.ButtonStyle,
        is_disabled: bool = False,
        emoji: typing.Union[str, discord.Emoji, discord.PartialEmoji, None] = None,
        label: str = None,
    ):
        super().__init__(style=style, label=label, disabled=is_disabled, emoji=emoji)
        self.button_type = button_type
        self.is_correct = is_correct

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)
        if interaction.user != self.view.user:
            return
        self.view.answer_his[self.view.idx_quiz] = self.button_type
        embed = create_embed(
            _question=self.view.list_quiz[self.view.idx_quiz][0],
            _answer=self.view.list_quiz[self.view.idx_quiz][1],
            score=self.view.score
            + SCORE_FOR_DIFFICULTY[
                self.view.list_quiz[self.view.idx_quiz][0].difficulty
            ]
            if self.is_correct
            else self.view.score,
            idx_quiz=self.view.idx_quiz,
            num_quiz=len(self.view.list_quiz),
            choice=self.button_type,
        )
        if self.is_correct:
            embed.add_field(
                name="You're correct !!!",
                value="Found an error in this question? Please, let us know in <#1085444549666680906>!",
                inline=False,
            )
            self.view.score = (
                self.view.score
                + SCORE_FOR_DIFFICULTY[
                    self.view.list_quiz[self.view.idx_quiz][0].difficulty
                ]
            )
        else:
            embed.add_field(
                name="Wrong! You chose "
                + option_labels[self.button_type]
                + " But the correct answer is ",
                value="Found an error in this question? Please, let us know in <#1085444549666680906>!",
                inline=False,
            )

        self.view.disable_answers()
        await interaction.edit_original_response(embed=embed, view=self.view)


class MultiQuizView(discord.ui.View):
    children: typing.List[typing.Union[NavButton, AnswerButton]]

    def __init__(
        self,
        list_quiz: list,
        idx_quiz: int,
        score: int,
        end_quiz,
        answer_his=None,
        user=None,
    ):
        super().__init__()
        if answer_his is None:
            answer_his = [-1 for _ in range(len(list_quiz))]
        self.list_quiz = list_quiz
        self.idx_quiz = idx_quiz
        self.score = score
        self.answer_his = answer_his
        self.user = user
        self.end_quiz = end_quiz

        self.add_item(
            NavButton(
                button_type=PREV, style=discord.ButtonStyle.blurple, label="< Prev"
            )
        )
        self.add_item(
            NavButton(
                button_type=NEXT, style=discord.ButtonStyle.blurple, label="Next >"
            )
        )

        for i in range(len(self.list_quiz[self.idx_quiz][1])):
            self.add_item(
                AnswerButton(
                    button_type=i,
                    is_correct=(
                        i
                        == self.list_quiz[self.idx_quiz][0].correctAnswerId
                        - self.list_quiz[self.idx_quiz][1][0].id
                    ),
                    style=discord.ButtonStyle.gray,
                    is_disabled=False,
                    emoji=choice_emojis[i],
                )
            )

        self.add_item(
            NavButton(
                button_type=END, style=discord.ButtonStyle.green, label="End Quiz"
            )
        )

        if (
            self.answer_his[self.idx_quiz] != UNANSWERED
            or self.answer_his[self.idx_quiz] == CANNOT_ANSWER
            or self.end_quiz
        ):
            self.disable_answers()

        self.adjust_nav_button()

    def disable_answers(self):
        for i in range(2, 2 + len(self.list_quiz[self.idx_quiz][1])):
            self.children[i].disabled = True

    def adjust_nav_button(self):
        if self.idx_quiz == 0:
            self.children[0].disabled = True
        elif self.idx_quiz == len(self.list_quiz) - 1:
            self.children[1].disabled = True


class Quiztest(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.test_bank = {}

    @app_commands.command(name="quiz-test", description="Get some easy test")
    @app_commands.choices(
        nums_of_quiz=[
            app_commands.Choice(name="5", value=5),
            app_commands.Choice(name="10", value=10),
            app_commands.Choice(name="15", value=15),
        ]
    )
    async def _quiz_test(
        self, interaction: discord.Interaction, nums_of_quiz: app_commands.Choice[int]
    ):
        await interaction.response.defer(thinking=True)
        questions = []
        question_ids = {}
        difficulties = [
            ("Easy", int(nums_of_quiz.value * 0.4)),
            ("Medium", int(nums_of_quiz.value * 0.3)),
            ("Hard", nums_of_quiz.value - int(nums_of_quiz.value * 0.7)),
        ]
        for difficulty, num_quiz in difficulties:
            for _ in range(num_quiz):
                quiz = self.client.db_api.read_quiz({"difficulty": difficulty})
                while quiz[0].id in question_ids:
                    quiz = self.client.db_api.read_quiz({"difficulty": difficulty})
                question_ids[quiz[0].id] = True
                questions.append(quiz)

        view = MultiQuizView(questions, 0, 0, False, None, interaction.user)
        embed = create_embed(
            _question=questions[0][0],
            _answer=questions[0][1],
            score=0,
            idx_quiz=0,
            num_quiz=len(questions),
            choice=UNANSWERED,
        )

        countdown_time = 5 * 60
        countdown_message = await interaction.followup.send(
            content=f"⏰ Time left: {countdown_time} seconds \n"
            f":warning: Warning: After answering the question, you cannot change your answer. \n"
            f":information: Information: Click next to go to the next question. \n",
            embed=embed,
            view=view,
        )
        for remaining in range(countdown_time, 0, -1):
            await asyncio.sleep(1)
            await countdown_message.edit(
                content=f"⏰ Time left: {remaining} seconds \n"
                f":warning: Warning: After answering the question, you cannot change "
                f"your answer. \n"
                f":information: Information: Click next to go to the next question. \n",
            )

        await countdown_message.edit(content="⏰ Time's up!")
        await disable_all_quiz(view, interaction)


async def setup(client):
    await client.add_cog(
        Quiztest(client), guilds=[discord.Object(id=client.config["serverId"])]
    )
