import asyncio
import asyncpg
import secrets
import string
import random
import time
import json
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
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


# @app.post("/api/v2/get-state")


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


app.mount("/", StaticFiles(directory="ui/dist", html=True), name="ui")
