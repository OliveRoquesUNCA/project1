import { StrictMode, React, useState, useCallback } from "react";
import { createRoot } from "react-dom/client";
import Api from "./Api.js";
import App from "./App.js";
import { "Deck" as Deck } from "./Deck.js";

async function main() {
  // const newDeck = await Api.deck();
  // console.log(newDeck);

  const fetchedDeck = await Api.deck("1234");
  console.log(fetchedDeck);

  let deck = new Deck();
  let d = sessionStorage.getItem("deck");
  let initialCards = sessionStorage.getItem("hand");
  let ended = false;
  if (d) d = JSON.parse(d);
  if (initialCards) JSON.parse(initialCards);
  if (!d || !initialCards || new Date() < Date(d.expiry)) {
    console.log("no session storage");
    initialCards = await deck.init();
    sessionStorage.setItem("hand", JSON.stringify(initialCards));
  } else {
    console.log("has session storage");
    initialCards = await deck.init(d.id, new Date(d.expiry));
    if (!initialCards) {
      // session storage worked
      initialCards = JSON.parse(sessionStorage.getItem("hand"));
      ended = sessionStorage.getItem("dealt");
      if (!ended) ended = false;
    } else {
      ended = false;
    }
  }

  deck.setSessionStorage();
  console.log("main deck: " + deck);

  // create React elements
  const root = createRoot(document.getElementById("app"));
  root.render(
    <App initialCards={initialCards} initialDeck={deck} initialEnded={ended} />,
  );
}

window.onload = main;
