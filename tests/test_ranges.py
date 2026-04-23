"""Tests for opponent range construction (ranges.py)."""

import pytest
from poker_ai.advisor.ranges import (
    opening_range,
    three_bet_range,
    calling_range,
    OPEN_RAISE_RANGES,
)


# ---------- Opening ranges ----------

def test_all_positions_have_opening_range():
    """Every position key should have a parseable range."""
    for pos in ["UTG", "MP", "CO", "BTN", "SB", "BB"]:
        r = opening_range(pos)
        assert r.num_combos() > 0


def test_utg_is_tighter_than_btn():
    """UTG opens fewer hands than BTN — basic poker truth."""
    utg = opening_range("UTG")
    btn = opening_range("BTN")
    assert utg.num_combos() < btn.num_combos()


def test_ranges_widen_monotonically():
    """Ranges should get wider as position improves (UTG < MP < CO < BTN)."""
    utg = opening_range("UTG").num_combos()
    mp = opening_range("MP").num_combos()
    co = opening_range("CO").num_combos()
    btn = opening_range("BTN").num_combos()
    assert utg < mp < co < btn


def test_premium_hands_in_every_opening_range():
    """AA, KK, and AKs should be in every opening range — no one folds them."""
    for pos in ["UTG", "MP", "CO", "BTN", "SB"]:
        r = opening_range(pos)
        # AA is 6 combos; check at least one is present
        aa_combos = [c for c in r.combos if c[0][0] == "A" and c[1][0] == "A"]
        assert len(aa_combos) == 6, f"AA missing from {pos} range"


def test_junk_not_in_utg_range():
    """72o should never be in a UTG opening range."""
    utg = opening_range("UTG")
    junk = [c for c in utg.combos if {c[0][0], c[1][0]} == {"7", "2"}]
    assert len(junk) == 0


def test_unknown_position_raises():
    with pytest.raises(ValueError):
        opening_range("XYZ")


# ---------- 3-bet ranges ----------

def test_3bet_vs_utg_is_tight():
    """3-betting over UTG should be rare — very few hands."""
    r = three_bet_range("UTG")
    assert r.num_combos() < 50  # Should be tight: QQ+, AK only


def test_3bet_widens_vs_later_position():
    """3-bet ranges should widen against looser openers."""
    vs_utg = three_bet_range("UTG").num_combos()
    vs_btn = three_bet_range("BTN").num_combos()
    assert vs_utg < vs_btn


def test_3bet_always_includes_aa_and_kk():
    """AA and KK should always be in any 3-bet range."""
    for pos in ["UTG", "MP", "CO", "BTN", "SB"]:
        r = three_bet_range(pos)
        aa = [c for c in r.combos if c[0][0] == "A" and c[1][0] == "A"]
        kk = [c for c in r.combos if c[0][0] == "K" and c[1][0] == "K"]
        assert len(aa) == 6
        assert len(kk) == 6


# ---------- Calling ranges ----------

def test_calling_range_excludes_premium():
    """Calling ranges should NOT include AA — those get 3-bet."""
    r = calling_range("UTG")
    aa = [c for c in r.combos if c[0][0] == "A" and c[1][0] == "A"]
    assert len(aa) == 0, "AA should be 3-bet, not flat-called"


def test_calling_range_widens_vs_later_position():
    """Flat-call ranges should widen against wider openers."""
    vs_utg = calling_range("UTG").num_combos()
    vs_btn = calling_range("BTN").num_combos()
    assert vs_utg < vs_btn