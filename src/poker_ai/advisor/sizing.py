"""
Bet sizing recommendations for poker decisions.

Uses a tiered approach: rather than computing exact bet sizes, we pick a
named tier (SMALL, MEDIUM, LARGE, etc.) based on the situation, then map
that tier to an actual BB amount given the pot and bet context.

Tiered sizing is easier to explain ("bet small — thin value") and easier
to tune than continuous percentage-of-pot calculations.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


# ============================================================
# Bet tier definitions
# ============================================================

class BetTier(Enum):
    """
    Named categories of bet sizings, ordered roughly small-to-large.
    
    Each tier maps to a percentage of pot (postflop) or a multiplier
    (preflop / raises). The actual BB amount is computed at sizing time.
    """
    
    # Postflop "opening the betting" tiers
    SMALL_BET = "small_bet"          # ~33% pot
    MEDIUM_BET = "medium_bet"        # ~50% pot
    LARGE_BET = "large_bet"          # ~75% pot
    OVERBET = "overbet"              # ~150% pot
    
    # Postflop "raising an existing bet" tiers
    MIN_RAISE = "min_raise"          # Min legal raise (villain_bet * 2)
    STANDARD_RAISE = "standard_raise"  # ~2.5x villain's bet
    LARGE_RAISE = "large_raise"      # ~3.5x villain's bet
    ALL_IN = "all_in"                # Shove
    
    # Preflop tiers
    PREFLOP_OPEN = "preflop_open"    # 2.5bb default open
    THREE_BET = "three_bet"          # 3x the open (IP) or 3.5x (OOP)


# ============================================================
# Mapping tiers to percentages / multipliers
# ============================================================
#
# Postflop "bet" tiers are expressed as percentage of current pot.
# Postflop "raise" tiers are expressed as multiplier of villain's bet.
# Preflop tiers are special-cased.

POSTFLOP_BET_FRACTIONS = {
    BetTier.SMALL_BET: 0.33,
    BetTier.MEDIUM_BET: 0.50,
    BetTier.LARGE_BET: 0.75,
    BetTier.OVERBET: 1.50,
}

POSTFLOP_RAISE_MULTIPLIERS = {
    BetTier.MIN_RAISE: 2.0,
    BetTier.STANDARD_RAISE: 2.5,
    BetTier.LARGE_RAISE: 3.5,
    # ALL_IN handled specially (use stack)
}


# ============================================================
# The BetSizing result
# ============================================================

@dataclass
class BetSizing:
    """
    A complete sizing recommendation.
    
    - `tier`: the named category (for reasoning text)
    - `amount`: the concrete BB amount to bet/raise to
    - `reasoning`: why this size
    """
    tier: BetTier
    amount: float
    reasoning: str
    
    def __repr__(self) -> str:
        return f"BetSizing({self.tier.value}, {self.amount:.1f}bb)"


# ============================================================
# Sizing helpers (low-level math)
# ============================================================

def size_postflop_bet(tier: BetTier, pot: float) -> float:
    """
    Compute the BB amount for a postflop bet at a given tier.
    
    Example: pot=10, tier=MEDIUM_BET (50% pot) -> 5.0bb
    """
    if tier not in POSTFLOP_BET_FRACTIONS:
        raise ValueError(f"Tier {tier} is not a postflop bet tier")
    
    fraction = POSTFLOP_BET_FRACTIONS[tier]
    return round(pot * fraction, 1)


def size_postflop_raise(
    tier: BetTier,
    villain_bet: float,
    stack: float,
) -> float:
    """
    Compute the BB amount for a postflop raise at a given tier.
    
    Example: villain bets 5bb, tier=STANDARD_RAISE (2.5x) -> raise to 12.5bb
    
    All-in is capped by hero's stack.
    """
    if tier == BetTier.ALL_IN:
        return round(stack, 1)
    
    if tier not in POSTFLOP_RAISE_MULTIPLIERS:
        raise ValueError(f"Tier {tier} is not a postflop raise tier")
    
    multiplier = POSTFLOP_RAISE_MULTIPLIERS[tier]
    amount = villain_bet * multiplier
    
    # Never raise more than the hero can put in
    return round(min(amount, stack), 1)


def size_preflop_open(position: str) -> float:
    """
    Standard preflop open sizing.
    
    For 100bb cash games, 2.5bb is the modern standard. Slight variations
    by position (some players use 2.2bb from BTN, 3bb from UTG).
    """
    # Phase 5.2 will refine this; for now, simple default
    return 2.5


def size_preflop_three_bet(
    open_size: float,
    hero_in_position: bool,
) -> float:
    """
    Standard 3-bet sizing over a preflop raise.
    
    In-position 3-bets are smaller (3x the open) because position is leverage.
    Out-of-position 3-bets are larger (3.5x to 4x) to compensate for being OOP.
    """
    multiplier = 3.0 if hero_in_position else 3.5
    return round(open_size * multiplier, 1)

# ============================================================
# Preflop sizing decision logic
# ============================================================

# Position ordering — higher index = later position = more in position
POSITION_ORDER = ["UTG", "MP", "CO", "BTN", "SB", "BB"]

# Standard open sizes by position (in BB)
PREFLOP_OPEN_SIZES = {
    "UTG": 2.5,
    "MP":  2.5,
    "CO":  2.2,
    "BTN": 2.2,
    "SB":  2.5,
    "BB":  None,  # BB doesn't open
}

# 3-bet multipliers (applied to open size)
THREE_BET_MULTIPLIER_IP = 3.0    # In position
THREE_BET_MULTIPLIER_OOP = 3.5   # Out of position

# 4-bet target: this fraction of the effective stack
FOUR_BET_FRACTION = 0.22         # ~22bb over a 8bb 3-bet at 100bb depth

# When SPR after a 4-bet would drop below this, just shove
SPR_SHOVE_THRESHOLD = 3.0


# Postflop position order: SB acts first, then BB, then UTG, MP, CO, BTN last
# This is different from preflop order where BB acts last
POSTFLOP_POSITION_ORDER = ["SB", "BB", "UTG", "MP", "CO", "BTN"]

def is_in_position(hero_pos: str, villain_pos: str) -> bool:
    """
    Return True if hero acts after villain postflop (hero is in position).
    
    Postflop order: SB → BB → UTG → MP → CO → BTN
    BTN always acts last and is always in position.
    SB always acts first and is always out of position.
    """
    hero_idx = POSTFLOP_POSITION_ORDER.index(hero_pos) if hero_pos in POSTFLOP_POSITION_ORDER else 3
    villain_idx = POSTFLOP_POSITION_ORDER.index(villain_pos) if villain_pos in POSTFLOP_POSITION_ORDER else 3
    return hero_idx > villain_idx


def preflop_open_sizing(position: str, effective_stack: float) -> BetSizing:
    """
    Return the recommended open raise sizing from a given position.
    
    If stack is shallow (< 15bb), just shove — standard open sizing 
    doesn't make sense short-stacked.
    """
    # Short stack: shove preflop
    if effective_stack < 15:
        return BetSizing(
            tier=BetTier.ALL_IN,
            amount=effective_stack,
            reasoning=f"Stack of {effective_stack}bb is too short to open normally — shove.",
        )
    
    size = PREFLOP_OPEN_SIZES.get(position, 2.5)
    if size is None:
        # BB shouldn't be calling this function; provide a safe default
        size = 2.5
    
    # Cap at effective stack
    size = min(size, effective_stack)
    
    return BetSizing(
        tier=BetTier.PREFLOP_OPEN,
        amount=round(size, 1),
        reasoning=f"Standard open from {position}: {size}bb.",
    )


def preflop_three_bet_sizing(
    open_size: float,
    hero_pos: str,
    villain_pos: str,
    effective_stack: float,
) -> BetSizing:
    """
    Return the recommended 3-bet sizing.
    
    In position = smaller (3x). Out of position = bigger (3.5x).
    If the result commits more than ~40% of the stack, just shove.
    """
    ip = is_in_position(hero_pos, villain_pos)
    multiplier = THREE_BET_MULTIPLIER_IP if ip else THREE_BET_MULTIPLIER_OOP
    size = round(open_size * multiplier, 1)
    
    position_note = "in position" if ip else "out of position"
    
    # If 3-bet is more than 40% of our stack, just shove
    if size > effective_stack * 0.40:
        return BetSizing(
            tier=BetTier.ALL_IN,
            amount=round(effective_stack, 1),
            reasoning=(
                f"3-bet of {size}bb commits too much of {effective_stack}bb stack "
                f"— shove instead."
            ),
        )
    
    # Cap at stack
    size = min(size, effective_stack)
    
    return BetSizing(
        tier=BetTier.THREE_BET,
        amount=round(size, 1),
        reasoning=(
            f"3-bet to {size}bb ({multiplier}x the {open_size}bb open, "
            f"{position_note})."
        ),
    )


def preflop_four_bet_sizing(
    three_bet_size: float,
    effective_stack: float,
) -> BetSizing:
    """
    Return the recommended 4-bet sizing.
    
    Standard 4-bet is ~2.5x the 3-bet. If SPR after the 4-bet would be
    too low, just shove — we're pot-committed anyway.
    """
    standard_size = round(three_bet_size * 2.5, 1)
    
    # If standard 4-bet commits >60% of stack, just shove
    if standard_size > effective_stack * 0.60:
        return BetSizing(
            tier=BetTier.ALL_IN,
            amount=round(effective_stack, 1),
            reasoning=(
                f"4-bet of {standard_size}bb commits >{60}% of stack "
                f"— shove for {effective_stack}bb."
            ),
        )
    
    size = min(standard_size, effective_stack)
    
    return BetSizing(
        tier=BetTier.PREFLOP_OPEN,  # Reusing tier; Phase 6 can add FOUR_BET tier
        amount=round(size, 1),
        reasoning=f"4-bet to {size}bb (2.5x the {three_bet_size}bb 3-bet).",
    )

# ============================================================
# Postflop sizing decision logic
# ============================================================

from poker_ai.engine.board import analyze_board, TextureType


def postflop_bet_sizing(
    equity: float,
    pot: float,
    stack: float,
    board: list,
) -> BetSizing:
    """
    Choose a bet tier and compute the BB amount for opening the betting postflop.
    
    Called when the advisor recommends BET (no prior bet to call).
    
    Args:
        equity: hero's win probability vs. villain's range (0-1)
        pot: current pot size in BB
        stack: hero's remaining stack in BB
        board: list of board card strings e.g. ['Kh', '7d', '2c']
    """
    # Stack-to-pot ratio — if very low, just shove
    spr = stack / pot if pot > 0 else 999
    if spr < 2.0:
        return BetSizing(
            tier=BetTier.ALL_IN,
            amount=round(stack, 1),
            reasoning=f"SPR {spr:.1f} — stack committed, shove for value.",
        )
    
    analysis = analyze_board(board)
    texture = analysis.texture
    
    # Special board overrides
    if texture == TextureType.MONOTONE:
        tier = BetTier.MEDIUM_BET
        extra = "Monotone board — polarized sizing."
    elif texture == TextureType.PAIRED:
        tier = BetTier.SMALL_BET
        extra = "Paired board — small sizing, narrow value range."
    
    # Strong equity (>75%): bet big regardless of texture
    elif equity > 0.75:
        tier = BetTier.LARGE_BET
        extra = f"Strong equity ({equity:.0%}) — large bet for maximum value."
    
    # Good equity (60-75%): texture drives size
    elif equity > 0.60:
        if texture == TextureType.WET:
            tier = BetTier.LARGE_BET
            extra = f"Good equity ({equity:.0%}) on wet board — large bet to deny draws."
        else:
            tier = BetTier.MEDIUM_BET
            extra = f"Good equity ({equity:.0%}) on dry board — medium value bet."
    
    # Marginal equity (45-60%): semi-bluff territory
    elif equity > 0.45:
        if texture == TextureType.WET:
            tier = BetTier.MEDIUM_BET
            extra = f"Marginal equity ({equity:.0%}) on wet board — semi-bluff bet."
        else:
            tier = BetTier.SMALL_BET
            extra = f"Marginal equity ({equity:.0%}) — small bet, thin value."
    
    # Low equity: shouldn't be betting, but size small if we do (bluff)
    else:
        tier = BetTier.SMALL_BET
        extra = f"Low equity ({equity:.0%}) — small bluff sizing."
    
    amount = size_postflop_bet(tier, pot)
    amount = min(amount, stack)  # Never bet more than stack
    
    return BetSizing(
        tier=tier,
        amount=round(amount, 1),
        reasoning=f"{extra} Bet {amount:.1f}bb into {pot:.1f}bb pot ({POSTFLOP_BET_FRACTIONS[tier]:.0%} pot).",
    )


def postflop_raise_sizing(
    equity: float,
    villain_bet: float,
    pot: float,
    stack: float,
    board: list,
) -> BetSizing:
    """
    Choose a raise tier and compute the BB amount when raising postflop.
    
    Called when the advisor recommends RAISE (there is a prior bet to raise over).
    
    Args:
        equity: hero's win probability vs. villain's range (0-1)
        villain_bet: the bet size hero is raising over (in BB)
        pot: current pot size in BB (including villain's bet)
        stack: hero's remaining stack in BB
        board: list of board card strings
    """
    # Stack-to-pot ratio: if shoving is basically correct, do it
    spr = stack / pot if pot > 0 else 999
    if spr < 1.5:
        return BetSizing(
            tier=BetTier.ALL_IN,
            amount=round(stack, 1),
            reasoning=f"SPR {spr:.1f} — raising to all-in for value.",
        )
    
    analysis = analyze_board(board)
    texture = analysis.texture
    
    # Choose raise tier
    if equity > 0.75:
        tier = BetTier.LARGE_RAISE
        extra = f"Strong equity ({equity:.0%}) — large raise to build pot."
    elif equity > 0.60 and texture == TextureType.WET:
        tier = BetTier.LARGE_RAISE
        extra = f"Good equity ({equity:.0%}) on wet board — large raise to deny draws."
    else:
        tier = BetTier.STANDARD_RAISE
        extra = f"Equity ({equity:.0%}) — standard raise for value."
    
    amount = size_postflop_raise(tier, villain_bet, stack)
    
    return BetSizing(
        tier=tier,
        amount=round(amount, 1),
        reasoning=f"{extra} Raise to {amount:.1f}bb.",
    )