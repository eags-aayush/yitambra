# app.py

from flask import Flask, send_file
import threading
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

# Load .env (only useful locally)
load_dotenv()

# Flask app for index.html
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return send_file("index.html")

def run_web():
    web_app.run(host="0.0.0.0", port=3000)

# Start Flask server in a separate thread
threading.Thread(target=run_web).start()

# Setup Discord bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user.name} is online!")
    try:
        await bot.tree.sync()
        print(f"✅ Slash commands synced!")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

async def load_cogs():
    base_path = os.path.dirname(os.path.abspath(__file__))
    for folder in ["commands", "events"]:
        folder_path = os.path.join(base_path, folder)
        if not os.path.exists(folder_path):
            print(f" ❌ Folder not found: {folder_path}")
            continue
        for filename in os.listdir(folder_path):
            if filename.endswith(".py") and filename != "__init__.py":
                extension = f"{folder}.{filename[:-3]}"
                try:
                    await bot.load_extension(extension)
                    print(f" ✅ Loaded {extension}")
                except Exception as e:
                    print(f" ❌ Failed to load {extension}: {e}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("DISCORD_BOT_TOKEN"))

asyncio.run(main())
