import json
#Implementation of a standard Poker card, with ability to output to JSON
class Card:
    def __init__(self, rank, suit):
        self.rank = {"rank": rank}
        self.suit = {"suit": suit}

    def to_json(self):
         return json.dumps({"rank": self.rank, 
                            "suit": self.suit})