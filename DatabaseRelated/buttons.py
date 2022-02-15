import nextcord
from nextcord.abc import _Overwrites
from nextcord.interactions import Interaction
import mongodb
import UpdateELO
from battle import Battle
from datetime import datetime as dt
import logging
import bot
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
#Buttons to start fights, figure out how to timeout button
class AttackButtons(nextcord.ui.View):
    def __init__(self, p1=None, p2=None, client = None, battle_thread=None):
        super().__init__(timeout=None)
        self.p1 = p1
        self.p2 = p2
        self.client = client
        self.battle_thread = battle_thread
        
    async def interaction_check1(self, player_to_check,interaction):
        logger.debug("Attack Buttons, player to check: %s player who interacted with button: %s", player_to_check, interaction.user.id)
        return player_to_check.id == interaction.user.id

    async def handleApproveorDeny(self,button: nextcord.ui.Button, interaction: nextcord.Interaction, approveClicked):
        button.disable = True
        #gets user and mention username
        user_id = self.p1.id
        user_id2 = self.p2.id
        if approveClicked:
                guild_id = interaction.message.guild.id
                server = self.client.get_guild(guild_id)
                #retrieves username from discord - the numbers
                p1_name = str(server.get_member(user_id))[:-5]
                p2_name = str(server.get_member(user_id2))[:-5]
                
                testing_interaction = None
                if bot.test == True:
                    testing_interaction = self.interaction_check1(self.p1,interaction)
                else:
                    testing_interaction = self.interaction_check1(self.p2,interaction)

                if await testing_interaction:
                    embed = nextcord.Embed(
                        title = "Fight Accepted!",
                        colour = nextcord.Colour.from_rgb(121,180,183)
                    )
                    #creates thread and sends the view to that thread
                    self.battle_thread = await nextcord.TextChannel.create_thread(interaction.channel,name ="{} vs {}".format(p1_name,p2_name), 
                    message = interaction.message, auto_archive_duration= 60, reason = None)
                    await interaction.response.edit_message(embed=embed, view =None)
                    thread_embed = nextcord.Embed(
                        title = "Let the Fight Begin!",
                        description = "Win or lose?",
                        colour = nextcord.Colour.from_rgb(121,180,183)
                    )
                    await self.battle_thread.send(embed=thread_embed, view = WinorLose(self.p1, self.p2, self.battle_thread))
                else:
                    await interaction.response.send_message("only {} can click approve".format(p2_name), ephemeral=True) 
        
        elif not approveClicked and await self.interaction_check1(self.p2,interaction):
            embed = nextcord.Embed(
                title = "Fight Denied!",
                description = "Try again some other time.",
                colour = nextcord.Colour.from_rgb(121,180,183)
            )
            await interaction.response.edit_message(embed=embed, view =None)

    
    #approve button for matches, should check to see if the @mention is the one who clicked it
    @nextcord.ui.button(label= "ACCEPT", emoji = None, style= nextcord.ButtonStyle.green, custom_id= "fight01")
    async def approve_button(self, button, interaction):
        await self.handleApproveorDeny(button, interaction, True)       
    
    #deny button for matches
    @nextcord.ui.button(label= "DENY", emoji = None, style= nextcord.ButtonStyle.danger, custom_id= "deny01")
    async def deny_button(self, button, interaction):
        
        await self.handleApproveorDeny(button, interaction, False)
        


class WinorLose(nextcord.ui.View):
    def __init__(self, p1=None, p2=None, battle_thread=None, rematch = None):
        super().__init__(timeout = None)
        self.clicks = 0
        self.p1 = p1
        self.p2 = p2
        self.battle_thread = battle_thread
        self.rematch = rematch

    async def BIP_char_select(self, interaction):
        get_user = interaction.user.id
        #Deletes Battle in progress if it hasn't been deleted
        if self.rematch == None:
            #deletes battle collection if one already exist
                delete_query = {}
                for player in mongodb.battle_collection.find():
                    if player["p1"] == get_user:
                        delete_query = {"p1": get_user}
                    if player["p2"] == get_user:
                        delete_query = {"p2": get_user}
                mongodb.battle_collection.delete_one(delete_query)
                #
                #Need to figure out how to get character select from list and input it in BIP
                #

                #creates battle collection
                battle = Battle(self.p1.get_id(),self.p2.get_id())
                battle_entry = {
                    "p1": battle.p1,
                    "p1_char": battle.p1_char,
                    "p2": battle.p2,
                    "p2_char": battle.p2_char
                    }
                mongodb.battle_collection.insert_one(battle_entry)                
        else:
            char1 = await self.char_list(self.p1)
            char2 = await self.char_list(self.p2)
            await interaction.channel.send("winner please select char",view=CharSelectView(char1))
            await interaction.channel.send("loser please select char",view=CharSelectView(char2)) 
            for player in mongodb.battle_collection.find():
                if player["p1"] == get_user:
                    self.p1 = get_user
                    self.p2 = player["p2"]
                if player["p2"] == get_user:
                    self.p2 = get_user
                    self.p1 = player["p1"]
    
    async def check_empty(self,array):
        return not array

    async def char_list(self,player):
        options: list[nextcord.SelectOption] = []
        for id in mongodb.player_collection.find():
            if id["_id"] == player.id:
                main_check = await self.check_empty(id.get("main"))
                sec_check = await self.check_empty(id.get("secondary"))
                if not main_check:
                    main_array = id.get("main")
                    for main_char in main_array:
                         options.append(nextcord.SelectOption(
                            label = main_char))
                if not sec_check:
                    secondary_tuple = id.get("secondary")
                    for sec_char in secondary_tuple:
                       options.append(nextcord.SelectOption(
                            label = sec_char))            
        return options

    async def interaction_check1(self, player_to_check,interaction):
        logger.debug("Win or lose buttons, player to check: %s player who interacted with button: %s", player_to_check, interaction.user.id)
        return player_to_check.id == interaction.user.id

    #Where the magic will happen; the buttons will call the updateELO class from here, also need to disable buttons here
    async def handle_win_or_lose(self, button: nextcord.ui.Button, interaction: nextcord.Interaction, clicker_wins):

        #retrieves the user and depending who the last past who clicks the button, updates the ELO and player_collection
        get_user = interaction.user.id           

        #number of clicks in the view
        if self.clicks >= 2:
            await self.BIP_char_select(interaction)
            #if last person clicks win
            if clicker_wins:
                for player in mongodb.battle_collection.find():
                    if player["p1"] == get_user:
                        winner = self.p1
                        loser = self.p2
                        winner_chosen_char = player["p1_char"]
                        loser_chosen_char = player["p2_char"]
                    elif player["p2"] == get_user:
                        winner = self.p2
                        loser = self.p1
                        winner_chosen_char = player["p2_char"]
                        loser_chosen_char = player["p1_char"]  
            else:
                for player in mongodb.battle_collection.find():
                    if player["p1"] == get_user:
                        winner = self.p2                       
                        loser = self.p1
                        winner_chosen_char = player["p2_char"]
                        loser_chosen_char = player["p1_char"]
                    elif player["p2"] == get_user:
                        winner = self.p1
                        loser = self.p2
                        winner_chosen_char = player["p1_char"]
                        loser_chosen_char = player["p2_char"]
            #can put winner_char and loser char and pass it to ELO, can do above when getting winner and loser***************************  
            UpdateELO.update_elo_rating(winner, loser, winner_chosen_char, loser_chosen_char) 
            #add battle to history collection
            #
            #add back when ready
            #
            #unfortunately, from 12/28 to 1/4, the history was not saved.
            # history_entry = {
            #     "winner": winner.get_id(),
            #     "loser": loser.get_id(),
            #     "win_char": winner_char.selected_value
            #     "lose_char": loser_char.selected_value
            #     "date": dt.now()
            # }
            # mongodb.history_collection.insert_one(history_entry)


            embed_end_match = nextcord.Embed(
                title = "Match Complete!",
                description = "<@{}> Wins Against <@{}>!".format(winner.get_id(), loser.get_id()),
                colour = nextcord.Colour.from_rgb(121,180,183)
            )

            await interaction.response.edit_message(embed= embed_end_match, 
            view=MatchComplete(self.p1, self.p2, self.battle_thread))
        else:
            await interaction.response.edit_message(view=self)  
      

    #button for winning
    @nextcord.ui.button(label= "WIN", disabled = False, emoji = None, style= nextcord.ButtonStyle.green, custom_id= "iWin01")
    async def win_button(self, button, interaction):     
        
        if await self.interaction_check1(self.p2, interaction) or await self.interaction_check1(self.p1, interaction):
            button.disabled = True
            self.clicks+=1
            await self.handle_win_or_lose(button,interaction, True)
        
    #button for losing
    @nextcord.ui.button(label= "LOSE", emoji = None, style= nextcord.ButtonStyle.danger, custom_id= "iLose01")
    async def loss_button(self, button, interaction):
        
        if await self.interaction_check1(self.p2, interaction) or await self.interaction_check1(self.p1, interaction):
            button.disabled = True
            self.clicks += 1
            await self.handle_win_or_lose(button,interaction, False)
    
    #button for reset
    @nextcord.ui.button(label= "RESET", emoji = None, style= nextcord.ButtonStyle.secondary, custom_id= "reset01")
    async def reset_button(self, button, interaction):
        if await self.interaction_check1(self.p2, interaction) or await self.interaction_check1(self.p1, interaction):
            thread_embed = nextcord.Embed(
                title = "Buttons Have Been Reset.",
                description = "Win or lose?",
                colour = nextcord.Colour.from_rgb(121,180,183)
            )
            await interaction.response.edit_message(embed=thread_embed, view=WinorLose(self.p1,self.p2, self.battle_thread))

class MatchComplete(nextcord.ui.View):
    def __init__(self, p1=None, p2=None, battle_thread = None):
        super().__init__(timeout=None)
        self.p1 = p1
        self.p2 = p2

        self.p1_clicks = 0
        self.p2_clicks = 0
        self.battle_thread = battle_thread 

    async def interaction_check1(self, player_to_check, interaction):
        logger.debug("Match Complete buttons, player to check: %s player who interacted with button: %s", player_to_check, interaction.user.id)
        return player_to_check.id == interaction.user.id
    
    async def char_list(self,player):
        options: list[nextcord.SelectOption] = []
        for id in mongodb.player_collection.find():
            if id["_id"] == player.id:
                main_check = await self.check_empty(id.get("main"))
                sec_check = await self.check_empty(id.get("secondary"))
                if not main_check:
                    main_array = id.get("main")
                    for main_char in main_array:
                         options.append(nextcord.SelectOption(
                            label = main_char))
                if not sec_check:
                    secondary_tuple = id.get("secondary")
                    for sec_char in secondary_tuple:
                       options.append(nextcord.SelectOption(
                            label = sec_char))            
        return options

    @nextcord.ui.button(label= "REMATCH",emoji = None, style= nextcord.ButtonStyle.green, custom_id= "rematch01")
    async def rematch_button(self,button, interaction):
        rematch = True
        if await self.interaction_check1(self.p2, interaction):
            self.p2_clicks +=1
            logger.debug(" user: %s amount clicks: %s fighter: %s", self.p1.id, self.p1_clicks, self.p2)
        elif await self.interaction_check1(self.p1, interaction):
            self.p1_clicks += 1
            
            if bot.test == True:
                self.p2_clicks +=1
            logger.debug(" user: %s: amount clicks %s fighter: %s", self.p1.id, self.p1_clicks,self.p1)
        if self.p1_clicks >= 1 and self.p2_clicks >= 1:
            thread_embed = nextcord.Embed(
                title = "Let the Fight Begin!",
                description = "Win or lose?",
                colour = nextcord.Colour.from_rgb(121,180,183)
            )
            await interaction.message.delete()
            await interaction.response.send_message(embed=thread_embed, view = WinorLose(self.p1, self.p2, self.battle_thread, rematch))
        
        #search for char 
        char1 = await self.char_list(interaction)
        #char2 = await self.char_list(self.p2)
        await interaction.channel.send(f"@{interaction.user.id} please select char",view=CharSelectView(char1,interaction.user.id))
        #await interaction.channel.send(f"@{.p2_id} please select char",view=CharSelectView(char2, self.p2))  
    
    @nextcord.ui.button(label= "GGs",emoji = None, style= nextcord.ButtonStyle.secondary, custom_id= "endMatch01")
    async def endMatch_button(self, button, interaction):        
        
        if await self.interaction_check1(self.p2, interaction) or await self.interaction_check1(self.p1, interaction):
            #deletes battle collection
            delete_query = {}
            for player in mongodb.battle_collection.find():
                if player["p1"] == self.p1.get_id():
                    delete_query = {"p1": self.p1.get_id()}
                if player["p2"] == self.p2.get_id():
                    delete_query = {"p2": self.p2.get_id()}
            mongodb.battle_collection.delete_one(delete_query)

            thread_embed = nextcord.Embed(
                title = "GGs!",
                description = "Thanks for playing!",
                colour = nextcord.Colour.from_rgb(121,180,183)
            )
            await interaction.response.edit_message(embed=thread_embed, view = None)
            # await self.battle_thread.delete()


#
#Don't forgot to check if right player chooses interaction
#
#
class CharSelectDropdown(nextcord.ui.Select):
    def __init__(self, options, player):
        super().__init__(placeholder = "choose a character", min_values=1, max_values =1, options=options)
        self.player = player
    
    async def callback(self, interaction):
        if self.interaction_check(self.player):
            player_char = self.values[0]
            for player in mongodb.battle_collection.find():
                if player["p1"] == self.player:
                    update_char = {"$set": {"p1_char": player_char}}
                elif player["p2"] == self.player:
                    update_char = {"$set": {"p2_char": player_char}}
            
            mongodb.battle_collection.update_one(self.player,update_char)
            # can change to embed later
            await interaction.response.send_message("updated your character win/losses")
        else:
            await interaction.response.send_message(f"sorry, @{interaction.user.id} isn't valid to press the button")

class CharSelectView(nextcord.ui.View):
    def __init__(self,options,player):
        super().__init__(timeout=None)
        self.player = player
        self.add_item(CharSelectDropdown(options, player))
