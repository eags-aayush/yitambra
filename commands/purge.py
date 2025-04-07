import discord
from discord import app_commands
from discord.ext import commands

class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="purge", description="Delete a specified number of messages")
    @app_commands.describe(amount="Number of messages to delete")
    @app_commands.checks.has_permissions(manage_messages=True)  # Ensure only authorized users can use it
    async def purge_msg(self, interaction: discord.Interaction, amount: int):
        """
        Slash Command Usage:
        - /purge amount:10 → Deletes the specified number of messages
        """
        # Check if the amount is a valid number and greater than 0
        if amount <= 0:
            return await interaction.response.send_message("❌ Please specify a number greater than 0.", ephemeral=True)

        # Check if the bot has permission to manage messages
        if not interaction.guild.me.guild_permissions.manage_messages:
            return await interaction.response.send_message("❌ I don't have permission to delete messages in this channel.", ephemeral=True)

        # Check if the user has the 'Moderator' role or a higher role
        moderator_role = discord.utils.get(interaction.guild.roles, name="Moderator")
        if moderator_role and moderator_role.position >= interaction.user.top_role.position:
            return await interaction.response.send_message("❌ You don't have the required role to use this command.", ephemeral=True)

        # Purge the specified number of messages
        try:
            deleted = await interaction.channel.purge(limit=amount + 1)  # +1 to include the command itself
            await interaction.response.send_message(f"✅ Deleted {len(deleted) - 1} messages.", ephemeral=True)  # -1 to not count the command message
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to delete messages in this channel.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"❌ Error while deleting messages: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Purge(bot))
