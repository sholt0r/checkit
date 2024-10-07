[![Dockerhub Build/Push](https://github.com/sholt0r/checkit/actions/workflows/main.yml/badge.svg)](https://github.com/sholt0r/checkit/actions/workflows/main.yml)

# Discord Bot - Satisfactory Server Manager

This is a Python-based Discord bot designed to manage and interact with a Satisfactory server via API commands. The bot can display the server status and issue restart commands directly from a Discord server.

## Installation

Run with docker or use the compose file

```shell
docker run -d -e D_TOKEN='discord token' -e S_TOKEN='satisfactory token' -e S_API_URL='https://[server.url]:[port]/api/v1' --name checkit sholt0r/checkit
```

## Commands

- `ficsit status`: Retrieves the current server status and displays the following information:
  - Active Session Name
  - Number of Players Connected
  - Tech Tier

- `ficsit restart`: Restarts the server.

## Environment Variables

- `D_TOKEN`: The token for your Discord bot.
- `S_TOKEN`: The authorization token for the Satisfactory server API.
- `S_API_URL`: The URL for the Satisfactory server API.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
