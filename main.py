import discord, config
from discord.ext import commands
from Cogs.admin_cmd import Button_class
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
initial_extensions = [
    "Cogs.admin_cmd",
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
    bot.add_view(Button_class())

bot.run(config.BOT_TOKEN)