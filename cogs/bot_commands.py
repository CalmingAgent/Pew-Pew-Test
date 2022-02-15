import nextcord
from nextcord.ext import commands
import sys
import random

#parent directory import
sys.path.append('DatabaseRelated')
sys.path.append('cogs')
import mongodb
from player import Player
from buttons import AttackButtons
from buttons import WinorLose 
import editdatabase

class Bot(commands.Cog):
    """Normal Bot Commands"""

    def __init__(self,client):
        self.client = client    

    async def character_dictionary_method(self):
        character_dictionary = {}
        value = []
        characters = open("server_emojis.txt")
        for line in characters:
            key,value = line.split()
            character_dictionary[key] = value
        characters.close()

        return character_dictionary

    async def character_alias_method(self):
        character_aliases = {}
        value = []
        characters = open("alias.txt")
        for line in characters:
            key,value = line.split()
            character_aliases[key] = value.lower()
        characters.close()

        #checks for more than one space
        # for idx, line in enumerate(characters, 1):
        #     split_list = line.split()
        #     if len(split_list) != 2:
        #         raise ValueError("Line {}: '{}' has {} spaces, expected 1"
        #             .format(idx, line.rstrip(), len(split_list) - 1))
        #     else:
        #         count = split_list
        #         print(count)
        return character_aliases


    @commands.command()
    async def fight(self,ctx, user: nextcord.Member):
        """
        Initiate a fight with another player\n
        **Usage:**: `=fight @player`\n
        **Directions:**
        > Opponent clicks `APPROVE` or `DENY`
        > If approved, both players click either `WIN` or `LOSE`
        > If pressed wrongly, press `RESET` to enable buttons again
        > Both players click `REMATCH` to reinitiate a fight process or end it with `GGs`
        """                          
                        
        channel = self.client.get_channel(ctx.channel.id)
        if channel.type == nextcord.ChannelType.public_thread:
            embed = nextcord.Embed(
                title = "Cannot do `=fight` command within thread!",
                colour = nextcord.Colour.from_rgb(121,180,183)
            )
            await ctx.channel.send(embed=embed)
            return
        
        if user.id == ctx.author.id:
            embed = nextcord.Embed(
                title = "You cannot fight yourself.",
                colour = nextcord.Colour.from_rgb(121,180,183)
            )
            await ctx.channel.send(embed=embed)

            return


        not_in_db_count = 0
        entries_added = False
        while not entries_added:
            #checks if both users are in the database, if not it adds them
            for id in mongodb.player_collection.find():
                if id["_id"] == user.id:
                    for idTwo in mongodb.player_collection.find():
                        if idTwo["_id"] == ctx.author.id:
                            #creates entry for player object
                            p1_entry = Player(idTwo["_id"], rating=idTwo["rating"], win_count=idTwo["win_count"], lose_count=idTwo["lose_count"], win_streak=idTwo["win_streak"], best_win_streak=idTwo["best_win_streak"])
                            p2_entry = Player(id["_id"], rating=id["rating"], win_count=id["win_count"], lose_count=id["lose_count"], win_streak=id["win_streak"], best_win_streak=id["best_win_streak"])
                            entries_added = True
                    
                            #gets the desired username without the #
                            guild_id = ctx.message.guild.id
                            server = self.client.get_guild(guild_id)
                            member_name1 = str(server.get_member(ctx.author.id))
                            member_name2 = str(server.get_member(user.id))
                            username1 = member_name1[0:len(member_name1)-5]
                            username2 = member_name2[0:len(member_name2)-5]
                            #checks to see if the username is the title (which would be just the thread) and if it is, only do win or lose view
                            if str(ctx.message.channel) == "{} vs {}".format(username1,username2):
                                viewButton = WinorLose(p1_entry, p2_entry,ctx.message.channel)                                   
                            else:
                                viewButton = AttackButtons(p1_entry, p2_entry, self.client)                               
                            

                            embed = nextcord.Embed(
                                title = "Settle it in Smash!",
                                description = "<@{}>, do you accept match against <@{}>?".format(p2_entry.get_id(), p1_entry.get_id()),
                                colour = nextcord.Colour.from_rgb(121,180,183)
                            )

                            #Sends the view to the right channel and the corresponding view associated with the thread or channel
                            await ctx.channel.send(embed=embed, view= viewButton)                            
                            return
                        
                        #if user is not in database adds them to the database    
                        else:
                            not_in_db_count += 1
                            author = ctx.author.id
                            
                else:
                    not_in_db_count += 1
                    author = user.id
            if not_in_db_count == 1:
                editdatabase.EditDatabase.createPlayer(author)
            else:
                editdatabase.EditDatabase.createPlayer(ctx.author.id)
                editdatabase.EditDatabase.createPlayer(user.id)      

    @commands.command()
    async def random(self, ctx):
        """
        See a random SSBU portrait
        > Try to get your main!
        """

        fighters = ['mario', 'donkey_kong', 'link', 'samus', 'dark_samus', 'yoshi', 'kirby', 'fox', 'pikachu', 'luigi', 'ness', 'captain_falcon', 'jigglypuff', 'peach', 'daisy', 'bowser', 'ice_climbers', 'sheik', 'zelda', 'dr_mario','pichu', 'falco', 'marth', 'lucina', 'young_link', 'ganondorf', 'mewtwo', 'roy', 'chrom','mr_game_and_watch', 'meta_knight', 'pit', 'dark_pit', 'zero_suit_samus', 'wario', 'snake', 'ike','pokemon_trainer', 'diddy_kong', 'lucas', 'sonic', 'king_dedede', 'olimar', 'lucario', 'rob', 'toon_link','wolf', 'villager', 'mega_man', 'wii_fit_trainer', 'rosalina_and_luma', 'little_mac', 'greninja', 'mii_brawler', 'mii_gunner', 'mii_swordfighter', 'palutena', 'pac_man', 'robin', 'shulk', 'bowser_jr', 'duck_hunt', 'ryu', 'ken', 'cloud','corrin', 'bayonetta', 'inkling', 'ridley', 'simon', 'richter', 'king_k_rool', 'isabelle', 'incineroar','piranha_plant', 'joker', 'dq_hero', 'banjo_and_kazooie', 'terry', 'byleth', 'minmin', 'steve', 'sephiroth', 'pyra', 'kazuya', 'sora']

        alts = ['main', 'main2', 'main3', 'main4', 'main5', 'main6', 'main7', 'main8']

        character_images = []

        url = "https://raw.githubusercontent.com/chriscolomb/ssbu/master/OPTIMIZED%20PORTRAITS/"
        for fighter in fighters:
            if "mii" not in fighter:
                for alt in alts:
                    image_url = url + fighter + '_' + alt + '.png'
                    character_images.append(image_url)
            else:
                image_url = url + fighter + '.png'
                character_images.append(image_url)
        
        embed = nextcord.Embed()
        embed.set_image(url=random.choice(character_images))
        embed.colour = nextcord.Colour.from_rgb(121,180,183)
        await ctx.channel.send(embed=embed)
    
    #handles the secondary and main command
    async def character_find(self,ctx, main, args):
        #dictionaries for character and alias        
        dictionary = await self.character_dictionary_method()
        alias_dictionary = await self.character_alias_method()
        character_array = []
        player_id = {"_id": ctx.author.id}
        #gets title depending on command, only if empty
        title = None
        colour = nextcord.Colour.from_rgb(121,180,183)
        if main:
            title = "Mains cleared!"
        else:
            title = "Secondaries Cleared"

        embed = nextcord.Embed(
            title = title,
            colour = colour
        )
        if args == None:
            character_array = [None]
        else:
            for characters in args:
                characters = characters.lower()
                isIn = True
                if characters in alias_dictionary:
                    characters = alias_dictionary[characters]
                try: dictionary[characters]
                except KeyError:
                    embed = nextcord.Embed(
                        title = "Character \"{}\" doesn't exist!".format(characters),
                        colour = colour
                    )
                    isIn = False
                if isIn:
                    characterID = int(dictionary[characters])
                    
                    if characterID not in character_array:
                        character_array.append(characterID)
                        title = "Character(s) added!"
                    else:
                        title = "Can't add duplicates!",
  
                    embed = nextcord.Embed(
                            title = title,
                            colour = colour
                        )
            
            await ctx.channel.send(embed=embed)

            if main:
                update_main_query = { "$set": { "main": character_array } }
                mongodb.player_collection.update_one(player_id, update_main_query)
            else:
                update_secondary_query = { "$set": { "secondary": character_array } }
                mongodb.player_collection.update_one(player_id, update_secondary_query)
        
    #async def assign_chars(self,ctx,)
    @commands.command()
    async def main(self,ctx, *args):
        """
        Assign mains to your player stats\n
        **Usage:** 
        > To add one or more: `=main rob zss`
        > To clear your mains: `=main`
        """
        await self.character_find(ctx, True, args)
        

    @commands.command()
    async def secondary(self,ctx, *args):
        """
        Assign secondaries to your player stats\n
        **Usage:** 
        > To add one or more: `=secondary sora marth`
        > To clear your secondaries: `=secondary`
        """
        await self.character_find(ctx, False, args)

def setup(client):
    client.add_cog(Bot(client))