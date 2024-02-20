import asyncio
import asyncpg
import secrets
import string
import random
import time
import json
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from collections import Counter
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from deck import Deck

SUITS = ["C", "D", "H", "S"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

app = FastAPI()

# Dictionaries to store client IDs and associated objects
deck_objects: dict[str, Deck] = {}
expiration_times: dict[str, float] = {}

DECK_ID_BYTES = 16
DECK_ID_DURATION_HOURS = 24


def generate_unique_deck_id() -> str:
    while True:
        did = secrets.token_urlsafe(DECK_ID_BYTES)
        if did not in deck_objects:
            return did
        


@app.get("/api/v1/hello")
async def api_v1():
    return {"message": "Hello World!"}


@app.get("/api/v1/deal")
async def api_v1_deal():
    return {"rank": random.choice(RANKS), "suit": random.choice(SUITS)}


# creates new deck, adds deck ID and associated deck object to dictionary, generates new expiration time associated with it
@app.post("/api/v2/deck/new")
async def api_v2_deck_new():
    d = Deck()
    deck_id = generate_unique_deck_id()
    deck_objects[deck_id] = d
    # converts datetime to unix timestamp in seconds
    expiration_time = (
        datetime.now() + timedelta(hours=DECK_ID_DURATION_HOURS)
    ).timestamp()
    expiration_times[deck_id] = expiration_time
    hand = d.draw(5)
    return {
        "deck_id": deck_id,
        "expires": expiration_time,
        "hand": {"cards": hand},
    }


# returns deck associated with given parameter deck_id
@app.head("/api/v2/deck/{deck_id}")
@app.get("/api/v2/deck/{deck_id}")
async def api_v2_deck(deck_id: str) -> dict:
    d = deck_objects.get(deck_id)

    if d is None:
        raise HTTPException(
            status_code=404, detail=f"Deck {deck_id} not found"
        )
    return {"cards": d.to_serializable(), "top": d.top}


# returns cards equal to given count from the top of the deck
# TODO: check for valid deals
@app.post("/api/v2/deck/{deck_id}/deal/{count}")
async def api_v2_deck_deal(deck_id: str, count: int):
    d = deck_objects.get(deck_id)
    if d is None:
        raise HTTPException(
            status_code=404, detail=f"Deck {deck_id} not found"
        )
    if d.cards_left < count:
        raise HTTPException(
            status_code=500, detail=f"Deck has no cards left."
        )
    dealt_cards = d.draw(count)
    return {"cards": dealt_cards}

# resets state of game associated with deck_id, making new Deck object, expiration date, and a new hand
@app.post("/api/v2/deck/{deck_id}/restart-game")
async def api_v2_deck_restart_game(deck_id: str):
    if deck_id not in deck_objects:
        raise HTTPException(
            status_code=404, detail=f"Deck {deck_id} not found"
        )
    d = Deck()
    deck_objects[deck_id] = d
    expiration_time = time.mktime(
        (datetime.now() + timedelta(hours=DECK_ID_DURATION_HOURS)).timetuple()
    )  # converts datetime to unix timestamp
    expiration_times[deck_id] = expiration_time
    hand = d.draw(5)
    return {"hand": {"cards": hand}, "expires": expiration_time}

# Hand string should be in format "[rank][suit],[rank][suit],...", each card 
# represented by two characters without the brackets
@app.get("/api/v2/deck/get-ranking")
async def api_v2_deck_get_ranking(cards: str):
    ranking = get_ranking(cards)
    return {"ranking": ranking}

def get_ranking(cards: str) -> str:
    hand_list = cards.split(",")
    ranks = [card[0] for card in hand_list]
    suits = [card[1] for card in hand_list]

    # Count occurrences of ranks, suits
    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)

    # Check for flush
    is_flush = len(suit_counts) == 1

    # Check for straight
    #creates sorted ranks list to compare hand to
    sorted_ranks = sorted(set(ranks), key= lambda x: '234567890JQKA'.index(x))

    #compares 5 characters of comparison list to 5 characters in hand
    is_straight = '23456789TJQKA'[
        '23456789TJQKA'.index(sorted_ranks[0]):
        '23456789TJQKA'.index(sorted_ranks[0]) + 5] == ''.join(sorted_ranks)
    
    # Check for straight flush
    is_straight_flush = is_straight and is_flush
    
    # Check for four of a kind
    is_four_of_a_kind = 4 in rank_counts.values()
    
    # Check for full house
    is_full_house = sorted(rank_counts.values()) == [2, 3]
    
    # Check for three of a kind
    is_three_of_a_kind = 3 in rank_counts.values()
    
    # Check for two pairs
    is_two_pairs = list(rank_counts.values()).count(2) == 2
    
    # Check for one pair
    is_one_pair = 2 in rank_counts.values()
    
    # Determine the hand ranking
    if is_straight_flush:
        return "Straight Flush"
    elif is_four_of_a_kind:
        return "Four of a Kind"
    elif is_full_house:
        return "Full House"
    elif is_flush:
        return "Flush"
    elif is_straight:
        return "Straight"
    elif is_three_of_a_kind:
        return "Three of a Kind"
    elif is_two_pairs:
        return "Two Pairs"
    elif is_one_pair:
        return "One Pair"
    else:
        return "High Card"





app.mount("/", StaticFiles(directory="ui/dist", html=True), name="ui")
