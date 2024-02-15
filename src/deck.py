from card import Card
import random
SUITS = ["C", "D", "H", "S"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

#TODO: implement ranking
class Deck:
    def __init__(self):
        self.cards = []
        for suit in (SUITS):
            for rank in (RANKS):
                card = Card(rank, suit)
                self.cards.append(card.to_json)
                
        random.shuffle(self.cards)
    
    def pop(self):
        return self.cards.pop()
    
    def draw(self, num):
        cards_drawn = []
        #if(self.cards.__sizeof__ < num):
            #num = self.cards.__sizeof__
        for _ in range(num):
            cards_drawn.append(self.pop())
        return cards_drawn

