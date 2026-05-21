"""Tests for bet sizing logic (sizing.py and board.py)."""

import pytest
from poker_ai.advisor.sizing import (
    BetTier,
    BetSizing,
    size_postflop_bet,
    size_postflop_raise,
    preflop_open_sizing,
    preflop_three_bet_sizing,
    preflop_four_bet_sizing,
    postflop_bet_sizing,
    postflop_raise_sizing,
    is_in_position,
)
from poker_ai.engine.board import analyze_board, TextureType


# ==================== Board texture tests ====================

def test_dry_board_classified_correctly():
    analysis = analyze_board(["Ks", "7d", "2c"])
    assert analysis.texture == TextureType.DRY
    assert not analysis.flush_draw
    assert not analysis.straight_draw


def test_wet_board_flush_and_straight():
    analysis = analyze_board(["Jh", "Th", "9c"])
    assert analysis.texture == TextureType.WET
    assert analysis.flush_draw
    assert analysis.straight_draw


def test_monotone_board():
    analysis = analyze_board(["Ah", "8h", "3h"])
    assert analysis.texture == TextureType.MONOTONE
    assert analysis.is_monotone


def test_paired_board():
    analysis = analyze_board(["Kh", "Kd", "7c"])
    assert analysis.texture == TextureType.PAIRED
    assert analysis.is_paired


def test_connected_rainbow_is_wet():
    """876 rainbow should be WET due to high connectedness."""
    analysis = analyze_board(["8h", "7c", "6d"])
    assert analysis.texture == TextureType.WET
    assert analysis.connectedness_score >= 8


def test_board_requires_flop():
    with pytest.raises(ValueError):
        analyze_board(["Ah", "Kd"])


def test_ace_high_detected():
    analysis = analyze_board(["Ah", "7d", "2c"])
    assert analysis.has_ace


def test_king_high_detected():
    analysis = analyze_board(["Kh", "7d", "2c"])
    assert analysis.has_king
    assert not analysis.has_ace


# ==================== Position tests ====================

def test_btn_is_ip_vs_utg():
    assert is_in_position("BTN", "UTG") is True


def test_bb_is_oop_vs_utg():
    assert is_in_position("BB", "UTG") is False


def test_sb_is_oop_vs_btn():
    assert is_in_position("SB", "BTN") is False


def test_co_is_ip_vs_utg():
    assert is_in_position("CO", "UTG") is True


# ==================== Sizing math tests ====================

def test_postflop_bet_math():
    """50% pot bet into 10bb = 5bb."""
    assert size_postflop_bet(BetTier.MEDIUM_BET, 10) == 5.0


def test_postflop_raise_math():
    """Standard raise (2.5x) vs 5bb = 12.5bb."""
    assert size_postflop_raise(BetTier.STANDARD_RAISE, 5, 100) == 12.5


def test_all_in_capped_by_stack():
    """All-in raise is capped at stack, not bet * multiplier."""
    assert size_postflop_raise(BetTier.ALL_IN, 5, 30) == 30


def test_raise_capped_at_stack():
    """Raise amount should never exceed stack."""
    result = size_postflop_raise(BetTier.LARGE_RAISE, 50, 40)
    assert result <= 40


# ==================== Preflop sizing tests ====================

def test_btn_opens_smaller_than_utg():
    btn = preflop_open_sizing("BTN", 100).amount
    utg = preflop_open_sizing("UTG", 100).amount
    assert btn <= utg


def test_short_stack_open_is_shove():
    result = preflop_open_sizing("BTN", 12)
    assert result.tier == BetTier.ALL_IN
    assert result.amount == 12


def test_ip_three_bet_smaller_than_oop():
    ip = preflop_three_bet_sizing(2.5, "BTN", "UTG", 100).amount
    oop = preflop_three_bet_sizing(2.5, "BB", "UTG", 100).amount
    assert ip < oop


def test_three_bet_short_stack_is_shove():
    result = preflop_three_bet_sizing(2.5, "BB", "BTN", 20)
    assert result.tier == BetTier.ALL_IN


def test_four_bet_standard_depth():
    result = preflop_four_bet_sizing(8, 100)
    assert result.amount == 20.0


def test_four_bet_shallow_stack_is_shove():
    result = preflop_four_bet_sizing(8, 30)
    assert result.tier == BetTier.ALL_IN


# ==================== Postflop sizing integration tests ====================

def test_strong_equity_gets_large_bet():
    """High equity on any board should produce a large bet."""
    result = postflop_bet_sizing(0.85, 10, 90, ["Ks", "7d", "2c"])
    assert result.tier == BetTier.LARGE_BET


def test_good_equity_wet_board_gets_large_bet():
    """Good equity on wet board should also be large."""
    result = postflop_bet_sizing(0.65, 10, 90, ["Jh", "Th", "9c"])
    assert result.tier == BetTier.LARGE_BET


def test_good_equity_dry_board_gets_medium_bet():
    """Good equity on dry board should be medium."""
    result = postflop_bet_sizing(0.65, 10, 90, ["Ks", "7d", "2c"])
    assert result.tier == BetTier.MEDIUM_BET


def test_marginal_equity_dry_gets_small_bet():
    """Marginal equity on dry board — small bet."""
    result = postflop_bet_sizing(0.50, 10, 90, ["Ks", "7d", "2c"])
    assert result.tier == BetTier.SMALL_BET


def test_monotone_override_is_medium():
    """Monotone board always gets medium sizing regardless of equity."""
    result = postflop_bet_sizing(0.90, 10, 90, ["Ah", "8h", "3h"])
    assert result.tier == BetTier.MEDIUM_BET


def test_paired_override_is_small():
    """Paired board always gets small sizing."""
    result = postflop_bet_sizing(0.80, 10, 90, ["Kh", "Kd", "7c"])
    assert result.tier == BetTier.SMALL_BET


def test_low_spr_bets_all_in():
    """Stack < 2x pot triggers all-in bet."""
    result = postflop_bet_sizing(0.80, 10, 8, ["Ks", "7d", "2c"])
    assert result.tier == BetTier.ALL_IN


def test_bet_never_exceeds_stack():
    """Bet amount is always capped at remaining stack."""
    result = postflop_bet_sizing(0.80, 100, 20, ["Ks", "7d", "2c"])
    assert result.amount <= 20


def test_strong_equity_raise_is_large():
    """High equity raise should be large."""
    result = postflop_raise_sizing(0.85, 5, 15, 90, ["Ks", "7d", "2c"])
    assert result.tier == BetTier.LARGE_RAISE


def test_standard_equity_raise_is_standard():
    """Moderate equity raise should be standard."""
    result = postflop_raise_sizing(0.55, 5, 15, 90, ["Ks", "7d", "2c"])
    assert result.tier == BetTier.STANDARD_RAISE


def test_raise_never_exceeds_stack():
    """Raise amount is always capped at stack."""
    result = postflop_raise_sizing(0.85, 5, 15, 20, ["Ks", "7d", "2c"])
    assert result.amount <= 20


def test_low_spr_raise_is_all_in():
    """Low SPR triggers all-in raise."""
    result = postflop_raise_sizing(0.85, 5, 15, 12, ["Ks", "7d", "2c"])
    assert result.tier == BetTier.ALL_IN