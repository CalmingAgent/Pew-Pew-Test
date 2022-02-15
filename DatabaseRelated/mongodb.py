import pymongo
from pprint import pprint
import bot

from pymongo import collection # pprint library is used to make the output look more pretty

# connect to MongoDB
client = pymongo.MongoClient(bot.database)
bot_db = client["Bot"]
player_collection = bot_db["Player"]
battle_collection = bot_db["BattleInProgress"]
history_collection = bot_db["History"]
global_char_stats = bot_db["Char_Stats"]
# Issue the serverStatus command and print the results
serverStatusResult=bot_db.command("serverStatus")
#pprint(serverStatusResult)

db_list = client.list_database_names()
collection_list = bot_db.list_collection_names()

character_dictionary = {}
