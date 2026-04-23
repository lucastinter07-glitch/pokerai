from poker_ai.engine.equity import EquityCalculator


# Use higher iterations in tests for stability — we don't care about speed here
TEST_ITERATIONS = 5000


def test_pocket_aces_preflop_dominates():
    """Pocket aces vs random hand preflop should be ~85% equity."""
    ec = EquityCalculator()
    equity = ec.equity_vs_random(["Ah", "Ad"], [], iterations=TEST_ITERATIONS)
    assert 0.82 <= equity <= 0.88, f"Expected 82-88%, got {equity:.1%}"


def test_worst_hand_is_underdog_preflop():
    """7-2 offsuit preflop should be around 35% vs a random hand."""
    ec = EquityCalculator()
    equity = ec.equity_vs_random(["7h", "2c"], [], iterations=TEST_ITERATIONS)
    assert 0.30 <= equity <= 0.40, f"Expected 30-40%, got {equity:.1%}"


def test_made_flush_crushes_random():
    """Made flush on the flop should be ~95%+ vs random."""
    ec = EquityCalculator()
    equity = ec.equity_vs_random(
        ["Ah", "2h"],
        ["5h", "9h", "Kh"],
        iterations=TEST_ITERATIONS,
    )
    assert equity >= 0.92, f"Expected ≥92%, got {equity:.1%}"


def test_dead_hand_is_dead():
    """If villain can only chop, our equity should still be very high."""
    ec = EquityCalculator()
    # Royal flush on the board — every possible hand ties
    # (both players play the board's royal flush)
    equity = ec.equity_vs_random(
        ["2c", "3d"],
        ["Ah", "Kh", "Qh", "Jh", "Th"],
        iterations=1000,
    )
    # Pure tie → equity = 0.5
    assert 0.45 <= equity <= 0.55, f"Expected ~50% (chop), got {equity:.1%}"


def test_equity_returns_in_valid_range():
    """Equity must always be between 0 and 1."""
    ec = EquityCalculator()
    equity = ec.equity_vs_random(["Ah", "Ks"], [], iterations=500)
    assert 0.0 <= equity <= 1.0


def test_more_iterations_similar_result():
    """Equity with different iteration counts should converge to similar values."""
    ec = EquityCalculator()
    equity_low = ec.equity_vs_random(["Ah", "Ad"], [], iterations=1000)
    equity_high = ec.equity_vs_random(["Ah", "Ad"], [], iterations=5000)
    # Both should be in a reasonable range of true equity (~85%)
    assert abs(equity_low - equity_high) < 0.05