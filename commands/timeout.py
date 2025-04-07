import discord
from discord import app_commands
from discord.ext import commands
import re
import asyncio
from datetime import timedelta

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="timeout", description="Timeout a specified user for a set duration")
    @app_commands.describe(member="The user to timeout", duration="Duration of the timeout (e.g., 1m, 1h, 1d)", reason="Reason for the timeout (optional)")
    @app_commands.checks.has_permissions(moderate_members=True)  # Ensure only authorized users can use it
    async def timeout_member(self, interaction: discord.Interaction, member: discord.Member, duration: str = None, reason: str = None):
        """
        Slash Command Usage:
        - /timeout member:<@user> duration:1h → Timeouts the user for 1 hour
        - /timeout member:<@user> duration:1h reason:Spamming → Timeouts the user for 1 hour with a reason
        """
        # Check if the bot has permission to timeout members
        if not interaction.guild.me.guild_permissions.moderate_members:
            return await interaction.response.send_message("❌ I don't have the required permission to timeout members.", ephemeral=True)

        # Check if the user has the necessary role to execute the command
        moderator_role = discord.utils.get(interaction.guild.roles, name="Moderator")
        if moderator_role and moderator_role.position >= interaction.user.top_role.position:
            return await interaction.response.send_message("❌ You don't have the required role to use this command.", ephemeral=True)

        # If no duration is provided, show an error message
        if duration is None:
            return await interaction.response.send_message("❌ Please specify a valid duration (e.g., 1m, 30s, 1h, 2d).", ephemeral=True)

        # Parse the duration string (e.g., "1m", "2h", "30s")
        time_pattern = re.compile(r'(\d+)([smhd])')
        matches = time_pattern.findall(duration.lower())

        if not matches:
            return await interaction.response.send_message("❌ Please provide a valid duration (e.g., 1m, 30s, 2d).", ephemeral=True)

        # Convert the duration to seconds
        timeout_duration = 0
        for match in matches:
            time_value, time_unit = match
            if time_unit == 's':
                timeout_duration += int(time_value)
            elif time_unit == 'm':
                timeout_duration += int(time_value) * 60
            elif time_unit == 'h':
                timeout_duration += int(time_value) * 3600
            elif time_unit == 'd':
                timeout_duration += int(time_value) * 86400  # 86400 seconds in a day

        # Timeout the member temporarily for the given duration
        try:
            await member.timeout(timedelta(seconds=timeout_duration), reason=f"Timeout for {duration} by bot: {reason if reason else 'No reason provided.'}")
            await interaction.response.send_message(f"✅ {member.mention} has been timed out for `{duration}`.")
            
            # Set up a task to remove the timeout after the specified duration
            await asyncio.sleep(timeout_duration)  # Wait for the specified time duration
            await member.remove_timeout()  # Remove the timeout after the specified time
            await interaction.followup.send(f"🔓 {member.mention} has been removed from timeout after `{duration}`.")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to timeout this member.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"❌ Error while trying to timeout member: {e}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ An unexpected error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Timeout(bot))
