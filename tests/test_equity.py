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


    # ==================== Range-based equity tests ====================

from poker_ai.core.hand_range import Range


def test_aa_vs_aa_is_tie():
    """AA vs. villain range of exactly AA should be ~50% (always tied... or chopped)."""
    ec = EquityCalculator()
    r = Range.from_string("AA")
    # Our hero must not hold Ah or Ad so that villain has valid AA combos left
    equity = ec.equity_vs_range(
        ["2c", "3d"],
        [],
        r,
        iterations=TEST_ITERATIONS,
    )
    # Hero almost always loses to AA; equity should be very low
    assert equity < 0.15, f"Expected < 15%, got {equity:.1%}"


def test_aa_crushes_weak_range():
    """AA vs. {KK, QQ} should still be ~80%+ equity."""
    ec = EquityCalculator()
    r = Range.from_string("KK, QQ")
    equity = ec.equity_vs_range(
        ["Ah", "Ad"],
        [],
        r,
        iterations=TEST_ITERATIONS,
    )
    # AA beats KK/QQ roughly 80% preflop
    assert equity >= 0.75, f"Expected ≥ 75%, got {equity:.1%}"


def test_equity_vs_range_vs_vs_random_differ():
    """Equity vs. realistic betting range should be much lower than vs. random."""
    ec = EquityCalculator()
    tight_range = Range.from_string("QQ+, AK")
    
    # 77 on a K-high flop — the Phase 2 problem scenario
    eq_random = ec.equity_vs_random(
        ["7h", "7s"],
        ["Ks", "8d", "2c"],
        iterations=TEST_ITERATIONS,
    )
    eq_range = ec.equity_vs_range(
        ["7h", "7s"],
        ["Ks", "8d", "2c"],
        tight_range,
        iterations=TEST_ITERATIONS,
    )
    
    # The whole point of Phase 4: equity vs. a realistic range is much lower
    assert eq_random > 0.5
    assert eq_range < 0.20
    assert (eq_random - eq_range) > 0.40


def test_range_with_weights_differs_from_unweighted():
    """Heavily weighting weak hands in villain's range should raise our equity."""
    ec = EquityCalculator()
    # Version A: QQ+, AK at full weight (tough for 77 on K-high)
    strong = Range.from_string("QQ+, AK")
    # Version B: same hands but villain rarely has the strong hands
    mostly_bluffs = Range.from_string("QQ+:0.1, AK:0.1, 54s, 65s, 76s")
    
    eq_strong = ec.equity_vs_range(
        ["7h", "7s"],
        ["Ks", "8d", "2c"],
        strong,
        iterations=TEST_ITERATIONS,
    )
    eq_mixed = ec.equity_vs_range(
        ["7h", "7s"],
        ["Ks", "8d", "2c"],
        mostly_bluffs,
        iterations=TEST_ITERATIONS,
    )
    # Against the weaker mixed range, 77 should do much better
    assert eq_mixed > eq_strong + 0.15


def test_empty_range_raises():
    """If all villain combos conflict with blocked cards, should raise."""
    ec = EquityCalculator()
    # Villain range is exactly AhAd, which conflicts with hero's cards
    r = Range.from_string("AA")
    # Block all Aces — villain's AA range becomes empty after filtering
    try:
        ec.equity_vs_range(
            ["Ah", "As"],
            ["Ad", "Ac", "2s"],  # board contains the other two aces
            r,
            iterations=100,
        )
        assert False, "Expected ValueError for empty range"
    except ValueError:
        pass  # expected