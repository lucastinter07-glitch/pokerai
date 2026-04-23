"""Card utilities shared across UIs."""

RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
SUITS = ["s", "h", "d", "c"]  # spades, hearts, diamonds, clubs

SUIT_SYMBOLS = {
    "s": "♠",
    "h": "♥",
    "d": "♦",
    "c": "♣",
}

SUIT_COLORS = {
    "s": "#000000",  # black
    "c": "#000000",  # black
    "h": "#D40000",  # red
    "d": "#D40000",  # red
}


def all_cards() -> list[str]:
    """Return all 52 cards in a stable order."""
    return [r + s for r in RANKS for s in SUITS]


def format_card(card: str) -> str:
    """'Ah' -> 'A♥' for display."""
    if not card or len(card) != 2:
        return "?"
    return card[0] + SUIT_SYMBOLS[card[1]]


def card_color(card: str) -> str:
    """Return hex color string for a card's suit."""
    if not card or len(card) != 2:
        return "#888888"
    return SUIT_COLORS[card[1]]