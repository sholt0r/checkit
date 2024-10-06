#!/usr/local/bin/python3.12

import os
import logging
import discord
from discord.ext import commands
from lwapi import lqa, hta

_log = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()

# Bot constants
D_TOKEN = os.getenv('D_TOKEN')
S_TOKEN = os.getenv('S_TOKEN')
S_API_URL = os.getenv('S_API_URL')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='ficsit ', intents=intents)

@bot.event
async def on_ready():
    _log.info(f"Logged on as {bot.user} (ID: {bot.user.id})")

@bot.hybrid_command()
async def status(ctx):
    _log.debug("Status command issued.")
    lstate = lqa.poll_server_state(f"{S_API_URL}")
    status = hta.send_http_request(S_API_URL, S_TOKEN, "QueryServerState")
    if not status:
        await ctx.send(f"The server state currently {lstate}")
        return
    await ctx.send(f"Active Session: {status['activeSessionName']}\nNumber of Players: {status['numConnectedPlayers']}/{status['playerLimit']}\nTech Tier: {status['techTier']}")

@bot.hybrid_command()
async def lstatus(ctx):
    _log.debug("Lightweight status command issued.")
    lstate = lqa.poll_server_state(f"{S_API_URL}")
    await ctx.send(f"The server state currently \"{lstate['state']}\"")

@bot.hybrid_command()
async def restart(ctx):
    _log.debug("Restart command issued.")
    lstate = lqa.poll_server_state(f"{S_API_URL}")
    restart = hta.send_http_request(S_API_URL, S_TOKEN, "Shutdown")
    if not restart:
        await ctx.send(f"The server state currently {lstate}")
        return
    await ctx.send("Restarting server.")

bot.run(f"{D_TOKEN}")