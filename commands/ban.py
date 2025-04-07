import discord
from discord import app_commands
from discord.ext import commands
import re
import asyncio

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Ban a member temporarily or permanently")
    @app_commands.describe(member="The user to ban", duration="Ban duration (optional: 1m, 1h, 1d, etc.)")
    @app_commands.checks.has_permissions(ban_members=True)  # Ensure only authorized users can use it
    async def ban_member(self, interaction: discord.Interaction, member: discord.Member, duration: str = None):
        """
        Slash Command Usage:
        - /ban member:<@user> → Permanently bans the user
        - /ban member:<@user> duration:1h → Temporarily bans the user for 1 hour
        """
        # Check bot permissions
        if not interaction.guild.me.guild_permissions.ban_members:
            return await interaction.response.send_message("❌ I don't have permission to ban members.", ephemeral=True)

        # Moderator role check (optional, can be removed)
        mod_role = discord.utils.get(interaction.guild.roles, name="Moderator")
        if mod_role and mod_role.position >= interaction.user.top_role.position:
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)

        # If no duration is provided, ban permanently
        if duration is None:
            try:
                await member.ban(reason="Permanent ban by bot.")
                await interaction.response.send_message(f"✅ {member.mention} has been permanently banned.")
            except discord.Forbidden:
                await interaction.response.send_message("❌ I don't have permission to ban this member.", ephemeral=True)
            return

        # Parse duration (e.g., "1h", "30m", "2d")
        time_pattern = re.compile(r'(\d+)([smhd])')
        matches = time_pattern.findall(duration.lower())

        if not matches:
            return await interaction.response.send_message("❌ Invalid duration format! Use `1h`, `30m`, `2d`, etc.", ephemeral=True)

        # Convert duration to seconds
        ban_duration = 0
        for time_value, time_unit in matches:
            if time_unit == 's':
                ban_duration += int(time_value)
            elif time_unit == 'm':
                ban_duration += int(time_value) * 60
            elif time_unit == 'h':
                ban_duration += int(time_value) * 3600
            elif time_unit == 'd':
                ban_duration += int(time_value) * 86400  # 86400 seconds in a day

        # Temporarily ban the member
        try:
            await member.ban(reason=f"Temporary ban for {duration} by bot.")
            await interaction.response.send_message(f"✅ {member.mention} has been banned for `{duration}`.")

            # Unban the user after the specified duration
            await asyncio.sleep(ban_duration)
            await interaction.guild.unban(member)
            await interaction.followup.send(f"🔓 {member.mention} has been unbanned after `{duration}`.")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to ban this member.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error banning member: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ban(bot))
