import discord
from database import daily_checkin

class CaptchaView(discord.ui.View):
    def __init__(self, answers, correct_answer, msg):
        super().__init__(timeout=65)
        self.correct_answer = int(correct_answer)
        self.answers = list(map(int, answers))
        self.msg = msg
        for i in range(3):
            self.add_item(self.CaptchaButton(label=self.answers[i], index=i, view=self))

    class CaptchaButton(discord.ui.Button):
        def __init__(self, label, index, view):
            super().__init__(label=label, style=discord.ButtonStyle.blurple)
            self.index = index
            self.view_ref = view

        async def callback(self, interaction: discord.Interaction):
            view = self.view_ref
            if view.answers[self.index] == view.correct_answer:
                data = await daily_checkin(interaction.user.id, interaction.user.name)
                embed = discord.Embed(description=f"**{data['message']}**", color=0x66FF00)
            else:
                embed = discord.Embed(description=f"**Oops {interaction.user.mention}! Your answer was not correct. Try again!**", color=0xFF0000)
            await interaction.response.edit_message(embed=embed, view=None)

    async def on_timeout(self):
        try:
            await self.msg.edit(embed=discord.Embed(description="⏰ **Time's up! You took longer than 1 minute.**", color=0xFF0000), view=None)
        except:
            pass
