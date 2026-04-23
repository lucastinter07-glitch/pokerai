"""
Hand range representation for poker.

A "range" is a collection of possible hands an opponent might have,
each weighted by probability. Real-world ranges come from notations like
"JJ+, AK, AQs" which this module parses into enumerable combos.
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Set, Iterable

# Rank order from weakest to strongest
RANKS = "23456789TJQKA"
SUITS = "shdc"  # spades, hearts, diamonds, clubs

# A combo is an ordered tuple of two card strings: ('As', 'Ks')
Combo = Tuple[str, str]


# ----------------------- Combo utilities -----------------------

def _rank_index(rank: str) -> int:
    """2 -> 0, 3 -> 1, ..., A -> 12."""
    return RANKS.index(rank)


def _canonical_combo(card1: str, card2: str) -> Combo:
    """
    Return the combo in canonical order: higher-ranked card first.
    For pairs, order by suit.
    """
    r1, s1 = card1[0], card1[1]
    r2, s2 = card2[0], card2[1]
    
    if _rank_index(r1) > _rank_index(r2):
        return (card1, card2)
    if _rank_index(r2) > _rank_index(r1):
        return (card2, card1)
    # Pair — order by suit
    if SUITS.index(s1) < SUITS.index(s2):
        return (card1, card2)
    return (card2, card1)


# ----------------------- Expanding notation to combos -----------------------

def expand_notation(code: str) -> Set[Combo]:
    """
    Expand a hand code like 'AKs', '77', 'KQo' into its set of specific combos.
    """
    code = code.strip()
    
    if len(code) == 2:
        r1, r2 = code[0], code[1]
        
        # Case A: a pair
        if r1 == r2:
            cards = [r1 + s for s in SUITS]
            combos = set()
            for i in range(len(cards)):
                for j in range(i + 1, len(cards)):
                    combos.add(_canonical_combo(cards[i], cards[j]))
            return combos
        
        # Case B: unspecified suitedness
        return expand_notation(r1 + r2 + "s") | expand_notation(r1 + r2 + "o")
    
    if len(code) == 3:
        r1, r2, kind = code[0], code[1], code[2]
        if kind not in ("s", "o"):
            raise ValueError(f"3-char code '{code}' must end in 's' or 'o'.")
        if r1 == r2:
            raise ValueError(f"Pair notation should be 2 chars, not '{code}'.")
        
        combos = set()
        if kind == "s":
            for s in SUITS:
                combos.add(_canonical_combo(r1 + s, r2 + s))
        else:
            for s1 in SUITS:
                for s2 in SUITS:
                    if s1 != s2:
                        combos.add(_canonical_combo(r1 + s1, r2 + s2))
        return combos
    
    raise ValueError(f"Unrecognized hand code: '{code}'")


# ----------------------- Plus notation -----------------------

def _expand_plus_notation(token: str) -> list[str]:
    """
    Expand '+' notation: 'JJ+' -> [JJ, QQ, KK, AA], 'ATs+' -> [ATs, AJs, AQs, AKs].
    """
    if not token.endswith("+"):
        return [token]
    base = token[:-1]
    
    if len(base) == 2:
        r1, r2 = base[0], base[1]
        if r1 == r2:
            start = _rank_index(r1)
            return [RANKS[i] * 2 for i in range(start, len(RANKS))]
        high = _rank_index(r1)
        low = _rank_index(r2)
        if low >= high:
            raise ValueError(f"Invalid '+' notation: {token}")
        return [r1 + RANKS[i] for i in range(low, high)]
    
    if len(base) == 3:
        r1, r2, kind = base[0], base[1], base[2]
        high = _rank_index(r1)
        low = _rank_index(r2)
        if low >= high:
            raise ValueError(f"Invalid '+' notation: {token}")
        return [r1 + RANKS[i] + kind for i in range(low, high)]
    
    raise ValueError(f"Cannot expand '+' notation: {token}")


# ----------------------- Dash notation -----------------------

def _expand_dash_notation(token: str) -> list[str]:
    """
    Expand '-' notation bounded on both ends.
    
    Examples:
        '22-55'     -> ['22', '33', '44', '55']
        'AJs-A9s'   -> ['AJs', 'ATs', 'A9s']
        'KQo-KTo'   -> ['KQo', 'KJo', 'KTo']
    
    For pairs and "fixed high rank" hands, the lower rank walks between bounds.
    """
    if "-" not in token:
        return [token]
    
    parts = token.split("-")
    if len(parts) != 2:
        raise ValueError(f"Invalid '-' notation (expected one dash): {token}")
    left, right = parts[0].strip(), parts[1].strip()
    
    # Case A: pair range like '22-TT'
    if len(left) == 2 and len(right) == 2 and left[0] == left[1] and right[0] == right[1]:
        low_idx = _rank_index(left[0])
        high_idx = _rank_index(right[0])
        if low_idx > high_idx:
            low_idx, high_idx = high_idx, low_idx
        return [RANKS[i] * 2 for i in range(low_idx, high_idx + 1)]
    
    # Case B: fixed-high, varying-low suited/offsuit range like 'AJs-A9s'
    if len(left) == 3 and len(right) == 3:
        if left[0] != right[0]:
            raise ValueError(f"Dash-range high ranks must match: {token}")
        if left[2] != right[2]:
            raise ValueError(f"Dash-range suitedness must match: {token}")
        high_rank = left[0]
        kind = left[2]
        low_rank_a = _rank_index(left[1])
        low_rank_b = _rank_index(right[1])
        lo, hi = min(low_rank_a, low_rank_b), max(low_rank_a, low_rank_b)
        return [high_rank + RANKS[i] + kind for i in range(lo, hi + 1)]
    
    raise ValueError(f"Unsupported '-' notation format: {token}")


# ----------------------- Parsing range strings -----------------------

def parse_range_string(raw: str) -> Dict[Combo, float]:
    """
    Parse a range string into a dict of combo -> weight.
    
    Supports:
    - Plain hands: 'AA', 'AKs', 'KJo'
    - Unspecified suits: 'AK' (= AKs + AKo)
    - Plus notation: 'JJ+', 'ATs+', 'AT+'
    - Dash notation: '22-TT', 'AJs-A9s'
    - Weights: 'AKs:0.5'
    - Comma-separated lists: 'JJ+, AK, AQs:0.5'
    """
    result: Dict[Combo, float] = {}
    
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        
        if ":" in token:
            code, weight_str = token.split(":")
            weight = float(weight_str)
        else:
            code = token
            weight = 1.0
        
        code = code.strip()
        
        # Expand dash first (e.g., '22-TT' -> ['22','33',...,'TT'])
        # Then expand plus for each resulting token
        # Then expand each resulting hand code to combos
        dash_expanded = _expand_dash_notation(code)
        for subtoken in dash_expanded:
            for hand_code in _expand_plus_notation(subtoken):
                for combo in expand_notation(hand_code):
                    result[combo] = weight
    
    return result


# ----------------------- The Range class -----------------------

@dataclass
class Range:
    """
    A weighted set of hand combos representing opponent's possible holdings.
    """
    combos: Dict[Combo, float] = field(default_factory=dict)
    
    @classmethod
    def from_string(cls, raw: str) -> "Range":
        return cls(combos=parse_range_string(raw))
    
    def remove_blocked(self, blocked_cards: Iterable[str]) -> "Range":
        blocked = set(blocked_cards)
        filtered = {
            combo: weight
            for combo, weight in self.combos.items()
            if combo[0] not in blocked and combo[1] not in blocked
        }
        return Range(combos=filtered)
    
    def total_combos(self) -> float:
        return sum(self.combos.values())
    
    def num_combos(self) -> int:
        return len(self.combos)
    
    def is_empty(self) -> bool:
        return len(self.combos) == 0
    
    def __repr__(self) -> str:
        return f"Range({self.num_combos()} combos, total weight {self.total_combos():.1f})"
    

    