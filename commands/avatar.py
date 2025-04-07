import discord
from discord import app_commands
from discord.ext import commands

class AvatarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Get the profile picture of a user")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member):
        embed = discord.Embed(title=f"{member.display_name}'s Avatar", color=0x000000)
        embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AvatarCog(bot))