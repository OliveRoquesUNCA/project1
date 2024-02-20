#!/bin/bash

set -e

set -x


#curl -w "\n" -X POST localhost:8000/api/v2/deck/new | jq -r '.deck_id, .expires, .hand'
deck_id=$(curl -s -X POST localhost:8000/api/v2/deck/new | jq -r '.deck_id')
curl -w "\n" localhost:8000/api/v2/deck/$deck_id | jq -r '.cards, .top'
curl -w "\n" -X POST localhost:8000/api/v2/deck/$deck_id/deal/4 | jq -r '.cards'
curl -w "\n" -X POST localhost:8000/api/v2/deck/$deck_id/restart-game | jq -r '.hand, .expires'
curl -w "\n" localhost:8000/api/v2/deck/get-ranking?cards=2C,3C,4C,5C,6C | jq -r '.ranking'

# The `-w "\n"' argument adds a new line to the end of curl's output


# You may want to parse the resulting JSON. The `jq` command is good
# for that. You can install it with `apt` in Linux or homebrew in
# Mac. I've commented out the following lines in case you don't have
# it installed.

# The `-s` option makes curl silence it's status output when piping
# The `-r` option to jq makes it return a string without quotes


