import discord
from discord.ext import commands

class Farewell(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """
        Sends a farewell message when a member leaves the server.
        - Sends a message in the "leave" channel.
        - Attempts to send a direct message to the user.
        """
        leave_channel_name = "leave"
        leave_channel = discord.utils.get(member.guild.text_channels, name=leave_channel_name)

        # Send farewell message in the designated channel
        if leave_channel:
            await leave_channel.send(f"😢 **{member.mention}** we will remember your contribution! 💔")

        # Attempt to send a direct message to the user
        try:
            await member.send(f"We're sad to see you leave **{member.guild.name}**. Take care, and we hope to see you again!")
        except discord.Forbidden:
            print(f"⚠️ Could not send a farewell DM to {member.name}.")

async def setup(bot):
    await bot.add_cog(Farewell(bot))
