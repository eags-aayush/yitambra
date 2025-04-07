import discord
from discord import app_commands
from discord.ext import commands

class ServerIcon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="icon", description="Get the server's profile picture")
    async def server_icon(self, interaction: discord.Interaction):
        if not interaction.guild.icon:
            await interaction.response.send_message("This server has no icon!", ephemeral=True)
            return

        embed = discord.Embed(title=f"{interaction.guild.name}'s Icon", color=0x000000)
        embed.set_image(url=interaction.guild.icon.url)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerIcon(bot))
