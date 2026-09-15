import random

import pytest
from simon.session_manager import MAX_SEQUENCE_LENGTH, SimonSession


def test_starts_with_requested_length():
    session = SimonSession(start_length=3, rng=random.Random(0))
    assert session.current_length == 3


def test_correct_round_grows_sequence_and_updates_best():
    session = SimonSession(start_length=2, rng=random.Random(0))
    session.record_round(correct=True)
    assert session.current_length == 3
    assert session.best_length == 2
    assert session.rounds_played == 1
    assert session.rounds_correct == 1
    assert not session.finished


def test_single_miss_does_not_end_session():
    session = SimonSession(start_length=2, rng=random.Random(0))
    session.record_round(correct=False)
    assert not session.finished
    assert session.current_length == 2  # sequence doesn't grow on a miss


def test_second_consecutive_miss_ends_session():
    session = SimonSession(start_length=2, rng=random.Random(0))
    session.record_round(correct=False)
    session.record_round(correct=False)
    assert session.finished


def test_miss_streak_resets_after_a_correct_round():
    session = SimonSession(start_length=2, rng=random.Random(0))
    session.record_round(correct=False)
    session.record_round(correct=True)
    session.record_round(correct=False)
    assert not session.finished


def test_finishes_at_max_sequence_length():
    session = SimonSession(start_length=MAX_SEQUENCE_LENGTH, rng=random.Random(0))
    session.record_round(correct=True)
    assert session.finished
    assert session.best_length == MAX_SEQUENCE_LENGTH


def test_recording_after_finish_raises():
    session = SimonSession(start_length=2, rng=random.Random(0))
    session.record_round(correct=False)
    session.record_round(correct=False)
    with pytest.raises(RuntimeError):
        session.record_round(correct=True)


def test_accuracy_tracks_correct_over_played():
    session = SimonSession(start_length=2, rng=random.Random(0))
    session.record_round(correct=True)
    session.record_round(correct=False)
    assert session.accuracy == 0.5


def test_accuracy_zero_when_no_rounds_played():
    session = SimonSession(start_length=2, rng=random.Random(0))
    assert session.accuracy == 0.0


def test_sequence_values_are_valid_color_indices():
    session = SimonSession(start_length=10, rng=random.Random(0))
    assert all(0 <= c < 4 for c in session.sequence)
