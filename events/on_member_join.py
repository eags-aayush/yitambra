import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Sends a welcome message when a new member joins the server.
        - Sends a message in the "welcome" channel.
        - Attempts to send a direct message to the user.
        """
        welcome_channel_name = "welcome"
        welcome_channel = discord.utils.get(member.guild.text_channels, name=welcome_channel_name)

        # Send welcome message in the designated channel
        if welcome_channel:
            await welcome_channel.send(f"🎉 Welcome to **{member.guild.name}**, {member.mention}! We're happy to have you here. 🎊")

        # Attempt to send a direct message to the user
        try:
            await member.send(f"👋 Welcome to **{member.guild.name}**! We're glad to have you here. Have a great time!")
        except discord.Forbidden:
            print(f"⚠️ Could not send a DM to {member.name}.")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
