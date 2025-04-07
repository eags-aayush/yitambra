import discord
from discord import app_commands
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unban", description="Unban a member from the server")
    @app_commands.describe(member="The user to unban (User ID)")
    @app_commands.checks.has_permissions(ban_members=True)  # Ensure the user has permission to unban members
    async def unban(self, interaction: discord.Interaction, member: str):
        """
        Slash Command Usage:
        - /unban member:<User ID> → Unbans the specified user by their User ID
        """

        try:
            # Convert member string to an integer (User ID)
            member_id = int(member)

            # Fetch the list of banned users
            banned_users = [entry async for entry in interaction.guild.bans()]
            member_to_unban = None

            # Try to find the banned user by ID
            for banned_entry in banned_users:
                if banned_entry.user.id == member_id:
                    member_to_unban = banned_entry.user
                    break

            if member_to_unban is None:
                return await interaction.response.send_message(f"❌ User with ID '{member_id}' is not banned.", ephemeral=True)

            # Unban the member
            await interaction.guild.unban(member_to_unban)
            await interaction.response.send_message(f"✅ Successfully unbanned {member_to_unban.name} ({member_to_unban.id}).")
        
        except ValueError:
            await interaction.response.send_message("❌ Invalid User ID format. Please enter a valid numerical ID.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I do not have permission to unban members.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Unexpected error: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
