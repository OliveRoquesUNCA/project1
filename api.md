# API Documentation

The poker server runs a poker game with which the client interacts. The
interaction is done over HTTP for ease of use, but it is worth noting
that the entirety of this interaction is stateful and that very little
(if anything) can be meaningfully cached.

## Transport and Session

The data sent and received by the server will be with JSON.
Most requests require a deck ID; this can be obtained through the
`/api/v2/deck/new` endpoint below.

The deck ID is a random string returned by the server. There are no
guarantees as to the string's contents besides URL safety.

## Data Types

A few types will be returned by the API, which is easier to define up front.

### Card

A card consists of an object with `rank` and `suit` fields.

The rank is a string containing one of:

- A number between 2-10
- J, Q, K, or A

The suit is one of `CHSD`.

For example, the following would represent a king of clubs:

```json
{
    "rank": "K",
    "suit": "C"
}
```

Or the following would represent a three of spades:

```json
{
    "rank": "3",
    "suit": "S"
}
```

### Hand

A 5-card hand consists of the following structure:

- "cards": a list of cards of length 5
- (Optional) "ranking": the ranking of the poker hand, one of:
    1.  `Royal Flush`
    2.  `Straight Flush`
    3.  `Four of a Kind`
    4.  `Full House`
    5.  `Flush`
    6.  `Straight`
    7.  `Three of a Kind`
    8.  `Two Pair`
    9.  `One Pair`
    10. `High Card`

The following is an example of a 5-card hand:

```json
{
    "cards": [
        {"rank": "A", "suit": "S"},
        {"rank": "K", "suit": "S"},
        {"rank": "Q", "suit": "S"},
        {"rank": "J", "suit": "S"},
        {"rank": "10", "suit": "S"}
    ],
    "ranking": "Royal Flush"
}
```

The ranking *may not be present*. If the API doesn't return a value,
clients are expected to generate one themselves if they wish.

## Endpoints

Each endpoint takes in a number of parameters, which are provided with
POST data in JSON format, or, if it is a GET request, is serialized as
key-value query parameters.

If an endpoint throws an error, it is to return the following structure
as data alongside the relevant HTTP status code:

```json
{
    "detail": "Error message (can be anything)."
}
```

Where the "message" field is replaced with a relevant error message,
displayable to the user.

### POST /api/v2/deck/new
The client asks for a new deck.

Parameters: none.

Returns a unique deck ID as a string, a hard-capped expiration date
in seconds since the UNIX epoch as a float, and a 5-card hand in a
structure as described above. The intent is for the client to use this
information for their own game.

An example of what this endpoint might return is the following:

```json
{
    "deck_id": "123456",
    "expires": 1707813721233.0,
    "hand": {
        "cards": [
            {"rank": "A", "suit": "S"},
            {"rank": "K", "suit": "S"},
            {"rank": "Q", "suit": "S"},
            {"rank": "J", "suit": "S"},
            {"rank": "10", "suit": "S"}
        ]
    }
}
```

This endpoint may return an error if for some reason it couldn't generate
the requisite information.

### POST /api/v2/{deck_id}/deal/{count}
Client discards a number of cards and requests a re-deal.
This number can be zero, but it is REQUIRED to advance the game state.

Parameters: deck ID, count, in the URL.

Returns `count` new cards.

Example request and response:

Request: `/api/v2/--dshrdshGGHH/2`

Response:

```json
{
    "cards": [
        {"rank": "A", "suit": "S"},
        {"rank": "K", "suit": "S"}
    ]
}
```

This endpoint will error if the deck ID isn't found.

### GET /api/v2/deck/{deck_id}
Client asks for a reminder of the entire deck.

Parameters: deck ID.

Server returns a list of all cards in the deck, past and present, and
the current top of the deck.

Example response:

```json
{
    "cards": [
        {"rank": "3", "suit": "H"},
        {"rank": "A", "suit": "S"},
        // ...
        {"rank": "K", "suit": "C"}
    ],
    "top": 30
}
```

### POST /api/v2/deck/{deck_id}/restart-game
Client asks to restart the game.

Parameters: deck ID.

This endpoint allows a client to reuse the same deck ID for multiple
games. The server will return a new 5-card hand and a new expiration
date for the deck ID.

Example response:

```json
{
    "hand": {
        "cards": [
            {"rank": "A", "suit": "S"},
            {"rank": "K", "suit": "S"},
            {"rank": "Q", "suit": "S"},
            {"rank": "J", "suit": "S"},
            {"rank": "10", "suit": "S"}
        ]
    },
    "expires": 1707886800000.0
}
```
