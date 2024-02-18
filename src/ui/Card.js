export default function Card({ rank, suit, selected, onClick }) {
  if (rank == 10) rank = "0";
  return (
    <img
      className="card"
      onClick={onClick}
      src={
        selected
          ? "https://deckofcardsapi.com/static/img/back.png"
          : `https://deckofcardsapi.com/static/img/${rank}${suit}.png`
      }
    ></img>
  );
}
