class ProfileModel:
    def __init__(self, nickname="Player"):
        self.nickname = nickname
        self.stats = {"total_matches": 0, "wins": 0, "losses": 0}
        self.decks = []

    def to_dict(self):
        return {
            "player_info": {"nickname": self.nickname},
            "player_stats": self.stats,
            "decks_info": {
                "total_decks": len(self.decks),
                "decks": self.decks
            }
        }