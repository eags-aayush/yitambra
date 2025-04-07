import discord
import os
import re
import sqlite3
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

DOWNLOAD_LOG_CHANNEL_ID = int(os.getenv("DOWNLOAD_LOG_CHANNEL_ID"))  # Log channel ID
ALL_LEAKS_CHANNEL_ID = int(os.getenv("ALL_LEAKS_CHANNEL_ID"))  # All-leaks channel ID

VIP_ROLE_NAME = "VIP"  # Change this to your VIP role name

# Initialize SQLite database
conn = sqlite3.connect("downloads.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS downloads (
        item TEXT PRIMARY KEY,
        count INTEGER DEFAULT 0
    )
""")
conn.commit()

def is_valid_url(url):
    pattern = re.compile(r"^https?:\/\/.*\.(?:jpg|jpeg|png|gif)(\?.*)?$", re.IGNORECASE)
    return bool(pattern.match(url))

def has_vip_role(member: discord.Member):
    """Check if the user has the VIP role by name."""
    return any(role.name == VIP_ROLE_NAME for role in member.roles)

def increment_download_count(item):
    cursor.execute("INSERT INTO downloads (item, count) VALUES (?, 1) ON CONFLICT(item) DO UPDATE SET count = count + 1", (item,))
    conn.commit()

def get_download_count(item):
    cursor.execute("SELECT count FROM downloads WHERE item = ?", (item,))
    result = cursor.fetchone()
    return result[0] if result else 0

class LeakView(discord.ui.View):
    def __init__(self, author, title, download_url, message_link):
        super().__init__()
        self.author = author
        self.title = title
        self.download_url = download_url
        self.message_link = message_link

    @discord.ui.button(label="🔗 Download", style=discord.ButtonStyle.primary)
    async def download_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_vip_role(interaction.user):
            await interaction.response.send_message("❌ Only VIP members can download this file!", ephemeral=True)
            await log_download(interaction.user, "Leak", self.title, "Fail", reason="Only for VIP users")
            return

        increment_download_count(self.title)
        download_count = get_download_count(self.title)

        await interaction.response.send_message(f"🔗 [Download]({self.download_url})", ephemeral=True)
        await log_download(interaction.user, "Leak", self.title, "Success", download_count=download_count, message_url=self.message_link)

async def log_download(user, category, item, status, reason=None, download_count=None, message_url=""):
    log_channel = user.guild.get_channel(DOWNLOAD_LOG_CHANNEL_ID)
    if not log_channel:
        return

    color = 0x006400 if status == "Success" else 0xe74c3c  # Green for success, Red for failure
    embed = discord.Embed(title=f"{category} > [{item}]({message_url})", color=color)
    embed.add_field(name="User", value=user.mention, inline=False)
    embed.add_field(name="Status", value=status, inline=True)

    if status == "Fail" and reason:
        embed.add_field(name="Failure Reason", value=reason, inline=True)
    
    if status == "Success" and download_count is not None:
        embed.add_field(name="Download Count", value=str(download_count), inline=True)

    await log_channel.send(embed=embed)

async def send_leak(interaction, title, download_url, image_url, purchase_url, category):
    if not is_valid_url(image_url):
        await interaction.response.send_message("Invalid image URL! Provide a direct link to a .jpg, .png, or .gif image.", ephemeral=True)
        return

    embed = discord.Embed(title=title, url=image_url, color=0x000000)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    embed.set_image(url=image_url)
    if purchase_url:
        embed.add_field(name="Purchase URL", value=f"[Link]({purchase_url})", inline=False)
        embed.set_footer(text=f"Posted by {interaction.user.display_name}")
    
    message = await interaction.channel.send(embed=embed, view=LeakView(interaction.user.mention, title, download_url, interaction.channel.jump_url))

    all_leaks_channel = interaction.client.get_channel(ALL_LEAKS_CHANNEL_ID)
    if all_leaks_channel:
        messages = [f"{title} - [Jump to Message]({message.jump_url})"]
        async for msg in all_leaks_channel.history(limit=100):
            messages.append(msg.content)
        messages.sort()
        await all_leaks_channel.purge()
        for msg in messages:
            await all_leaks_channel.send(msg)
    
    await interaction.response.send_message(f"{category} posted successfully!", ephemeral=True)
    await log_download(interaction.user, category, title, "Success", download_count=get_download_count(title), message_url=message.jump_url)

class LeakModal(discord.ui.Modal, title="Submit a Leak"):
    title_input = discord.ui.TextInput(label="Name of Preset/Scene Pack", required=True, max_length=100)
    purchase_url = discord.ui.TextInput(label="Place of Purchase (URL)", required=True, style=discord.TextStyle.short)
    download_url = discord.ui.TextInput(label="Download Path (URL)", required=True, style=discord.TextStyle.short)
    image_url = discord.ui.TextInput(label="Thumbnail URL (Optional)", required=False, style=discord.TextStyle.short)
    
    def __init__(self, category):
        super().__init__()
        self.category = category

    async def on_submit(self, interaction: discord.Interaction):
        await send_leak(
            interaction,
            title=self.title_input.value,
            download_url=self.download_url.value,
            image_url=self.image_url.value if self.image_url.value else "https://via.placeholder.com/150",
            purchase_url=self.purchase_url.value,
            category=self.category
        )

class LeakCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leak")
    async def leak(self, interaction: discord.Interaction):
        await interaction.response.send_modal(LeakModal(category="Leak"))

    @app_commands.command(name="scenepack")
    async def scenepack(self, interaction: discord.Interaction):
        await interaction.response.send_modal(LeakModal(category="Scene Pack"))

async def setup(bot):
    if bot.get_cog("LeakCommands"):
        await bot.remove_cog("LeakCommands")  # Unload if already loaded
    await bot.add_cog(LeakCommands(bot))