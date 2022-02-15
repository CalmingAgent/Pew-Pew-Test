import mongodb
from player import Player
from datetime import datetime as dt


'''Updates ELO ratings from match results'''
def update_elo_rating(winner,loser,win_char,lose_char):
    # Get ratings from Player objects
    winner_rating = winner.rating
    loser_rating = loser.rating

    POWOFTEN = 10
    ALGOF400 = 400

    #transform rating
    transform_p1 = pow(POWOFTEN,(winner_rating/ALGOF400 ))
    transform_p2 = pow(POWOFTEN,(loser_rating/ALGOF400 ))


    # Calculate probabilities of winning
    winner_probability = transform_p1 / (transform_p1 + transform_p2)
    loser_probability = transform_p2 / (transform_p1 + transform_p2)    

    # FIDE K-factor for Winner
    if winner_rating < 2300 or (winner.win_count + winner.lose_count) <= 30:
        p1_k = 40
    elif winner_rating < 2400:
        p1_k = 20
    else:
        p1_k = 10
    
    # FIDE K-factor for Loser
    if loser_rating < 2300 or (loser.win_count + loser.lose_count) <= 30:
        p2_k = 40
    elif loser_rating < 2400:
        p2_k = 20
    else:
        p2_k = 10

    # Calculate players' ELO ratings
    winner_rating = winner_rating + p1_k * (1 - winner_probability)
    loser_rating = loser_rating + p2_k * (0 - loser_probability)

    # Set new ratings to Player objects
    winner.set_rating(int(round(winner_rating,0)))
    loser.set_rating(int(round(loser_rating,0)))
    
    # Add wins and loses accordingly
    winner.plus_win()
    loser.plus_lose()

    p1_query = {
        "_id": winner.id,
    }
    p2_query = {
        "_id": loser.id,
    }
    #updates loser char_stats
    for player in mongodb.player_collection.find():
        #updates winners char_stats
        if player["_id"] == winner.get_id():
            
            try: player["char_stats"]
            except KeyError:
                win = {"win": 0, "lose": 0}
                enemy_dictionary = {lose_char: win}
                char_stat_copy_win = {win_char: enemy_dictionary}
                #char_stat_copy_win = {{{"win": 0, "lose": 0}}}
            else:
                char_stat_copy_win = player["char_stats"]

            if char_stat_copy_win != None:
                if char_stat_copy_win == win_char:
                    if char_stat_copy_win[win_char] == lose_char:
                        char_stat_copy_win[win_char][lose_char]["win"] += 1
                    else:
                        #add loser character to char_stat in player profile
                        char_stat_copy_win[win_char][lose_char]["win"] = 1
                        char_stat_copy_win[win_char][lose_char]["lose"] = 0
                else:
                    #add winner character to char_stat in player profile
                    char_stat_copy_win[win_char][lose_char]["win"] = 1
                    char_stat_copy_win[win_char][lose_char]["lose"] = 0
            else:
                char_stat_copy_win[win_char][lose_char]["win"] = 1
                char_stat_copy_win[win_char][lose_char]["lose"] = 0
        
        #updates loser char_stats
        if player["_id"] == loser.get_id():

            try: player["char_stats"]
            except KeyError:
                win = {"win": 0, "lose": 0}
                enemy_dictionary = {win_char: win}
                char_stat_copy_lose = {lose_char: enemy_dictionary}
                #char_stat_copy_win = {{{"win": 0, "lose": 0}}}
            else:
                char_stat_copy_lose = player["char_stats"]

            if char_stat_copy_lose != None:
                if char_stat_copy_lose == lose_char:
                    if char_stat_copy_lose[lose_char] == win_char:
                        char_stat_copy_lose[lose_char][win_char]["lose"] += 1
                    else:
                        #add loser character to char_stat in player profile
                        char_stat_copy_lose[lose_char][win_char]["lose"] = 1
                        char_stat_copy_lose[lose_char][win_char]["win"] = 0
                else:
                    #add winner character to char_stat in player profile
                    char_stat_copy_lose[lose_char][win_char]["lose"] = 1
                    char_stat_copy_lose[lose_char][win_char]["win"] = 0
            else:
                char_stat_copy_lose[lose_char][win_char]["lose"] = 1
                char_stat_copy_lose[lose_char][win_char]["win"] = 0                   
        

    new_p1 = { 
        "$set": { 
            "rating": winner.rating,
            "win_count": winner.win_count,
            "lose_count": winner.lose_count,
            "win_streak": winner.win_streak,
            "best_win_streak": winner.best_win_streak,
            "char_stats": char_stat_copy_win
        } 
    }

    new_p2 = { 
        "$set": { 
            "rating": loser.rating,
            "win_count": loser.win_count,
            "lose_count": loser.lose_count,
            "win_streak": loser.win_streak,
            "best_win_streak": loser.best_win_streak,
            "char_stats": char_stat_copy_lose
        } 
    }
    
    

    mongodb.player_collection.update_one(p1_query, new_p1)
    mongodb.player_collection.update_one(p2_query, new_p2)
    #updates history
    for player in mongodb.player_collection.find():
        if player["_id"] == winner.get_id():
            copy = player["match_history"]
            if player["match_history"][0].get(str(loser.get_id())) != None:
                copy[0][str(loser.get_id())] += 1
            else:                 
                copy[0][str(loser.get_id())] = 1    
            query = {
                "_id": winner.get_id(),
            }
            update_query = { "$set": { "match_history": copy } }
            mongodb.player_collection.update_one(query, update_query)
        elif player["_id"] == loser.get_id():
            copy = player["match_history"]
            if player["match_history"][1].get(str(winner.get_id())) != None:
                copy[1][str(winner.get_id())] += 1
            else:                 
                copy[1][str(winner.get_id())] = 1    
            query = {
                "_id": loser.get_id(),
            }
            update_query = { "$set": { "match_history": copy } }
            mongodb.player_collection.update_one(query, update_query)

