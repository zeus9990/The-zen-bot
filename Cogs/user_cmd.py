import discord
from discord.ext import commands
from discord import app_commands
from database import get_rank, get_leaderboard

class UserCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(
        name = "leaderboard",
        description = "Check leaderboard of top Shard holders."
    )
    @app_commands.guild_only()
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        data = await get_leaderboard(interaction.user.id)
        dt = discord.utils.utcnow()
        embed = discord.Embed(title="**🏆 Leaderboard of top 10 Shard holders!!**",
                              description=data, color=0x060f42)
        embed.set_image(url="https://imgur.com/1ViskLR.png")
        embed.set_footer(text= f'Today at', icon_url=self.bot.user.avatar.url)
        embed.timestamp = dt
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(
        name = "myrank",
        description = "Check Your individual rank and Shards."
    )
    @app_commands.guild_only()
    async def myrank(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        data = await get_rank(interaction.user.id)
        if data['success']:
            dt = discord.utils.utcnow()
            embed = discord.Embed(title=f"**Your server Rank: {data['message']['rank']}**",
                                description=f"> • **Username: `{data['message']['username']}`**\n> • **Total Shards: `{data['message']['shards']}`**", color=0x060f42)
            embed.set_footer(text= f'Today at', icon_url=self.bot.user.avatar.url)
            embed.timestamp = dt
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(content=f"> {data['message']}")

async def setup(bot):
    await bot.add_cog(UserCog(bot))
