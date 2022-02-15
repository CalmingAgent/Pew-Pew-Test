from distutils.command.config import config
import json
from pipes import Template
import nextcord
from nextcord.ext import commands
import os

from cogs import help_commands

from nextcord.ext.commands.core import group

# sys.path.append("C:\Users\Chapm\GitHub\Pew_Pew\cogs")
#from cogs import help_commands


intents = nextcord.Intents.default()
intents.members = True
#test
#server
#switch
test = False
command_prefix_set =""
if test:
    command_prefix_set = "??"
    key_file = "/koten.json"

else:
    command_prefix_set = "="
    key_file = "/kotenTrue.json"
client = commands.Bot(command_prefix = command_prefix_set, intents = intents, description="**Ranked Matchmaking Bot for SSBU with ELO Rating!**\n> To see a description for each command based on category: \n> `=help command_category`\n> For help with specific commands: \n> `=help command_name`")
client.help_command = help_commands.MyHelpCommand()

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

if os.path.exists(os.getcwd() + key_file): 
    with open("." + key_file) as f:
        config_data = json.load(f)
else:
    template = {"Token": "", "Prefix": command_prefix_set, "DB": ""}

    with open(os.getcwd() + key_file, "w+") as f:
        json.dump(template, f)
token = config_data["Token"]
database = config_data["DB"]       

client.run(token)
