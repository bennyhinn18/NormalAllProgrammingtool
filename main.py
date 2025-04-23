import discord
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
ALLOWED_GUILD_IDS = os.getenv('ALLOWED_GUILD_IDS').split(',')
SUPABASE_URL = os.getenv('SUPABASE_FUNCTION_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)

def get_week_start():
    now = datetime.utcnow()
    return (now - timedelta(days=now.weekday())).date().isoformat()

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = str(message.guild.id)
    if guild_id not in ALLOWED_GUILD_IDS:
        return

    payload = {
        "user_id": str(message.author.id),
        "week": get_week_start()
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    try:
        res = requests.post(SUPABASE_URL, json=payload, headers=headers)
        if res.status_code != 200:
            print(f"Supabase error: {res.text}")
    except Exception as e:
        print(f"Error sending to Supabase: {e}")

client.run(TOKEN)
