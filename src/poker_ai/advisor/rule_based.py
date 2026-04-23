from poker_ai.advisor.base import Advisor
from poker_ai.core.game_state import GameState

# Simplified preflop opening ranges by position.
# These are "hand codes" — AKs = Ace-King suited, 77 = pocket sevens, etc.
OPENING_RANGES = {
    "UTG": {"AA","KK","QQ","JJ","TT","99","AKs","AQs","AJs","AKo"},
    "MP":  {"AA","KK","QQ","JJ","TT","99","88","AKs","AQs","AJs","ATs","KQs","AKo","AQo"},
    "CO":  {"AA","KK","QQ","JJ","TT","99","88","77","AKs","AQs","AJs","ATs","A9s","KQs","KJs","QJs","AKo","AQo","AJo"},
    "BTN": {"AA","KK","QQ","JJ","TT","99","88","77","66","55","AKs","AQs","AJs","ATs","A9s","A8s","A7s","A6s","A5s","KQs","KJs","KTs","QJs","QTs","JTs","T9s","AKo","AQo","AJo","ATo","KQo","KJo","QJo"},
    "SB":  {"AA","KK","QQ","JJ","TT","99","88","77","AKs","AQs","AJs","ATs","KQs","KJs","QJs","AKo","AQo","AJo"},
    "BB":  set(),  # BB defends by calling, not opening
}


def hand_to_code(hole_cards: list[str]) -> str:
    """
    Convert ['Ah', 'Ks'] to 'AKs' (suited) or 'AKo' (offsuit) or 'AA' (pair).
    """
    rank1, suit1 = hole_cards[0][0], hole_cards[0][1]
    rank2, suit2 = hole_cards[1][0], hole_cards[1][1]
    
    # Rank order for canonical form (higher rank first)
    order = "23456789TJQKA"
    if order.index(rank1) < order.index(rank2):
        rank1, rank2 = rank2, rank1
        suit1, suit2 = suit2, suit1
    
    if rank1 == rank2:
        return rank1 + rank2            # Pair, e.g., "AA"
    suited = "s" if suit1 == suit2 else "o"
    return rank1 + rank2 + suited       # e.g., "AKs" or "AKo"


class RuleBasedAdvisor(Advisor):
    """Phase 1: Simple preflop advisor using fixed opening ranges."""
    
    def recommend(self, state: GameState) -> dict:
        code = hand_to_code(state.hole_cards)
        
        # state.position is now a Position enum — extract the string key
        pos_key = state.position.value if hasattr(state.position, "value") else state.position
        opening_range = OPENING_RANGES.get(pos_key, set())
        
        action = "raise" if code in opening_range else "fold"
        in_range = code in opening_range
        
        return {
            "action": action,
            "reasoning": f"Hand {code} {'is' if in_range else 'is not'} in the {pos_key} opening range.",
            "equity": None,
            "pot_odds": state.pot_odds,
        }