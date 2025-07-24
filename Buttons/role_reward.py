import discord
from database import claim_role_reward

class RoleSelect(discord.ui.Select):
    def __init__(self, roles: dict):
        options = [discord.SelectOption(label=name[0], value=role_id) for role_id, name in roles.items()]
        super().__init__(placeholder="Choose a role to claim...", options=options)
        self.roles = roles

    async def callback(self, interaction: discord.Interaction):
        role_id= str(self.values[0])
        result = await claim_role_reward(interaction.user.id, role_id)
        embed = discord.Embed(
            description=f"**{result['message']}**",
            color=result['color']
        )
        await interaction.response.edit_message(embed=embed, view=None)

class RoleView(discord.ui.View):
    def __init__(self, roles: dict):
        super().__init__(timeout=None)
        self.add_item(RoleSelect(roles))