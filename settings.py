import os
from dotenv import load_dotenv


load_dotenv()

DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")
SNUSBASE_API_SECRET = os.getenv("SNUSBASE_API_TOKEN")
