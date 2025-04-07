import discord
from discord import app_commands
from discord.ext import commands

class RoleManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="role", description="Assign or remove roles for a user")
    @app_commands.describe(member="The user to modify the role", role="The role to assign or remove")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def role_assign(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role = None):
        """
        Slash Command Usage:
        - /role member:<@user> role:<role> → Assigns the specified role to the user
        - /role member:<@user> → Removes all roles (except @everyone) from the user
        """
        # Check if the user has a role higher than "Moderator"
        author_top_role = interaction.user.top_role
        moderator_role = discord.utils.get(interaction.guild.roles, name="Moderator")

        if moderator_role is None:
            return await interaction.response.send_message("❌ The 'Moderator' role does not exist in this server.", ephemeral=True)

        if author_top_role <= moderator_role:
            return await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)

        if role is None:
            # If no role is specified, remove all roles (except @everyone)
            try:
                roles_to_remove = [r for r in member.roles if r != interaction.guild.default_role]
                await member.remove_roles(*roles_to_remove)
                await interaction.response.send_message(f"✅ All roles have been removed from {member.mention}.")
            except discord.Forbidden:
                await interaction.response.send_message("❌ I do not have permission to remove roles for this user.", ephemeral=True)
            except discord.HTTPException as e:
                await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)
            return

        # Check if the bot has permission to assign this role
        if interaction.guild.me.top_role <= role:
            return await interaction.response.send_message("❌ I do not have permission to assign this role.", ephemeral=True)

        try:
            # Add the role to the member
            await member.add_roles(role)
            await interaction.response.send_message(f"✅ Successfully assigned the role '{role.name}' to {member.mention}.")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I do not have permission to modify roles for this user.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleManagement(bot))