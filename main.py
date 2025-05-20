import discord
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
ALLOWED_GUILD_IDS = os.getenv('ALLOWED_GUILD_IDS').split(',')
SUPABASE_URL = os.getenv('SUPABASE_URL')  # e.g., https://your-project.supabase.co
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
TRACKED_CATEGORY_IDS = [1351223065354178722,1192874281365934080]  # You can add more category IDs here

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)

def get_member_id(discord_username):
    """Fetch the member.id from the members table based on discord_username."""
    url = f"{SUPABASE_URL}/rest/v1/members?discord_username=eq.{discord_username}&select=id"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        return response.json()[0]['id']
    else:
        print(f"[❌] Member not found for username: {discord_username}")
        return None

def increment_discord_points(member_id, increment=1):
    """Update member_stat table to increment discord_points for given member_id."""
    url = f"{SUPABASE_URL}/rest/v1/member_stats?member_id=eq.{member_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    # Fetch current discord_points
    get_points = requests.get(url + "&select=discord_points", headers=headers)
    if get_points.status_code != 200 or not get_points.json():
        print(f"[❌] No member_stat found for member_id: {member_id}")
        return

    current_points = get_points.json()[0]['discord_points'] or 0
    new_points = current_points + increment

    # Patch with updated points
    payload = { "discord_points": new_points }
    response = requests.patch(url, json=payload, headers=headers)

    if response.status_code in [200, 204]:
        print(f"[✅] Updated discord_points for member_id {member_id}: {new_points}")
    else:
        print(f"[❌] Failed to update points: {response.text}")

@client.event
async def on_ready():
    print(f"[🚀] Logged in as {client.user} (ID: {client.user.id})")

@client.event
async def on_message(message):
    if message.author.bot or str(message.guild.id) not in ALLOWED_GUILD_IDS:
        return

    if message.channel.category_id not in TRACKED_CATEGORY_IDS:
        return

    discord_username = str(message.author)
    member_id = get_member_id(discord_username)
    if member_id:
        increment_discord_points(member_id, increment=1)

client.run(TOKEN)
