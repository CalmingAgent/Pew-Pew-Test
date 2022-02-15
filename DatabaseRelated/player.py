class Player:
    def __init__(self, id, rating=1000, win_count=0, lose_count=0, win_streak=0, best_win_streak=0):
        self.id = id
        self.rating = rating
        self.win_count = win_count
        self.lose_count = lose_count
        self.win_streak = win_streak
        self.best_win_streak = best_win_streak

    def get_id(self):
        return self.id

    def get_rating(self):
        return self.rating

    def set_rating(self, rating):
        self.rating = rating
    
    # def set_char_selected(self, char_selected):
    #     self.char_selected = char_selected
    
    # def get_char(self):
    #     return self.char_selected

    def plus_win(self):
        self.win_count += 1
        self.win_streak += 1
        if self.win_streak > self.best_win_streak:
            self.best_win_streak = self.win_streak

    def plus_lose(self):
        self.lose_count += 1
        self.win_streak = 0
    
    def get_tier(rating):
        if 0 < rating <= 1149:
            return "Bronze"
        elif 1149 < rating <= 1499:
            return "Silver"
        elif 1499 < rating <= 1849:
            return "Gold"
        elif 1849 < rating <= 2199:
            return "Platinum"
        elif 2199 < rating:
            return "Diamond"
