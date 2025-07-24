import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone
from database import add_remove_role, get_date,reset_daily_flags
from config import ROLE_REWARD

class EventCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_run_date = None
        self.daily_loop.start()
    
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.roles != after.roles:
            added_roles = [role for role in after.roles if role not in before.roles]
            removed_roles = [role for role in before.roles if role not in after.roles]

            if added_roles:
                for role in added_roles:
                    role_r = ROLE_REWARD.get(str(role.id), [])
                    if role_r:
                        reward = role_r[1]
                        data = await add_remove_role(user_id=after.id, role_id=str(role.id), reward=reward, remove=False)
                        print(data['message'])
            if removed_roles:
                for role in removed_roles:
                    role_r = ROLE_REWARD.get(str(role.id), [])
                    if role_r:
                        reward = role_r[1]
                        data = await add_remove_role(user_id=after.id, role_id=str(role.id), reward=reward, remove=True)
                        print(data['message'])

    def cog_unload(self):
        self.daily_loop.cancel()

    @tasks.loop(minutes=5)
    async def daily_loop(self):
        now_utc = datetime.now(timezone.utc).date().isoformat()
        self.last_run_date = await get_date()
        if self.last_run_date != now_utc:
            await get_date(set_date=now_utc)
            await self.run_daily_task()

    async def run_daily_task(self):
        data = await reset_daily_flags()
        print(data['message'])

    @daily_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(EventCog(bot))