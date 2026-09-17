import random

import pytest
from simon.memory_session import MAX_PAIR_COUNT, MemoryGameSession


def test_grid_has_two_of_each_symbol():
    session = MemoryGameSession(pair_count=4, rng=random.Random(0))
    assert len(session.cards) == 8
    for symbol in set(session.cards):
        assert session.cards.count(symbol) == 2


def test_pair_count_reflects_grid_size():
    session = MemoryGameSession(pair_count=5, rng=random.Random(0))
    assert session.pair_count == 5


def test_pair_count_clamped_to_valid_range():
    assert MemoryGameSession(pair_count=0, rng=random.Random(0)).pair_count == 1
    assert MemoryGameSession(pair_count=999, rng=random.Random(0)).pair_count == MAX_PAIR_COUNT


def test_not_complete_at_start():
    session = MemoryGameSession(pair_count=3, rng=random.Random(0))
    assert not session.is_complete


def test_reveal_second_card_signals_ready_to_resolve():
    session = MemoryGameSession(pair_count=3, rng=random.Random(0))
    assert session.reveal(0) is False
    assert session.reveal(1) is True


def test_reveal_ignores_already_revealed_or_matched_card():
    session = MemoryGameSession(pair_count=3, rng=random.Random(0))
    session.reveal(0)
    assert session.reveal(0) is False  # same card twice


def test_resolve_without_two_revealed_raises():
    session = MemoryGameSession(pair_count=3, rng=random.Random(0))
    session.reveal(0)
    with pytest.raises(RuntimeError):
        session.resolve()


def test_matching_pair_marks_both_matched_and_counts_a_move():
    session = MemoryGameSession(pair_count=3, rng=random.Random(0))
    # find a real matching pair from the shuffled deck
    i = 0
    j = next(k for k in range(1, len(session.cards)) if session.cards[k] == session.cards[i])
    session.reveal(i)
    session.reveal(j)
    assert session.resolve() is True
    assert i in session.matched and j in session.matched
    assert session.moves == 1
    assert session.mismatches == 0
    assert session.revealed == []


def test_mismatched_pair_not_marked_matched_and_counts_a_mismatch():
    session = MemoryGameSession(pair_count=3, rng=random.Random(0))
    i = 0
    j = next(k for k in range(1, len(session.cards)) if session.cards[k] != session.cards[i])
    session.reveal(i)
    session.reveal(j)
    assert session.resolve() is False
    assert i not in session.matched and j not in session.matched
    assert session.moves == 1
    assert session.mismatches == 1


def test_is_complete_once_all_pairs_matched():
    session = MemoryGameSession(pair_count=1, rng=random.Random(0))
    session.reveal(0)
    session.reveal(1)
    session.resolve()
    assert session.is_complete
