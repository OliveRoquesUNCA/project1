# API Documentation

The poker server runs a poker game with which the client interacts. The
interaction is done over HTTP for ease of use, but it is worth noting that the
entirety of this interaction is stateful and that very little (if anything)
can be meaningfully cached.

## Transport and Session

The data sent and received by the server will be with JSON. Attached to many
requests will be a session ID (SID). This will be attached in the
`Authorization` header after a request to the `/new-game` endpoint, detailed
below.

The session ID is a random string returned by the server. There are no
guarantees as to the string's contents.

## Data Types

A few types will be returned by the API, which is easier to define up front.

### Card

A card consists of an object with `rank` and `suit` fields.

The rank is a string containing one of:

- A number between 1-10
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
- "ranking": the ranking of the poker hand, one of:
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

## Endpoints

Each endpoint takes in a number of parameters, which are provided with POST
data in JSON format, or, if it is a GET request, is serialized as key-value
query parameters.

If an endpoint throws an error, it is to return the following structure
as data alongside the relevant HTTP status code:

```json
{
    "message": "Error message (can be anything)."
}
```

Where the "message" field is replaced with a relevant error message,
displayable to the user.

### POST /new-game
The client asks for a new session.

Parameters: none.

Returns a unique session ID as a string, a hard-capped expiration date in
milliseconds since the UNIX epoch as an integer, and a 5-card hand in a
structure as described above. The intent is for the client to use this
information for their own session.

An example of what this endpoint might return is the following:

```json
{
    "session_id": "123456",
    "expires": 1707813721233,
    "hand": {
        "cards": [
            {"rank": "A", "suit": "S"},
            {"rank": "K", "suit": "S"},
            {"rank": "Q", "suit": "S"},
            {"rank": "J", "suit": "S"},
            {"rank": "10", "suit": "S"}
        ],
        "ranking": "Royal Flush"
    }
}
```

This endpoint may return an error if for some reason it couldn't generate
the requisite information.

### POST /deal-cards
Client discards a number of cards and requests a re-deal.
This number can be zero, but it is REQUIRED to advance the game state.

Parameters: list of cards in the "cards" field. Can be empty.
Requires authorization.

Returns the user's new 5-card hand after cards are re-dealt in the "hand"
field.

Example request and response:

```json
{
    "cards": [
        {"rank": "3", "suit": H}
    ]
}
```

Response:

```json
{
    "hand": {
        "cards": [
            {"rank": "A", "suit": "S"},
            {"rank": "K", "suit": "S"},
            {"rank": "Q", "suit": "S"},
            {"rank": "J", "suit": "S"},
            {"rank": "10", "suit": "S"}
        ],
        "ranking": "Royal Flush"
    }
}
```

This endpoint will error if the session ID in the `Authorization` header
isn't found or if the cards requested aren't in the user's hand.

### GET /state
Client asks for a reminder of current game state.

Parameters: none. Requires authorization.

Server returns a 5-card hand and whether cards have been re-dealt,
which in this game means the game has ended.

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
        ],
        "ranking": "Royal Flush"
    },
    "has_redealt": true
}
```

### POST /restart-game
Client asks to restart the game.

Parameters: none. Requires authentication.

This endpoint allows a client to reuse the same session for multiple games.
The server will return a new 5-card hand and a new expiration date for the
session ID.

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
        ],
        "ranking": "Royal Flush"
    },
    "expires": 1707886800000
}
```
