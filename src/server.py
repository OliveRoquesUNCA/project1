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

def generate_unique_deck_id(length=20):
    alphabet = string.ascii_letters + string.digits
    while True:
        deck_id = ''.join(secrets.choice(alphabet) for _ in range(length))
        if deck_id not in deck_objects:
            return deck_id


@app.get("/api/v1/hello")
async def api_v1():
    return {"message": "Hello World!"}


@app.get("/api/v1/deal")
async def api_v1_deal():
    return {"rank": random.choice(RANKS), "suit": random.choice(SUITS)}

#creates new deck, adds deck ID and associated deck object to dictionary, generates new expiration time associated with it
@app.post("/api/v2/deck/new")
async def api_v2_deck_new():
    d = Deck()
    deck_id = generate_unique_deck_id()
    deck_objects[deck_id] = d
    expiration_time = time.mktime((datetime.now() + timedelta(hours=24)).timetuple()) #converts datetime to unix timestamp
    expiration_times[deck_id] = expiration_time
    hand = d.draw(5)  
    return {
            "deck_id": deck_id,
            "expires": expiration_time,
            "hand": { 
                "cards": [hand]
                }
            }

#returns deck associated with given parameter deck_id
@app.get("/api/v2/deck/{deck_id}")
async def api_v2_deck(deck_id: str):
    if(deck_id not in deck_objects):
        raise HTTPException(status_code=404, detail=f"Deck {deck_id} not found")
    return deck_objects.get(deck_id)

#returns cards equal to given count from the top of the deck
#TODO: check for valid deals
@app.post("/api/v2/deck/{deck_id}/deal")
async def api_v2_deck_deal(deck_id: str, count: int):
    if(deck_id not in deck_objects):
        raise HTTPException(status_code=404, detail=f"Deck {deck_id} not found")
    d = deck_objects.get(deck_id)
    dealt_cards = d.draw(count)
    return {
        "dealt_cards": { 
        "cards": [dealt_cards] 
        }
    }
    

#@app.post("/api/v2/get-state")

#resets state of game associated with deck_id, making new Deck object, expiration date, and a new hand
@app.post("/api/v2/deck/{deck_id}/restart-game")
async def api_v2_deck_restart_game(deck_id: str):
    d = Deck()
    deck_objects[deck_id] = d
    expiration_time = time.mktime((datetime.now() + timedelta(hours=24)).timetuple()) #converts datetime to unix timestamp
    expiration_times[deck_id] = expiration_time
    hand = d.draw(5)
    return {
        "hand": {
        "cards": [hand]
        },
        "expires": expiration_time
    }


app.mount("/", StaticFiles(directory="ui/dist", html=True), name="ui")
