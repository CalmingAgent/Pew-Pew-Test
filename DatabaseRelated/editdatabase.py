from player import Player
import mongodb
class EditDatabase:
    
    def createPlayer(user):
        """adds player to database"""
        for id in mongodb.player_collection.find():
            if id["_id"] == user:
                #await message.channel.send("<@{0}> is already in the database.".format(user))
                print("already in database")
                return

        p1 = Player(user)
        wins = {}
        loses = {}
        char_stats = {{[]}}
        p1_entry = {
            "_id": p1.id,
            "rating": p1.rating,
            "win_count": p1.win_count,
            "lose_count": p1.lose_count,
            "win_streak": p1.win_streak,
            "best_win_streak": p1.best_win_streak,
            "match_history": [wins, loses],
            "char_stats": char_stats
        }
        mongodb.player_collection.insert_one(p1_entry)