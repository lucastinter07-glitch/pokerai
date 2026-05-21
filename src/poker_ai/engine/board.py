"""
Board texture analysis for postflop bet sizing.

Classifies the flop/turn/river as dry, wet, or dynamic based on
suitedness, connectedness, high card presence, and pairedness.
These classifications drive postflop bet sizing decisions.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List

# Rank values for connectedness calculations
RANK_VALUES = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
    "9": 9, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14
}


class TextureType(Enum):
    """
    Board texture classification.
    
    DRY:       Few draws, static — small bets work well
    NEUTRAL:   Some draws, moderate — medium bets
    WET:       Many draws, dynamic — large bets to deny equity
    MONOTONE:  Three of one suit — polarized; variable sizing
    PAIRED:    Board has a pair — narrow betting range
    """
    DRY = "dry"
    NEUTRAL = "neutral"
    WET = "wet"
    MONOTONE = "monotone"
    PAIRED = "paired"


@dataclass
class BoardAnalysis:
    """
    Complete analysis of a board's texture.
    
    - texture: the overall classification
    - flush_draw: True if two or more cards share a suit
    - straight_draw: True if cards are connected (gap <= 2)
    - has_ace: True if board contains an Ace
    - has_king: True if board contains a King
    - is_paired: True if any rank appears twice
    - is_monotone: True if all three flop cards share a suit
    - connectedness_score: 0-10 (10 = maximally connected J-T-9)
    - reasoning: human-readable description
    """
    texture: TextureType
    flush_draw: bool
    straight_draw: bool
    has_ace: bool
    has_king: bool
    is_paired: bool
    is_monotone: bool
    connectedness_score: int
    reasoning: str


def _ranks(board: List[str]) -> List[int]:
    """Extract rank values from board cards."""
    return sorted([RANK_VALUES[c[0]] for c in board], reverse=True)


def _suits(board: List[str]) -> List[str]:
    """Extract suits from board cards."""
    return [c[1] for c in board]


def _has_flush_draw(board: List[str]) -> bool:
    """True if two or more board cards share a suit."""
    suits = _suits(board)
    return any(suits.count(s) >= 2 for s in set(suits))


def _is_monotone(board: List[str]) -> bool:
    """True if all cards (on the flop) share the same suit."""
    if len(board) < 3:
        return False
    flop_suits = [board[i][1] for i in range(3)]
    return len(set(flop_suits)) == 1


def _is_paired(board: List[str]) -> bool:
    """True if any rank appears more than once on the board."""
    ranks = [c[0] for c in board]
    return len(ranks) != len(set(ranks))


def _connectedness_score(board: List[str]) -> int:
    """
    Score 0-10 for how connected the board is.
    
    Uses the three flop cards (ignoring turn/river for base texture).
    Lower gaps between ranks = higher score = more straight draws possible.
    
    Score 10: J-T-9 (maximally connected, 8 straight draws)
    Score 0:  A-7-2 (no meaningful connections)
    """
    if len(board) < 3:
        return 0
    
    flop_ranks = sorted([RANK_VALUES[board[i][0]] for i in range(3)], reverse=True)
    
    # Gap between highest and middle, and middle and lowest
    gap_1 = flop_ranks[0] - flop_ranks[1]
    gap_2 = flop_ranks[1] - flop_ranks[2]
    
    # Score based on gaps — smaller gaps = more connected
    total_gap = gap_1 + gap_2
    
    if total_gap <= 2:   return 10  # J-T-9, T-9-8 etc.
    if total_gap <= 3:   return 8   # J-T-8, Q-T-9 etc.
    if total_gap <= 4:   return 6   # J-T-7, Q-J-8 etc.
    if total_gap <= 5:   return 4   # J-9-7, Q-J-7 etc.
    if total_gap <= 7:   return 2   # K-9-7, A-9-7 etc.
    return 0                        # A-7-2, K-8-2 etc.


def _has_ace(board: List[str]) -> bool:
    return any(c[0] == "A" for c in board)


def _has_king(board: List[str]) -> bool:
    return any(c[0] == "K" for c in board)


def analyze_board(board: List[str]) -> BoardAnalysis:
    """
    Analyze a board and return its texture classification.
    
    Works on flop (3 cards), turn (4 cards), or river (5 cards).
    Uses the first 3 cards (flop) as the primary texture reference.
    """
    if len(board) < 3:
        raise ValueError("Board analysis requires at least a flop (3 cards).")
    
    flush_draw = _has_flush_draw(board)
    monotone = _is_monotone(board)
    paired = _is_paired(board)
    straight_draw = False
    conn_score = _connectedness_score(board)
    ace = _has_ace(board)
    king = _has_king(board)
    
    # Connectedness score >= 6 means meaningful straight draws present
    if conn_score >= 6:
        straight_draw = True
    
    # ---- Classify texture ----
    
    # Monotone overrides other classifications (most important structural fact)
    if monotone:
        texture = TextureType.MONOTONE
        reasoning = "Monotone flop — all three cards same suit. Polarized sizing."
    
    # Paired board
    elif paired:
        texture = TextureType.PAIRED
        reasoning = "Paired board — trips heavily discounted. Narrow value range."
    
    # Both flush AND straight draws = maximally wet
    elif flush_draw and straight_draw:
        texture = TextureType.WET
        reasoning = (
            f"Wet board — flush draw + straight draw (connectedness {conn_score}/10). "
            "Large sizing to deny equity."
        )
    
    # Flush draw only = semi-wet
    elif flush_draw and not straight_draw:
        texture = TextureType.NEUTRAL
        reasoning = (
            "Neutral board — flush draw present, limited straight draws. "
            "Medium sizing."
        )
    
    # Straight draw only — highly connected = wet, moderately connected = neutral
    elif straight_draw and not flush_draw:
        if conn_score >= 8:
            texture = TextureType.WET
            reasoning = (
                f"Wet board — highly connected (connectedness {conn_score}/10), "
                "many straight draws. Large sizing to deny equity."
            )
        else:
            texture = TextureType.NEUTRAL
            reasoning = (
                f"Neutral board — straight draw present (connectedness {conn_score}/10), "
                "no flush draw. Medium sizing."
            )
    
    # No draws at all = dry
    else:
        texture = TextureType.DRY
        reasoning = (
            "Dry board — rainbow, disconnected. "
            "Small sizing; villain's range doesn't change much."
        )
    
    return BoardAnalysis(
        texture=texture,
        flush_draw=flush_draw,
        straight_draw=straight_draw,
        has_ace=ace,
        has_king=king,
        is_paired=paired,
        is_monotone=monotone,
        connectedness_score=conn_score,
        reasoning=reasoning,
    )