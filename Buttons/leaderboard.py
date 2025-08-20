import discord
from config import MAIN_COLOR
class Paginator(discord.ui.View):
    def __init__(self, pages: list, msg_id: int, interaction):
        super().__init__(timeout=300)
        self.current_page = 0
        self.msg_id = msg_id
        self.pages = pages
        self.interaction = interaction
        self.message = None

    async def update_page(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = False
        if self.current_page == 0:
            self.previous_button.disabled = True
        if self.current_page == len(self.pages) - 1:
            self.next_button.disabled = True

        dt = discord.utils.utcnow()
        embed = discord.Embed(title="**🏆 Leaderboard of top 50 Shard holders!!**",
                              description=self.pages[self.current_page], color=MAIN_COLOR)
        embed.set_image(url="https://imgur.com/1ViskLR.png")
        embed.set_footer(text=f'Page: {self.current_page+1}', icon_url=self.interaction.user.display_avatar.url)
        embed.timestamp = dt
        self.message = await self.interaction.followup.edit_message(embed=embed, view=self, message_id=self.msg_id)

    @discord.ui.button(label="Previous Page", style=discord.ButtonStyle.green)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_page()

    @discord.ui.button(label="Next Page", style=discord.ButtonStyle.green)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.update_page()

    async def on_timeout(self):
        await self.message.edit(content="⏰ **Time's up! You took longer than 5 minutes.**", embed=None, view=None)
        self.stop()

