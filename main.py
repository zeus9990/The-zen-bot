import discord, config
from discord.ext import commands
from Cogs.admin_cmd import Checkin_button
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
initial_extensions = [
    "Cogs.admin_cmd",
    "Cogs.user_cmd",
    "Cogs.event"
]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def setup_hook():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f'SUCCESS: Extension {extension} is loaded!')
        except Exception as e:
            print(f'ERROR: {e}')
    await bot.tree.sync()
    bot.add_view(Checkin_button())

bot.run(config.BOT_TOKEN)