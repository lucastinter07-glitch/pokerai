from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class Street(Enum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"


class Position(Enum):
    UTG = "UTG"
    MP = "MP"
    CO = "CO"
    BTN = "BTN"
    SB = "SB"
    BB = "BB"


@dataclass
class GameState:
    """Complete state of a poker decision point in a cash game."""
    
    # Player's situation
    hole_cards: List[str]              # e.g., ["Ah", "Ks"]
    position: Position
    stack: float                       # Player's remaining stack in BB (big blinds)
    
    # Table state
    board: List[str] = field(default_factory=list)  # e.g., ["Qh", "7d", "2c"]
    pot: float = 1.5                   # Default: SB + BB = 1.5bb preflop
    to_call: float = 0.0               # Amount player must call to stay in
    
    # Context
    num_players: int = 6               # 6-max default for cash games
    effective_stack: float = 100.0     # Smallest stack in the hand, in BB
    
    @property
    def street(self) -> Street:
        """Derive current street from board length."""
        n = len(self.board)
        if n == 0: return Street.PREFLOP
        if n == 3: return Street.FLOP
        if n == 4: return Street.TURN
        if n == 5: return Street.RIVER
        raise ValueError(f"Invalid board length: {n}")
    
    @property
    def pot_odds(self) -> float:
        """
        Return pot odds as a ratio (0-1): the equity you need to profitably call.
        Example: pot=10, to_call=5 → need 5/(10+5) = 33.3% equity.
        """
        if self.to_call == 0:
            return 0.0
        return self.to_call / (self.pot + self.to_call)