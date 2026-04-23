from treys import Card, Evaluator as TreysEvaluator
from typing import List

class HandEvaluator:
    """
    Evaluates made hand strength on a given board.
    Wraps the `treys` library so the rest of our code never imports it directly.
    """
    
    def __init__(self):
        self._evaluator = TreysEvaluator()
    
    def _to_treys(self, cards: List[str]) -> List[int]:
        """Convert our string format ('Ah') to treys' internal int format."""
        return [Card.new(c) for c in cards]
    
    def rank(self, hole_cards: List[str], board: List[str]) -> int:
        """
        Return the treys rank (1 = best, 7462 = worst).
        Requires at least a flop (3 board cards).
        """
        if len(board) < 3:
            raise ValueError("Hand evaluation requires at least a flop.")
        return self._evaluator.evaluate(
            self._to_treys(board),
            self._to_treys(hole_cards)
        )
    
    def hand_class(self, hole_cards: List[str], board: List[str]) -> str:
        """Return a human-readable hand class: 'Flush', 'Two Pair', etc."""
        rank = self.rank(hole_cards, board)
        class_int = self._evaluator.get_rank_class(rank)
        return self._evaluator.class_to_string(class_int)
    
    def strength_percentile(self, hole_cards: List[str], board: List[str]) -> float:
        """
        Return hand strength as a 0-1 percentile (1.0 = best possible hand).
        Useful for comparing hands intuitively.
        """
        rank = self.rank(hole_cards, board)
        return 1.0 - (rank - 1) / 7461  # treys: 1 is best, 7462 is worst