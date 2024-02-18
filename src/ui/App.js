import Api from "./Api.js";
import { Deck, DeckExpiredError } from "./Deck.js";
import Hand from "./Hand.js";
import { useState, useCallback, useEffect } from "react";

/**
   Note: For each game, we'll only allow the "Draw" to happen once.
   This means we should hide the "Draw" button after it is clicked.
   Better yet, let's change it to a different "Play Again" button that
   resets everything and plays another hand (with a new Deck).
**/
export default function App({ initialCards, initialDeck, initialEnded }) {
  const [cards, setCards] = useState(initialCards);
  const [selected, setSelected] = useState([]);
  const [deck, setDeck] = useState(initialDeck);
  const [dealt, setDealt] = useState(initialEnded);
  const [error, setError] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  console.log("initialDeck: " + initialDeck);
  console.log("current deck: " + deck);
  console.log("setDeck? " + setDeck);

  useEffect(() => {
    if (error) {
      // restart from scratch
      let d = new Deck();
      d.init().then((result) => {
        d.setSessionStorage();
        setCards(result);
        setDeck(d);
        setError(false);
      });
      setSelected([]);
      setDealt(false);
    }
  }, [initialCards, initialDeck, cards, selected, deck, dealt, error]);

  useEffect(() => {
    if (!error) {
      console.log("storing deck: " + deck.deckId);
      console.log(deck.expiry);
      deck.setSessionStorage();
      sessionStorage.setItem("hand", JSON.stringify(cards));
      sessionStorage.setItem("dealt", JSON.stringify(dealt));
    }
  }, [initialCards, initialDeck, cards, selected, deck, dealt, error]);

  function toggleSelected(index) {
    if (dealt) {
      setSelected([]);
      return;
    }
    const newSelected = selected.concat([index]);
    const remaining = [0, 1, 2, 3, 4].filter((e) => !newSelected.includes(e));
    if (
      (selected.length >= 3 &&
        (remaining.length == 0 || cards[remaining[0]].rank !== "A")) ||
      selected.includes(index)
    ) {
      setSelected(selected.filter((elt) => elt !== index));
    } else {
      setSelected(newSelected);
    }
  }

  // This function will be called when the Draw button is clicked
  const fetchNewCards = useCallback(async () => {
    console.log(`need to fetch ${selected.length} cards`);

    // fetch the new cards
    let fetchedCards;
    try {
      fetchedCards = await deck.deal(selected.length);
    } catch (e) {
      console.log(e);
      setErrorMsg(e.message);
      setError(true);
      return;
    }
    // let's print out the fetched cards
    console.log(fetchedCards);

    // create the new hand with the fetched cards replacing the
    // selected cards
    let fetchedCardsIndex = 0;
    const newCards = cards.map((card, index) => {
      if (selected.includes(index)) {
        // we map this card to the new card, and increment
        // our fetchedCardsIndex counter
        return fetchedCards[fetchedCardsIndex++];
      } else {
        return card;
      }
    });

    // update state, causing a re-render
    setCards(newCards);
    setSelected([]);
    setDeck(deck.clone());
    setDealt(true);
    setError(false);
    setErrorMsg("");
  }, [selected, deck, cards, error]);

  const restartGame = useCallback(async () => {
    try {
      let cards = await deck.restart();
      setCards(cards);
      setDeck(deck.clone());
      setDealt(false);
      setSelected([]);
    } catch (e) {
      console.log(e);
      setErrorMsg(e.message);
      setError(true);
      return;
    }
  }, [cards, deck, error]);

  const dealButton = dealt ? (
    ""
  ) : (
    <button onClick={async () => fetchNewCards(selected)}>Draw</button>
  );
  const errorDisplay = errorMsg ? (
    <p>An error occurred. {errorMsg}. Restarting game.</p>
  ) : (
    ""
  );
  const restartGameButton = dealt ? (
    <button onClick={async () => restartGame()}>Restart</button>
  ) : (
    ""
  );

  return (
    <div>
      <Hand
        cards={cards}
        selected={selected}
        onSelect={(index) => toggleSelected(index)}
      />
      {dealButton}
      {errorDisplay}
      {restartGameButton}
    </div>
  );
}
