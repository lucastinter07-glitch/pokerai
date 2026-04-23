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
    hole_cards: List[str]
    position: Position
    stack: float
    
    # Table state
    board: List[str] = field(default_factory=list)
    pot: float = 1.5
    to_call: float = 0.0
    
    # Context
    num_players: int = 6
    effective_stack: float = 100.0
    
    # Villain modeling (Phase 4)
    villain_position: Optional[Position] = None
    """Which position the active betting opponent is in. If None, we use a default."""
    
    @property
    def street(self) -> Street:
        n = len(self.board)
        if n == 0: return Street.PREFLOP
        if n == 3: return Street.FLOP
        if n == 4: return Street.TURN
        if n == 5: return Street.RIVER
        raise ValueError(f"Invalid board length: {n}")
    
    @property
    def pot_odds(self) -> float:
        if self.to_call == 0:
            return 0.0
        return self.to_call / (self.pot + self.to_call)