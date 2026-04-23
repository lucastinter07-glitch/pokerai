import random
from typing import List
from treys import Card, Deck, Evaluator as TreysEvaluator
from poker_ai.core.hand_range import Range


class EquityCalculator:
    """
    Estimates win probability via Monte Carlo simulation.
    
    Two modes:
    - equity_vs_random: vs. a uniformly-random opponent hand (Phase 2)
    - equity_vs_range:  vs. a weighted distribution of opponent hands (Phase 4)
    """
    
    def __init__(self):
        self._evaluator = TreysEvaluator()
    
    # ---------- Phase 2: vs. random hand ----------
    
    def equity_vs_random(
        self,
        hole_cards: List[str],
        board: List[str],
        iterations: int = 2000,
    ) -> float:
        """
        Return our equity (0-1) vs. a single random opponent hand.
        """
        hero = [Card.new(c) for c in hole_cards]
        board_cards = [Card.new(c) for c in board]
        known = set(hero + board_cards)
        
        wins = 0.0
        
        for _ in range(iterations):
            deck = Deck()
            deck.cards = [c for c in deck.cards if c not in known]
            random.shuffle(deck.cards)
            
            villain = [deck.cards.pop(), deck.cards.pop()]
            full_board = board_cards + [deck.cards.pop() for _ in range(5 - len(board_cards))]
            
            hero_rank = self._evaluator.evaluate(full_board, hero)
            villain_rank = self._evaluator.evaluate(full_board, villain)
            
            if hero_rank < villain_rank:
                wins += 1
            elif hero_rank == villain_rank:
                wins += 0.5
        
        return wins / iterations
    
    # ---------- Phase 4: vs. a range ----------
    
    def equity_vs_range(
        self,
        hole_cards: List[str],
        board: List[str],
        villain_range: Range,
        iterations: int = 2000,
    ) -> float:
        """
        Return our equity (0-1) vs. a weighted distribution of villain hands.
        
        Villain's range is filtered to remove combos that conflict with
        hero's cards and the board. Each iteration samples one combo from
        the filtered range (weighted by combo weights) and runs a showdown.
        
        Raises ValueError if the filtered range is empty (no valid combos).
        """
        # Remove any combos that share a card with hero or the board
        blocked_cards = list(hole_cards) + list(board)
        filtered = villain_range.remove_blocked(blocked_cards)
        
        if filtered.is_empty():
            raise ValueError(
                "Villain's range has no valid combos after removing blocked cards."
            )
        
        # Pre-build weighted sampling pool from the filtered range
        combos = list(filtered.combos.keys())
        weights = list(filtered.combos.values())
        
        # Convert hero + board to treys ints (once, outside the loop)
        hero_treys = [Card.new(c) for c in hole_cards]
        board_treys = [Card.new(c) for c in board]
        known_ints = set(hero_treys + board_treys)
        
        wins = 0.0
        
        for _ in range(iterations):
            # Sample a villain combo weighted by range weights
            villain_combo = random.choices(combos, weights=weights, k=1)[0]
            villain_treys = [Card.new(villain_combo[0]), Card.new(villain_combo[1])]
            
            # Remaining deck minus known + villain's cards
            all_blocked = known_ints | set(villain_treys)
            deck = Deck()
            deck.cards = [c for c in deck.cards if c not in all_blocked]
            random.shuffle(deck.cards)
            
            full_board = board_treys + [deck.cards.pop() for _ in range(5 - len(board_treys))]
            
            hero_rank = self._evaluator.evaluate(full_board, hero_treys)
            villain_rank = self._evaluator.evaluate(full_board, villain_treys)
            
            if hero_rank < villain_rank:
                wins += 1
            elif hero_rank == villain_rank:
                wins += 0.5
        
        return wins / iterations