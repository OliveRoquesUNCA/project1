from card import Card
import random
from dataclasses import dataclass, field
from functools import partial

SUITS = ["C", "D", "H", "S"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
CARDS = [Card(rank=r, suit=s) for r in RANKS for s in SUITS]


# TODO: implement ranking
@dataclass
class Deck:
    cards: list[Card] = field(
        default_factory=partial(random.sample, CARDS, len(CARDS))
    )
    top: int = 0

    def pop(self) -> dict[str, str]:
        card = self.cards[self.top]
        self.top += 1
        return card._asdict()

    def draw(self, num: int) -> list[dict[str, str]]:
        return [self.pop() for _ in range(num)]

    def to_serializable(self) -> list[dict[str, str]]:
        return [c._asdict() for c in self.cards]

    @property
    def cards_left(self) -> int:
        """
        Returns the number of cards left in the deck.
        """
        return len(self.cards) - self.top
