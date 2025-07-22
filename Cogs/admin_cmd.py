import discord, config, captcha
from discord.ext import commands
from discord import app_commands
from Buttons.daily_check import CaptchaView
from Buttons.daily_quiz import QuizView
from Buttons.role_reward import RoleView
from database import get_daily_quiz, add_shards, remove_shards, get_user

class Checkin_button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Daily Check-in', style=discord.ButtonStyle.blurple, custom_id='ckn')
    async def checkin_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        msg = await interaction.followup.send(embed=discord.Embed(description="**Generating Captcha..**"), ephemeral=True)
        captcha_question, answers, correct_answer = captcha.generate_captcha()
        embed = discord.Embed(title="Solve this to claim you checkin reward!", description=f"• **{captcha_question}**", color=0x5bcff5)
        await interaction.followup.edit_message(embed=embed, view=CaptchaView(answers, correct_answer, msg), message_id=msg.id)

    @discord.ui.button(label='Daily Quiz', style=discord.ButtonStyle.blurple, custom_id='quiz')
    async def quiz_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        msg = await interaction.followup.send(embed=discord.Embed(description="**Preparing Question..**"), ephemeral=True)
        quiz_data = await get_daily_quiz(user_id=interaction.user.id)
        if quiz_data['success']:
            quizid = quiz_data['message']['_id']
            question = quiz_data['message']['question']
            options = quiz_data['message']['options']
            correct = quiz_data['message']['correct']
            embed = discord.Embed(title=f"Q: {question}", color=0x5bcff5)
            for key, answer_text in options.items():
                embed.add_field(name=f"• Option {key}", value=answer_text)
            await interaction.followup.edit_message(embed=embed, view=QuizView(answers=options, correct_answer=correct, quizid=quizid, msg=msg), message_id=msg.id)
        else:
            await interaction.followup.edit_message(embed=discord.Embed(description=quiz_data['message']), message_id=msg.id)
    
    @discord.ui.button(label='Claim Role reward', style=discord.ButtonStyle.blurple, custom_id='role')
    async def role_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(
            title="🎖️ Claim Your Role Reward",
            description="Pick your role from the dropdown to claim your reward! Just make sure the role is already in your profile so the system can verify it.",
            color=0x5bcff5
        )
        await interaction.followup.send(embed=embed, view=RoleView(config.ROLE_REWARD), ephemeral=True)

class Panel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def check(self, interaction):
        if [i for i in interaction.user.roles if i.id in config.RUNNER]:
            return True

    @app_commands.command(
        name="panel",
        description="provides the check-in, quiz & claim roles panel view."
    )
    @app_commands.describe(
        channel="channel where you want the view to be sent."
    )
    @app_commands.guild_only()
    async def check_in(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if await self.check(interaction):
            url = self.bot.user.display_avatar.url
            embed = discord.Embed(title="**🎉 Welcome to the Zenrock Daily Rewards Panel! 🎉**",
                                    description= "Check in daily, challenge your mind with Zenrock-themed quiz questions, and earn Spartan Shards – collect exclusive rewards for community roles! 🛡️⚔️\n\n**💠 How to Participate:**\n- ✅ Daily Check-In – Earn Spartan Shards every day you show up!\n- 🧠 Zenrock Quiz – Test your knowledge and earn bonus shards.\n- 🎖️ Role-Based Rewards – The higher your role, the more you earn!\n🔓 Climb the Ranks. Stack Your Shards. Claim Your Glory.",
                                    color=0x060f42)
            embed.set_thumbnail(url=url)
            embed.set_image(url="https://i.imgur.com/1ViskLR.png")
            await channel.send(embed=embed, view=Checkin_button())
            await interaction.response.send_message(f"**Check-in view is sent to {channel.mention} channel.**", ephemeral=True)
    
    @app_commands.command(
        name="add_shard",
        description="Add the number of Shards to a mentioned user."
    )
    @app_commands.describe(
        user="User to recieve the shards.",
        shards="Number of shards to be added."
    )
    @app_commands.guild_only()
    async def add_shard(self, interaction: discord.Interaction, user: discord.Member, shards: int):
        await interaction.response.defer(thinking=True)
        if await self.check(interaction):
            data = await add_shards(user.id, shards)
            dt = discord.utils.utcnow()
            embed = discord.Embed(description=f"> • **{data['message']}**", color=0x4FEB28)
            embed.set_footer(icon_url=self.bot.user.avatar.url)
            embed.timestamp = dt
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(content="> **Only server admins can run this command!**", ephemeral=True)
    
    @app_commands.command(
        name="remove_shard",
        description="Remove the number of Shards from a mentioned user."
    )
    @app_commands.describe(
        user="User from whom the shards will be removed.",
        shards="Number of shards to be removed."
    )
    @app_commands.guild_only()
    async def remove_shard(self, interaction: discord.Interaction, user: discord.Member, shards: int):
        await interaction.response.defer(thinking=True)
        if await self.check(interaction):
            data = await remove_shards(user.id, shards)
            dt = discord.utils.utcnow()
            embed = discord.Embed(description=f"> • **{data['message']}**", color=0x4FEB28)
            embed.set_footer(icon_url=self.bot.user.avatar.url)
            embed.timestamp = dt
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(content="> **Only server admins can run this command!**", ephemeral=True)
    
    @app_commands.command(
        name="user_details",
        description="Get details of a user from the database."
    )
    @app_commands.describe(
        user="User to fetch details for.",
    )
    @app_commands.guild_only()
    async def user_details(self, interaction: discord.Interaction, user: discord.Member=None):
        await interaction.response.defer(thinking=True)
        if await self.check(interaction):
            if user:
                data = await get_user(userid=user.id)
            else:
                data = await get_user(userid=interaction.user.id)
            
            if data['success']:
                username = data['message']['username']
                userid = data['message']['userid']
                shards = data['message']['shards']
                role_shards = data['message']['role_shards']

                roles = list(data['message']['roles'].keys())
                roles_formatted = "||".join([f"<@&{str(role_id)}>" for role_id in roles])
                total_quiz_played = data['message']['quiz_data']['total_quizzes']
                total_check_ins = data['message']['checkin_data']['total_checkins']

                dt = discord.utils.utcnow()
                embed = discord.Embed(title="User details!",
                                      description=f"\
                                        > • **User:** <@{userid}>\n\
                                        > • **Username:** {username}\n\
                                        > • **Userid:** {userid}\n\
                                        > • **Shards Balance:** {shards + role_shards}\n\
                                        > • **User Roles:** {roles_formatted if roles else None}\n\
                                        > • **Total Quizzes Played:** {total_quiz_played}\n\
                                        > • **Total Checkins Done:** {total_check_ins}",
                                        color=0x4FEB28)
                embed.set_footer(icon_url=self.bot.user.avatar.url)
                embed.timestamp = dt
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(content=f"> **{data['message']}**", ephemeral=True)
        else:
            await interaction.followup.send(content="> **Only server admins can run this command!**", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Panel(bot))
