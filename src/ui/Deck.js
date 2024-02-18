export class DeckNotFoundError extends Error {
    constructor(message) {
        super(message);
        this.name = "DeckNotFoundError";
    }
}

export class Deck {
    deckId;
    expiry;

    async init(id, expiry) {
        if (
            typeof id === "string" &&
            typeof expiry === "object" &&
            new Date() < expiry
        ) {
            this.deckId = id;
            this.expiry = expiry;
            const testresp = await fetch(`/api/v2/deck/${this.deckId}`, {
                method: "HEAD",
            });
            if (testresp.ok) {
                console.log("session storage worked.");
                return;
            }
        }
        const resp = await fetch("/api/v2/deck/new", { method: "POST" });
        const response = await resp.json();
        console.log(response);
        this.deckId = response.deck_id;
        this.expiry = new Date(response.expires * 1000);
        return response.hand.cards;
    }

    clone() {
        let d = new Deck();
        d.init(this.deckId, this.expiry);
        return d;
    }

    // WARNING: stateful
    setSessionStorage() {
        sessionStorage.setItem(
            "deck",
            JSON.stringify({
                id: this.deckId,
                expiry: this.expiry.getTime(),
            }),
        );
    }

    /*
     * Throws an error if deck is expired.
     */
    check_expiry() {
        if (new Date() > this.expiry) {
            throw new DeckNotFoundError("deck is expired");
        }
    }

    async deal(count) {
        if (typeof count !== "number")
            throw new Error("count must be a number.");
        this.check_expiry();

        const resp = await fetch(`/api/v2/deck/${this.deckId}/deal/${count}`, {
            method: "POST",
        });
        const response = await resp.json();
        return response.cards;
    }

    async restart() {
        this.check_expiry();
        const resp = await fetch(`/api/v2/deck/${this.deckId}/restart-game`, {
            method: "POST",
        });
        const response = await resp.json();
        this.expiry = new Date(response.expires * 1000);
        return response.hand.cards;
    }
}
