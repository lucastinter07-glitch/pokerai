from abc import ABC, abstractmethod
from poker_ai.core.game_state import GameState


class Advisor(ABC):
    """
    Abstract base class for all decision-making strategies.
    
    Every advisor must implement `recommend()` and return a dict with:
      - action:    str  — 'fold', 'check', 'call', 'bet', or 'raise'
      - reasoning: str  — human-readable explanation of the decision
      - equity:    float | None — win probability (0-1), or None if not computed
      - pot_odds:  float — required equity to call (0-1)
    """
    
    @abstractmethod
    def recommend(self, state: GameState) -> dict:
        pass