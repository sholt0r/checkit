#!/usr/local/bin/python3.12

from dotenv import load_dotenv
import os
import requests as re

load_dotenv()
api_url = "https://ficsit.thebois.au:7777/api/v1"
token = os.getenv('S_TOKEN')
headers = {"Content-Type":"application/json", "Authorization":f"Bearer {token}"}
data = {"function": "QueryServerState"}
response = re.post(api_url, headers=headers, json=data)

if response.status_code == 204:
    print("No Content")
else:
    print(response.json()['data']['serverGameState']['activeSessionName'])