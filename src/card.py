from typing import NamedTuple


class Card(NamedTuple):
    """
    Represents a playing card.
    """

    rank: str
    suit: str
