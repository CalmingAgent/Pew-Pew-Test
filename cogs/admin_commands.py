from os import close
import nextcord
import sys
from nextcord import client
from nextcord.ext import commands

#parent directory import
sys.path.append('DatabaseRelated')
sys.path.append('cogs')
import mongodb
import UpdateELO
from player import Player
from buttons import AttackButtons, CharSelectView
from buttons import WinorLose
from buttons import MatchComplete

from datetime import datetime as dt

from nextcord.ext.commands.core import has_permissions
from nextcord.ext.commands import MissingPermissions

# this would be used for only admin in TTD server, need to implement this
class Admin(commands.Cog):
    """Admin Commands"""

    def __init__(self,client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("bot ready")
        self.client.add_view(AttackButtons())
        self.client.add_view(WinorLose())
        self.client.add_view(MatchComplete())
        #self.client.add_view(CharSelectView())
 
        await self.write_emojis()
        
        # await self.simulate_history()
        #print('Logged on as {0}!'.format(self.user.name))
    
    # @commands.command()
    # async def load(self,ctx,extension):
    #     """
    #     Loads cog files
    #     """
    #     admin1= 472883421212049409
    #     admin2= 705139734426419260
    #     if ctx.author.id == admin2 or ctx.author.id == admin1: 
    #         self.client.load_extension(f'cogs.{client.extension}')

    # @commands.command()
    # async def unload(self,ctx, extension):
    #     """
    #     Unload cog files
    #     """
    #     admin1= 472883421212049409
    #     admin2= 705139734426419260
    #     if ctx.author.id == admin2 or ctx.author.id == admin1: 
    #         self.client.unload_extension(f'cogs.{client.extension}')

    # @commands.command()
    # @has_permissions(administrator=True)
    # async def createPlayer(self,ctx, user: nextcord.Member):
    #     """
    #     Add user to database\n
    #     **Usage:** `=createPlayer @player`
    #     """
    #     #print('ctx from {0.author}: {0.content}'.format(ctx))
    #     for id in mongodb.player_collection.find({},
    #                                                 {"_id": 1, "rating": 0, "win_count": 0, "lose_count": 0, "win_streak": 0, "best_win_streak": 0}):
    #         if id["_id"] == user.id:
    #             embed = nextcord.Embed(
    #                 title = "{0} is already in the database.".format(user),
    #                 colour = nextcord.Colour.from_rgb(121,180,183)
    #             )
    #             await ctx.channel.send(embed=embed)                
    #             return

    #     p1 = Player(user.id)
    #     p1_entry = {
    #         "_id": p1.id,
    #         "rating": p1.rating,
    #         "win_count": p1.win_count,
    #         "lose_count": p1.lose_count,
    #         "win_streak": p1.win_streak,
    #         "best_win_streak": p1.best_win_streak
    #     }
    #     mongodb.player_collection.insert_one(p1_entry)
    #     embed = nextcord.Embed(
    #         title = "<@{0}> entry for database created.".format(user),
    #         colour = nextcord.Colour.from_rgb(121,180,183)
    #     )
    #     await ctx.channel.send(embed=embed)

    @commands.command()
    @has_permissions(administrator=True)
    async def deletePlayer(self,ctx, user: nextcord.Member):
        """
        Delete user from database\n
        **Usage:** `=deletePlayer @player`
        """
        admin1= 472883421212049409
        admin2= 705139734426419260
        if ctx.author.id == admin2 or ctx.author.id == admin1: 
            for id in mongodb.player_collection.find({},
                                                    {"_id": 1, "rating": 0, "win_count": 0, "lose_count": 0, "win_streak": 0, "best_win_streak": 0}):
                if id["_id"] == user.id:
                    delete_id = {"_id": user.id}
                    mongodb.player_collection.delete_one(delete_id)

                    embed = nextcord.Embed(
                        title = "Entry for {0} has been deleted.".format(user),
                        colour = nextcord.Colour.from_rgb(121,180,183)
                    )
                    await ctx.channel.send(embed=embed)
                    return

            embed = nextcord.Embed(
                title = "{0} is not in the database.".format(user),
                colour = nextcord.Colour.from_rgb(121,180,183)
            )
            await ctx.channel.send(embed=embed)
        else:
            embed = nextcord.Embed(
                title = "Only developers can use this command.",
                colour = nextcord.Colour.from_rgb(121,180,183)
            )
            await ctx.channel.send(embed=embed)

    # @commands.command()
    # @has_permissions(administrator = True)
    # async def create_log(self,):
    #     logger = logging.getLogger(__name__)
    #     logger.setLevel(logging.debug)
    
    
    # @createPlayer.error
    # async def createPlayer_error(ctx, error):
    #     if isinstance(error, MissingPermissions):
    #         embed = nextcord.Embed(
    #             title = "Only `Admins` can do this command!",
    #             colour = nextcord.Colour.from_rgb(121,180,183)
    #         )
    #         await ctx.channel.send(embed=embed)
    
    # @deletePlayer.error
    # async def deletePlayer_error(ctx, error):
    #     if isinstance(error, MissingPermissions):
    #         embed = nextcord.Embed(
    #             title = "Only `Admins` can do this command!",
    #             colour = nextcord.Colour.from_rgb(121,180,183)
    #         )
    #         await ctx.channel.send(embed=embed)
    
    async def write_emojis(self):
        """
        Writes server emojis into a text file
        """ 
        #TTD 753129805318455356  
        #Test 575869943346757682
        server_emojis = open("server_emojis.txt", "w")
        #need to change this to TTD server ID
        server = self.client.get_guild(753129805318455356)
        for emoji in server.emojis:
            character = [str(emoji.name).lower(), " ", str(emoji.id), "\n"]
            server_emojis.writelines(character)
        
        server_emojis.close()
    
    async def simulate_history(self):
        count = 0
        for id in mongodb.player_collection.find():
            if id["_id"] > 0:

                query = { "_id": id["_id"] }
                wins = {}
                loses = {}
                update = { 
                    "$set": { 
                        "rating": 1000,
                        "win_count": 0,
                        "lose_count": 0,
                        "win_streak": 0,
                        "best_win_streak": 0,
                        "match_history": [wins, loses]
                    } 
                }

                mongodb.player_collection.update_one(query,update)
                count += 1
        
        print(str(count) +  " player entries set to default")

        # print("starting batch delete...")
        # date = dt(2021, 12, 29)
        # myquery = { "date": {"$gte": date} }
        # x = mongodb.history_collection.delete_many(myquery)
        # print(x.deleted_count, " documents deleted.")

        count = 0
        print("starting history simulation...")
        for entry in mongodb.history_collection.find():
            for id in mongodb.player_collection.find():
                if id["_id"] == entry["winner"]:
                    winner = Player(entry["winner"], rating=id["rating"], win_count=id["win_count"], lose_count=id["lose_count"], win_streak=id["win_streak"], best_win_streak=id["best_win_streak"])
                if id["_id"] == entry["loser"]:
                    loser = Player(entry["loser"], rating=id["rating"], win_count=id["win_count"], lose_count=id["lose_count"], win_streak=id["win_streak"], best_win_streak=id["best_win_streak"])
            count += 1
            UpdateELO.update_elo_rating(winner, loser)
            print("updated " + str(count) + " entries")
        
        print("finished going through history")




def setup(client):
    client.add_cog(Admin(client))