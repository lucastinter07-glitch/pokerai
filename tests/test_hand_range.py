"""Tests for the Range class and notation parsing."""

import pytest
from poker_ai.core.hand_range import (
    Range,
    expand_notation,
    _expand_plus_notation,
    _canonical_combo,
    parse_range_string,
)


# ---------- Canonical combo ordering ----------

def test_canonical_combo_orders_higher_rank_first():
    """Higher-ranked card should come first regardless of input order."""
    assert _canonical_combo("Ks", "As") == ("As", "Ks")
    assert _canonical_combo("As", "Ks") == ("As", "Ks")
    assert _canonical_combo("2c", "Th") == ("Th", "2c")


def test_canonical_combo_pair_stable():
    """Same pair given in different orders should produce identical combos."""
    a = _canonical_combo("Ah", "Ad")
    b = _canonical_combo("Ad", "Ah")
    assert a == b


# ---------- expand_notation ----------

def test_expand_pair_gives_6_combos():
    """Any pair expands to exactly 6 combos."""
    assert len(expand_notation("AA")) == 6
    assert len(expand_notation("77")) == 6
    assert len(expand_notation("22")) == 6


def test_expand_suited_gives_4_combos():
    """Suited non-pair expands to exactly 4 combos."""
    assert len(expand_notation("AKs")) == 4
    assert len(expand_notation("72s")) == 4


def test_expand_offsuit_gives_12_combos():
    """Offsuit non-pair expands to exactly 12 combos."""
    assert len(expand_notation("AKo")) == 12
    assert len(expand_notation("QJo")) == 12


def test_expand_unspecified_gives_16_combos():
    """'AK' (unspecified suitedness) = 16 combos (4 suited + 12 offsuit)."""
    assert len(expand_notation("AK")) == 16


def test_expand_suited_combos_share_suit():
    """Every AKs combo has matching suits."""
    for c1, c2 in expand_notation("AKs"):
        assert c1[1] == c2[1]  # same suit


def test_expand_offsuit_combos_differ_in_suit():
    """Every AKo combo has different suits."""
    for c1, c2 in expand_notation("AKo"):
        assert c1[1] != c2[1]  # different suits


def test_expand_bad_code_raises():
    """Garbage input should raise ValueError."""
    with pytest.raises(ValueError):
        expand_notation("XYZ")
    with pytest.raises(ValueError):
        expand_notation("AAs")  # pairs can't be suited
    with pytest.raises(ValueError):
        expand_notation("AKx")  # invalid kind


# ---------- _expand_plus_notation ----------

def test_plus_pair_expands_correctly():
    """'JJ+' means JJ, QQ, KK, AA."""
    result = _expand_plus_notation("JJ+")
    assert result == ["JJ", "QQ", "KK", "AA"]


def test_plus_pair_aa_only_itself():
    """'AA+' means just AA (no higher pair exists)."""
    result = _expand_plus_notation("AA+")
    assert result == ["AA"]


def test_plus_suited_expands_correctly():
    """'ATs+' means ATs, AJs, AQs, AKs."""
    result = _expand_plus_notation("ATs+")
    assert result == ["ATs", "AJs", "AQs", "AKs"]


def test_plus_offsuit_expands_correctly():
    """'AJo+' means AJo, AQo, AKo."""
    result = _expand_plus_notation("AJo+")
    assert result == ["AJo", "AQo", "AKo"]


def test_plus_unspecified_expands_correctly():
    """'AT+' means AT, AJ, AQ, AK (each unspecified suitedness)."""
    result = _expand_plus_notation("AT+")
    assert result == ["AT", "AJ", "AQ", "AK"]


def test_no_plus_returns_token_unchanged():
    """Tokens without '+' should pass through."""
    assert _expand_plus_notation("AKs") == ["AKs"]
    assert _expand_plus_notation("77") == ["77"]


# ---------- parse_range_string ----------

def test_parse_simple_range():
    """Parse a single hand."""
    result = parse_range_string("AA")
    assert len(result) == 6  # 6 combos of AA
    for weight in result.values():
        assert weight == 1.0


def test_parse_multiple_hands():
    """Parse a comma-separated list."""
    result = parse_range_string("AA, KK, AKs")
    # 6 + 6 + 4 = 16 combos
    assert len(result) == 16


def test_parse_weighted_hand():
    """Parse a hand with explicit weight."""
    result = parse_range_string("AKs:0.5")
    assert len(result) == 4
    for weight in result.values():
        assert weight == 0.5


def test_parse_mixed_weights():
    """Parse hands with mixed weights."""
    result = parse_range_string("AA, KK:0.5")
    # AA combos should weight 1.0; KK combos should weight 0.5
    for combo, weight in result.items():
        if combo[0][0] == "A":  # ace pair
            assert weight == 1.0
        else:  # king pair
            assert weight == 0.5


def test_parse_with_plus_notation():
    """Plus notation should work inside range strings."""
    result = parse_range_string("TT+")
    # TT, JJ, QQ, KK, AA = 5 pairs × 6 combos = 30
    assert len(result) == 30


# ---------- Range class ----------

def test_range_from_string():
    """Range can be built from a string."""
    r = Range.from_string("JJ+, AK")
    # JJ+ = 4 pairs × 6 = 24 combos
    # AK = 16 combos
    # Total = 40
    assert r.num_combos() == 40
    assert r.total_combos() == 40.0


def test_range_is_empty():
    """Empty range behaves correctly."""
    r = Range()
    assert r.is_empty()
    assert r.num_combos() == 0


def test_range_remove_blocked_cards():
    """Blocking a card removes all combos containing it."""
    r = Range.from_string("AA")
    # Block Ah — should remove 3 AA combos (Ah with each other Ace)
    r2 = r.remove_blocked(["Ah"])
    assert r2.num_combos() == 3


def test_range_remove_multiple_blocked_cards():
    """Blocking multiple cards removes all combos containing any of them."""
    r = Range.from_string("AKs")  # 4 suited combos
    # Block Ah and Ks — removes AhKh (Ah) and AsKs (Ks) and any other Ks/Ah combo
    r2 = r.remove_blocked(["Ah", "Ks"])
    # Remaining: AdKd, AcKc (2 combos)
    assert r2.num_combos() == 2


def test_range_remove_blocked_does_not_mutate_original():
    """remove_blocked should return a new Range without modifying the original."""
    r = Range.from_string("AA")
    r2 = r.remove_blocked(["Ah"])
    assert r.num_combos() == 6  # original unchanged
    assert r2.num_combos() == 3  # new range smaller


def test_weighted_range_total_combos():
    """total_combos reflects weighted sum, num_combos reflects raw count."""
    r = Range.from_string("AA, KK:0.5")
    assert r.num_combos() == 12  # 6 AA + 6 KK
    assert r.total_combos() == 9.0  # 6 * 1.0 + 6 * 0.5


    # ==================== Dash notation tests ====================

from poker_ai.core.hand_range import _expand_dash_notation


def test_dash_pair_range():
    """'22-55' should expand to [22, 33, 44, 55]."""
    result = _expand_dash_notation("22-55")
    assert result == ["22", "33", "44", "55"]


def test_dash_pair_range_reverse_order():
    """'55-22' should also work — order doesn't matter."""
    result = _expand_dash_notation("55-22")
    assert result == ["22", "33", "44", "55"]


def test_dash_suited_range():
    """'AJs-A9s' should expand to [A9s, ATs, AJs]."""
    result = _expand_dash_notation("AJs-A9s")
    assert set(result) == {"A9s", "ATs", "AJs"}


def test_dash_offsuit_range():
    """'KQo-KTo' should expand to [KTo, KJo, KQo]."""
    result = _expand_dash_notation("KQo-KTo")
    assert set(result) == {"KTo", "KJo", "KQo"}


def test_no_dash_passes_through():
    """Tokens without '-' should pass through unchanged."""
    assert _expand_dash_notation("AA") == ["AA"]
    assert _expand_dash_notation("JJ+") == ["JJ+"]


def test_dash_mismatched_high_rank_raises():
    """'AJs-KTs' (different high ranks) should be rejected."""
    with pytest.raises(ValueError):
        _expand_dash_notation("AJs-KTs")


def test_dash_mismatched_suitedness_raises():
    """'AJs-ATo' (mixed suited/offsuit) should be rejected."""
    with pytest.raises(ValueError):
        _expand_dash_notation("AJs-ATo")


def test_parse_range_with_dash():
    """Full range parser should handle dash notation."""
    r = Range.from_string("22-TT")
    # 22, 33, 44, 55, 66, 77, 88, 99, TT = 9 pairs × 6 combos = 54
    assert r.num_combos() == 54


def test_parse_range_with_combined_notation():
    """Dash + plus notation should combine cleanly."""
    # '22-TT, JJ+, AK' should give: 9 pairs (54 combos) + 4 pairs (24 combos) + AK (16) = 94
    r = Range.from_string("22-TT, JJ+, AK")
    assert r.num_combos() == 94