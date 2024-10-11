import os
import sys
import logging
import discord
import asyncio
from discord.ext import commands
from common import hta, lqa, log

# Constants
D_TOKEN = os.getenv('D_TOKEN')
S_TOKEN = os.getenv('S_TOKEN')
HOST = os.getenv('S_API_HOST')
PORT = os.getenv('S_PORT', 7777)

logger = log.setup_logger()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='ficsit ', intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Logged on as {bot.user} (ID: {bot.user.id})")

@bot.hybrid_command()
async def status(ctx):
    logger.info("Status command issued.")
    if not status:
        await ctx.send(f"The server is not responding")
        return
    await ctx.send(f"Active Session: {status['activeSessionName']}\nNumber of Players: {status['numConnectedPlayers']}/{status['playerLimit']}\nTech Tier: {status['techTier']}")

@bot.hybrid_command()
async def restart(ctx):
    logger.info("Restart command issued.")
    if not restart:
        await ctx.send(f"The server is not responding")
        return
    await ctx.send("Restarting server.")

bot.run(f"{D_TOKEN}")