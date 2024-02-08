import Api from "./Api.js";
import Hand from "./Hand.js";
import { useState, useCallback } from "react";

/**
   Note: For each game, we'll only allow the "Draw" to happen once.
   This means we should hide the "Draw" button after it is clicked.
   Better yet, let's change it to a different "Play Again" button that
   resets everything and plays another hand (with a new Deck).
**/
export default function App({ initialCards }) {
  const [cards, setCards] = useState(initialCards);
  const [selected, setSelected] = useState([]);

  function toggleSelected(index) {
    if (!selected.includes(index)) {
      setSelected(selected.concat([index]));
    } else {
      setSelected(selected.filter((elt) => elt !== index));
    }
  }

  // This function will be called when the Draw button is clicked
  const fetchNewCards = useCallback(async () => {
    console.log(`need to fetch ${selected.length} cards`);

    // fetch the new cards
    const fetchedCards = await Promise.all(
      /**
         This is some wacky functional programming magic. It's bad
         code, but you should practice understanding it.  Essentially,
         we're creating a new array of the appropriate length, then
         mapping over it to create an array of Promises, which we then
         await.

         Once API v2 is created, we can delete this and change it to a
         much simpler single API call that specifies the number of
         cards we want dealt.
       **/
      Array.from(Array(selected.length).keys()).map((arg, index) => {
        return Api.deal();
      }),
    );

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
  }, [selected, cards]);

  return (
    <div>
      <Hand
        cards={cards}
        selected={selected}
        onSelect={(index) => toggleSelected(index)}
      />
      <button onClick={async () => fetchNewCards(selected)}>Draw</button>
    </div>
  );
}
