#!/usr/local/bin/python3.12

import os
import discord
from discord.ext import commands
import requests as re
import lqa.lqa as lqa

d_token = os.getenv('D_TOKEN')
s_token = os.getenv('S_TOKEN')
s_api_url = os.getenv('S_API_URL')

def sendRequest(api_url, token, s_func):
    headers = {"Content-Type":"application/json", "Authorization":f"Bearer {token}"}
    json = {"function":f"{s_func}"}
    try:
        response = re.post(api_url, headers=headers, json=json)
        if response.status_code not in (200, 204):
            return False
        if s_func == "QueryServerState":
            return response.json()['data']['serverGameState']
        if s_func == "Shutdown":
            return True
    except:
        return False

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='ficsit ', intents=intents)

@bot.event
async def on_ready():
    print(f"Logged on as {bot.user} (ID: {bot.user.id})")

@bot.hybrid_command()
async def status(ctx):
    print("Status command issued.")
    status = sendRequest(s_api_url, s_token, "QueryServerState")
    if not status:
        lstate = lqa.poll_server_state(f"S_API_URL")
        await ctx.send(f"The server state currently {lstate['state']}")
        return
    await ctx.send(f"Active Session: {status['activeSessionName']}\nNumber of Players: {status['numConnectedPlayers']}/{status['playerLimit']}\nTech Tier: {status['techTier']}")

@bot.hybrid_command()
async def restart(ctx):
    print("Restart command issued.")
    restart = sendRequest(s_api_url, s_token, "Shutdown")
    if not restart:
        lstate = lqa.poll_server_state(f"S_API_URL")
        await ctx.send(f"The server state currently {lstate['state']}")
        return
    await ctx.send("Restarting server.")

bot.run(f"{d_token}")