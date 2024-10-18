import os, discord, asyncio, socket, struct, time, select
import requests as re
from discord.ext import commands
from common import log


# Bot Constants
D_TOKEN = os.getenv('D_TOKEN')
S_TOKEN = os.getenv('S_TOKEN')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT', 7777)


# LWAPI Constants
PROTOCOL_MAGIC = 0xF6D5
PROTOCOL_VERSION = 1
MESSAGE_TYPE_POLL = 0
MESSAGE_TYPE_RESPONSE = 1


class LWAResponse:
    def __init__(self, protocol_magic, message_type, protocol_version, response_cookie, server_state, server_net_cl, server_flags, num_sub_states):
        self.protocol_magic = protocol_magic
        self.message_type = message_type
        self.protocol_version = protocol_version
        self.cookie = response_cookie
        self.server_state = server_state
        self.server_net_cl = server_net_cl
        self.server_flags = server_flags
        self.num_sub_states = num_sub_states


class HTTPServerState:
    def __init__(self, host, token, port=7777):
        self.host = host
        self.port = port
        self.token = token

        self.url = f'https://{self.host}:{self.port}/api/v1'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}' 
        }

        self.update_local_state()

    def query_server_state(self):
        logger.info("Query server state.")
        json = {'function': 'QueryServerState'}
        response = re.post(self.url, headers=self.headers, json=json)
        if response.status_code not in (200, 204):
            logger.error(f"Status code {response.status_code}.")
            return
        return response.json()['data']['serverGameState']


    def restart_server(self):
        logger.info("Restarting server.")
        json = {'function': 'Shutdown'}
        re.post(self.url, self.headers, json)
        return True


    def update_local_state(self):
        logger.info("Updating local state.")
        self.local_state = self.query_server_state()
        self.active_session = self.local_state.get('activeSessionName')
        self.num_players = self.local_state.get('numConnectedPlayers')
        self.player_limit = self.local_state.get('playerLimit')
        self.tech_tier = self.local_state.get('techTier')


    def __repr__(self):
        return (f"Active Session: {self.active_session}\n"
                f"Number of Players: {self.active_session}/{self.player_limit}\n"
                f"Tech Tier: {self.tech_tier}")


def poll_server_state(host, port, poll_interval=0.05):
    server = (host, port)
    c_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    c_sock.setblocking(False)

    try:
        # Generate message with unique cookie
        cookie = int(time.time() * 1000)
        request_message = struct.pack('<HBBQ', PROTOCOL_MAGIC, MESSAGE_TYPE_POLL, PROTOCOL_VERSION, cookie) + b'\x01'

        c_sock.sendto(request_message, server)

        ready_to_read, _, _ = select.select([c_sock], [], [], poll_interval)

        if ready_to_read:
            response, _ = c_sock.recvfrom(1024)
            response_len = len(response)
            if response_len < 22:
                raise ValueError(f"Response too short: {response_len} bytes")
            
            header_format = '<HBBQBIQB'
            header_size = struct.calcsize(header_format)
            state = LWAResponse(*struct.unpack_from(header_format, response, 0))
            sub_states_size = state.num_sub_states * 3
            server_name_length_offset = header_size + sub_states_size
            server_name_length = struct.unpack_from('<H', response, server_name_length_offset)[0]

            if state.protocol_magic != PROTOCOL_MAGIC or state.message_type != MESSAGE_TYPE_RESPONSE or state.cookie != cookie:
                logger.error('Unexpected state or mismatched cookie.')

            if response_len < header_size + sub_states_size + 2:  # 2 bytes for server name length
                logger.error("Response does not contain enough data for sub-states or server name length")

            if response_len < server_name_length_offset + 2 + server_name_length:
                logger.error(f"Response too short to contain server name. Expected at least {server_name_length_offset + 2 + server_name_length}, got {response_len}")

            return response


    except asyncio.CancelledError:
        return False, "err_can"
    finally:
        c_sock.close()


async def track_state(host, http_server_state, port=7777, poll_interval=0.05):
    previous_state = None
    while True:
        state = poll_server_state(host, port)
        if previous_state is None:
            previous_state = state

        if state.num_sub_states != previous_state.num_sub_states:
            logger.info("State Updated")
            http_server_state.update_local_state()

        previous_state = state
        await asyncio.sleep(poll_interval)


logger = log.setup_logger()

http_server_state = HTTPServerState(HOST, S_TOKEN)
server_state = track_state(HOST, http_server_state)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='ficsit ', intents=intents)


@bot.event
async def on_ready():
    logger.info(f"Logged on as {bot.user} (ID: {bot.user.id})")


@bot.hybrid_command()
async def status(ctx):
    logger.info("Status command issued.")
    await ctx.send(f"Active Session: {http_server_state.active_session}\nNumber of Players: {http_server_state.num_players}/{http_server_state.player_limit}\nTech Tier: {http_server_state.tech_tier}")


@bot.hybrid_command()
async def restart(ctx):
    logger.info("Restart command issued.")
    await ctx.send("Restarting server.")

bot.run(f"{D_TOKEN}")
