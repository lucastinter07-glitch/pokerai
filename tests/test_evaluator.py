from poker_ai.engine.evaluator import HandEvaluator


def test_royal_flush_is_best_possible_hand():
    """Royal flush should have rank 1 (best in treys)."""
    ev = HandEvaluator()
    rank = ev.rank(["Ah", "Kh"], ["Qh", "Jh", "Th"])
    assert rank == 1


def test_pair_beats_high_card():
    """Lower treys rank = stronger hand. Pocket aces should beat AK high."""
    ev = HandEvaluator()
    pair_of_aces = ev.rank(["Ah", "Ad"], ["Kc", "7h", "2s"])
    ace_high = ev.rank(["Ah", "Kd"], ["Qc", "7h", "2s"])
    assert pair_of_aces < ace_high


def test_hand_class_readable():
    """The hand_class method should return a human-readable string."""
    ev = HandEvaluator()
    trips = ev.hand_class(["Ah", "Ad"], ["As", "7h", "2s"])
    assert trips == "Three of a Kind"


def test_flush_beats_straight():
    """Basic hand ranking: flush > straight."""
    ev = HandEvaluator()
    flush = ev.rank(["Ah", "2h"], ["5h", "9h", "Kh"])
    straight = ev.rank(["9s", "8d"], ["7h", "6c", "5s"])
    assert flush < straight


def test_strength_percentile_in_valid_range():
    """Percentile should always be between 0 and 1, and rank stronger hands higher."""
    ev = HandEvaluator()
    
    trips = ev.strength_percentile(["Ah", "Ad"], ["As", "7h", "2s"])
    pair = ev.strength_percentile(["Ah", "Kd"], ["Ac", "7h", "2s"])
    high_card = ev.strength_percentile(["Ah", "Kd"], ["Qc", "7h", "2s"])
    
    # All must be valid percentiles
    for p in (trips, pair, high_card):
        assert 0.0 <= p <= 1.0
    
    # Ordering must be correct: trips > pair > high card
    assert trips > pair > high_card


def test_royal_flush_is_perfect_percentile():
    """Royal flush (rank 1) should be exactly 1.0 percentile."""
    ev = HandEvaluator()
    percentile = ev.strength_percentile(["Ah", "Kh"], ["Qh", "Jh", "Th"])
    assert percentile == 1.0


def test_raises_error_without_flop():
    """Evaluator should refuse to evaluate preflop (no board)."""
    ev = HandEvaluator()
    try:
        ev.rank(["Ah", "Kh"], [])
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # expected