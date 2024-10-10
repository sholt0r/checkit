import os
import sys
import logging
import discord
from discord.ext import commands
from lwapi import hta#, lqa

# Constants
D_TOKEN = os.getenv('D_TOKEN')
S_TOKEN = os.getenv('S_TOKEN')
S_API_URL = os.getenv('S_API_URL')
LOGGER_NAME = "checkit"

handler = logging.StreamHandler()
formatter = discord.utils._ColourFormatter()
logger = logging.getLogger(LOGGER_NAME)
handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='ficsit ', intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Logged on as {bot.user} (ID: {bot.user.id})")

@bot.hybrid_command()
async def status(ctx):
    logger.info("Status command issued.")
    #lstate = lqa.poll_server_state(f"{S_API_URL}", logger)
    status = hta.send_http_request(S_API_URL, S_TOKEN, "QueryServerState", LOGGER_NAME)
    if not status:
        #await ctx.send(f"The server state currently {lstate}")
        await ctx.send(f"The server is not responding")
        return
    await ctx.send(f"Active Session: {status['activeSessionName']}\nNumber of Players: {status['numConnectedPlayers']}/{status['playerLimit']}\nTech Tier: {status['techTier']}")

@bot.hybrid_command()
async def restart(ctx):
    logger.info("Restart command issued.")
    #lstate = lqa.poll_server_state(f"{S_API_URL}", logger)
    restart = hta.send_http_request(S_API_URL, S_TOKEN, "Shutdown", LOGGER_NAME)
    if not restart:
        #await ctx.send(f"The server state currently {lstate}")
        await ctx.send(f"The server is not responding")
        return
    await ctx.send("Restarting server.")

bot.run(f"{D_TOKEN}")