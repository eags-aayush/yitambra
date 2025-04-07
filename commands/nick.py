import discord
from discord import app_commands
from discord.ext import commands

class Nick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nick", description="Change a user's nickname")
    @app_commands.describe(member="The member whose nickname you want to change", nickname="The new nickname (optional)")
    async def change_nickname(self, interaction: discord.Interaction, member: discord.Member = None, nickname: str = None):
        """
        Slash command: /nick member:<@user> nickname:<text>
        - Member is optional (defaults to the user)
        - Nickname is optional (if not provided, resets nickname)
        """
        if member is None:
            member = interaction.user  # Default to command user

        try:
            if nickname:
                await member.edit(nick=nickname)
                await interaction.response.send_message(f"✅ {member.mention}'s nickname changed to `{nickname}`!", ephemeral=True)
            else:
                await member.edit(nick=None)  # Reset nickname
                await interaction.response.send_message(f"🔄 {member.mention}'s nickname has been reset.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to change nicknames!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Nick(bot))
