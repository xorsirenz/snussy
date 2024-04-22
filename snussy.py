import requests
import json
import settings
import discord
from discord import app_commands
from discord.ext import commands

snusbase_auth = settings.SNUSBASE_API_SECRET
snusbase_api = 'https://api-experimental.snusbase.com/'

logger = settings.logging.getLogger("bot")

def send_request(url, body=None):
    headers = {
        'Auth': snusbase_auth,
        'Content-Type': 'application/json',
        }
    method = 'POST' if body else 'GET'
    data = json.dumps(body) if body else None
    response = requests.request(
        method, snusbase_api + url, headers=headers, data=data)
    return response.json()


def run():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="/", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"{bot.user} is logging in")
        print("Please wait for commands to sync...")
        await bot.tree.sync()
        await bot.change_presence(
                activity=discord.activity.Game(name="with IEDs"),
                status=discord.Status.do_not_disturb)
        print("Slash commands synced\nSnussybot is ready\nLOGS:")

    @bot.tree.command(
            name="snussybot",
            description="search snusbase API",
            nsfw=True)
    @app_commands.checks.cooldown(1, 5.0)
    @app_commands.choices(lookup=[
        app_commands.Choice(name="email", value="email"),
        app_commands.Choice(name="hash", value="hash"),
        app_commands.Choice(name="lastip", value="lastip"),
        app_commands.Choice(name="name", value="name"),
        app_commands.Choice(name="password", value="password"),
        app_commands.Choice(name="username", value="username")
        ])
        
    async def search(
        interaction: discord.Interaction,
        lookup: str, data: app_commands.Range[str, 1, 40]
        ):
        search_type = lookup
        user_argument = data 
        search_response = send_request('data/search',{
            'terms': [user_argument],
            'types': [search_type],
            'wildcard': False,})
        response_data = search_response

        if 'results' in response_data:
            await interaction.response.send_message(f"SEARCHED FOR: {user_argument}\n")
            for key, value_list in response_data['results'].items():
                output = ""
                output += f"│  Item: {key}\n"
                for item in value_list:
                    for attribute, value in item.items():
                        output += f"│  {attribute}: {value}\n"
                    output += "│──\n"
                    output2 = output.replace("http", "hxxp")
                await interaction.followup.send(output2)
            await interaction.followup.send("**SEARCH RESULTS FINISHED**")
            #return output
        else:
            await interaction.response.send_message(f"SEARCHED FOR: {user_argument}\nNo results found")

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)

    @search.error
    async def cooldown_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            await interaction.response.send_message(content=str(error), ephemeral=True)
        else:
            return


if __name__ == "__main__":
    run()
