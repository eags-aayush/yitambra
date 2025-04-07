import discord
from discord import app_commands
from discord.ext import commands

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="search", description="Search for all works by a specific creator in the Leaks forum.")
    async def search(self, interaction: discord.Interaction, creator: discord.Member):
        leaks_forum = discord.utils.get(interaction.guild.channels, name="leaks", type=discord.ChannelType.forum)
        if not leaks_forum:
            await interaction.response.send_message("❌ The Leaks forum channel was not found.", ephemeral=True)
            return

        posts = []
        async for thread in leaks_forum.archived_threads(limit=100):  # Fetch archived threads
            if thread.owner_id == creator.id:
                posts.append((thread.name, thread.jump_url))
        
        for thread in leaks_forum.threads:  # Fetch active threads
            if thread.owner_id == creator.id:
                posts.append((thread.name, thread.jump_url))

        if not posts:
            await interaction.response.send_message(f"❌ No works found for {creator.mention} in {leaks_forum.mention}.", ephemeral=True)
            return

        embed = discord.Embed(title=f"📌 Works of {creator.display_name}", color=0x000000)
        embed.set_thumbnail(url=creator.avatar.url if creator.avatar else interaction.guild.icon.url)
        embed.description = "\n".join([f"🔗 **[{title}]({url})**" for title, url in posts])
        embed.set_footer(text="Click on a title to view the original post.")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Search(bot))