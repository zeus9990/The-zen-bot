import discord
from database import submit_answer

class QuizView(discord.ui.View):
    def __init__(self, answers: dict, correct_answer: str, quizid: str, msg):
        super().__init__(timeout=120)
        self.correct_answer = correct_answer
        self.answers = answers
        self.msg = msg
        self.quiz_id = quizid

        for key, answer_text in self.answers.items():
            self.add_item(self.QuizButton(label=f"Option {key}", answer_text=answer_text))

    class QuizButton(discord.ui.Button):
        def __init__(self, label: str, answer_text: str):
            super().__init__(label=label, style=discord.ButtonStyle.blurple)
            self.answer_text = answer_text

        async def callback(self, interaction: discord.Interaction):
            view: QuizView = self.view
            data = await submit_answer(user_id=interaction.user.id, quiz_id=view.quiz_id, selected_answer=self.answer_text)
            embed = discord.Embed(description=f"{data['message']}", color=0x66FF00)
            await interaction.response.edit_message(embed=embed, view=None)

    async def on_timeout(self):
        try:
            await self.msg.edit(embed=discord.Embed(description="⏰ **Time's up! You took longer than 2 minutes.**", color=0xFF0000), view=None)
        except:
            pass