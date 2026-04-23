"""
Opponent range construction based on position and betting action.

These ranges are simplified 6-max NL cash game ranges at 100bb depth,
based on modern solver-derived strategies. They're not GTO-perfect but
provide a solid baseline for realistic opponent modeling.
"""

from poker_ai.core.hand_range import Range


# ============================================================
# Preflop opening ranges (raise first in)
# ============================================================
#
# What villains raise with when the action folds to them.

OPEN_RAISE_RANGES = {
    # UTG: ~15% of hands — tightest position
    "UTG": "66+, ATs+, KJs+, QJs, JTs, AJo+, KQo",
    
    # MP: ~17% — slightly wider
    "MP": "55+, A9s+, KTs+, QTs+, J9s+, T9s, AJo+, KJo+, QJo",
    
    # CO: ~25% — opens up significantly
    "CO": "44+, A7s+, K9s+, Q9s+, J8s+, T8s+, 97s+, 87s, 76s, ATo+, KTo+, QTo+, JTo",
    
    # BTN: ~45% — widest position
    "BTN": ("22+, A2s+, K5s+, Q7s+, J7s+, T7s+, 97s+, 86s+, 75s+, 65s, 54s, "
            "A7o+, K9o+, Q9o+, J9o+, T9o"),
    
    # SB: ~40% — wide because only BB left to play against
    "SB": ("22+, A2s+, K7s+, Q8s+, J8s+, T8s+, 97s+, 86s+, 75s+, 65s, "
           "A8o+, K9o+, Q9o+, J9o+"),
    
    # BB: if folded to — same as SB essentially, but BB rarely "opens" because
    # everyone already folded. Use sparingly.
    "BB": "22+, A2s+, K5s+, Q7s+, J7s+, T7s+, 97s+, 87s, 76s, ATo+, KTo+",
}


# ============================================================
# 3-bet ranges (reraise preflop)
# ============================================================
#
# These ranges represent what villain reraises with after facing an open.
# Tighter 3-bet ranges face earlier-position raisers; wider ranges face later.

THREE_BET_VS_UTG = "QQ+, AKs, AKo"  # Very tight
THREE_BET_VS_MP = "JJ+, AQs+, AKo"
THREE_BET_VS_CO = "TT+, AJs+, AQo+, KQs"
THREE_BET_VS_BTN = "99+, ATs+, KJs+, AJo+, KQo"
THREE_BET_VS_SB = "99+, ATs+, KJs+, AJo+"


# ============================================================
# Calling ranges (flat-call a preflop raise)
# ============================================================
#
# When villain just calls a raise rather than 3-betting, their range is
# typically medium-strength hands — too good to fold but not strong enough to 3-bet.

CALL_VS_UTG_OPEN = "22-TT, AJs-ATs, KQs, KJs, QJs, JTs, T9s, 98s, 87s, AQo, AJo, KQo"
CALL_VS_MP_OPEN = "22-TT, A9s-ATs, K9s+, Q9s+, J9s+, T9s, 98s, 87s, 76s, AJo-ATo, KJo+, QJo"
CALL_VS_CO_OPEN = "22-99, A2s-A9s, K9s+, Q9s+, J8s+, T8s+, 97s+, 86s+, 76s, 65s, ATo+, KTo+, QTo+, JTo"
CALL_VS_BTN_OPEN = "22-99, A2s-A9s, K7s+, Q8s+, J8s+, T8s+, 97s+, 86s+, 75s+, 65s, 54s, A8o+, K9o+, Q9o+, J9o+"


# ============================================================
# Public API
# ============================================================

def opening_range(position: str) -> Range:
    """
    Return the opening raise range for a given position.
    These are hands a competent 6-max player raises first in from this seat.
    """
    raw = OPEN_RAISE_RANGES.get(position)
    if raw is None:
        raise ValueError(f"Unknown position: {position}")
    return Range.from_string(raw)


def three_bet_range(raiser_position: str) -> Range:
    """
    Return the 3-bet range against an opener from a specific position.
    Example: three_bet_range('UTG') returns the range villains reraise with
    when facing a UTG opener.
    """
    mapping = {
        "UTG": THREE_BET_VS_UTG,
        "MP": THREE_BET_VS_MP,
        "CO": THREE_BET_VS_CO,
        "BTN": THREE_BET_VS_BTN,
        "SB": THREE_BET_VS_SB,
    }
    raw = mapping.get(raiser_position)
    if raw is None:
        raise ValueError(f"No 3-bet range defined for raiser position: {raiser_position}")
    return Range.from_string(raw)


def calling_range(raiser_position: str) -> Range:
    """
    Return the flat-call range against an opener from a specific position.
    These are hands villains call (rather than 3-bet or fold) after a raise.
    """
    mapping = {
        "UTG": CALL_VS_UTG_OPEN,
        "MP": CALL_VS_MP_OPEN,
        "CO": CALL_VS_CO_OPEN,
        "BTN": CALL_VS_BTN_OPEN,
    }
    raw = mapping.get(raiser_position)
    if raw is None:
        raise ValueError(f"No calling range defined for raiser position: {raiser_position}")
    return Range.from_string(raw)