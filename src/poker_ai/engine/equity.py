import random
from typing import List
from treys import Card, Deck, Evaluator as TreysEvaluator


class EquityCalculator:
    """
    Estimates win probability via Monte Carlo simulation.
    
    For Phase 2, we simulate vs. a random opponent hand. In Phase 3 we'll
    upgrade this to simulate vs. a realistic opponent *range*.
    """
    
    def __init__(self):
        self._evaluator = TreysEvaluator()
    
    def equity_vs_random(
        self,
        hole_cards: List[str],
        board: List[str],
        iterations: int = 2000,
    ) -> float:
        """
        Return our equity (0-1) vs. a single random opponent hand.
        
        `iterations` trades off accuracy vs. speed:
        - 1000  → ~±1.5% error, <100ms (good for UI responsiveness)
        - 2000  → ~±1.0% error, ~200ms (default)
        - 10000 → ~±0.5% error, ~1s (good for offline analysis)
        """
        hero = [Card.new(c) for c in hole_cards]
        board_cards = [Card.new(c) for c in board]
        known = set(hero + board_cards)
        
        wins = 0.0  # float so we can count ties as 0.5
        
        for _ in range(iterations):
            # Fresh deck minus known cards
            deck = Deck()
            deck.cards = [c for c in deck.cards if c not in known]
            random.shuffle(deck.cards)
            
            # Deal villain 2 random cards
            villain = [deck.cards.pop(), deck.cards.pop()]
            
            # Complete the board to 5 cards
            full_board = board_cards + [deck.cards.pop() for _ in range(5 - len(board_cards))]
            
            hero_rank = self._evaluator.evaluate(full_board, hero)
            villain_rank = self._evaluator.evaluate(full_board, villain)
            
            if hero_rank < villain_rank:       # lower = better in treys
                wins += 1
            elif hero_rank == villain_rank:
                wins += 0.5                     # split pot
        
        return wins / iterations