import discord
from discord import app_commands
from discord.ext import commands

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(member="The user to kick", reason="The reason for the kick (optional)")
    @app_commands.checks.has_permissions(kick_members=True)  # Ensure only authorized users can use it
    async def kick_member(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """
        Slash Command Usage:
        - /kick member:<@user> → Kicks the user from the server
        - /kick member:<@user> reason:Some reason → Kicks the user with a specified reason
        """
        # Check bot permissions
        if not interaction.guild.me.guild_permissions.kick_members:
            return await interaction.response.send_message("❌ I don't have permission to kick members.", ephemeral=True)

        # Moderator role check (optional, can be removed)
        mod_role = discord.utils.get(interaction.guild.roles, name="Moderator")
        if mod_role and mod_role.position >= interaction.user.top_role.position:
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)

        # Ensure the target member is not higher or equal in role hierarchy
        if member.top_role.position >= interaction.user.top_role.position:
            return await interaction.response.send_message("❌ You cannot kick a member with a higher or equal role than you.", ephemeral=True)

        # Kick the member and send a confirmation message
        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"✅ Successfully kicked {member.mention}. Reason: {reason if reason else 'No reason provided.'}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to kick this member.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"❌ Error kicking member: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Kick(bot))
