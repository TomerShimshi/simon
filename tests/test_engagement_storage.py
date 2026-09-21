from datetime import date, timedelta

from simon.engagement_storage import EngagementStore
from simon.kv_store import InMemoryKeyValueStore

TODAY = date(2026, 6, 15)


def test_no_days_played_when_empty():
    store = EngagementStore(store=InMemoryKeyValueStore())
    assert store.total_days_played() == 0
    assert store.current_streak(today=TODAY) == 0


def test_record_visit_increments_total_days():
    store = EngagementStore(store=InMemoryKeyValueStore())
    store.record_visit(today=TODAY)
    assert store.total_days_played() == 1


def test_recording_the_same_day_twice_does_not_double_count():
    store = EngagementStore(store=InMemoryKeyValueStore())
    store.record_visit(today=TODAY)
    store.record_visit(today=TODAY)
    assert store.total_days_played() == 1


def test_persists_across_instances():
    backend = InMemoryKeyValueStore()
    store1 = EngagementStore(store=backend)
    store1.record_visit(today=TODAY)

    store2 = EngagementStore(store=backend)
    assert store2.total_days_played() == 1


def test_current_streak_counts_consecutive_days_ending_today():
    store = EngagementStore(store=InMemoryKeyValueStore())
    for offset in range(3):
        store.record_visit(today=TODAY - timedelta(days=offset))
    assert store.current_streak(today=TODAY) == 3


def test_current_streak_ignores_days_before_a_gap():
    store = EngagementStore(store=InMemoryKeyValueStore())
    store.record_visit(today=TODAY)
    store.record_visit(today=TODAY - timedelta(days=1))
    store.record_visit(today=TODAY - timedelta(days=3))  # gap at day-2 breaks the run
    assert store.current_streak(today=TODAY) == 2


def test_current_streak_is_zero_when_today_not_recorded():
    store = EngagementStore(store=InMemoryKeyValueStore())
    store.record_visit(today=TODAY - timedelta(days=1))
    assert store.current_streak(today=TODAY) == 0


def test_a_missed_day_quietly_restarts_the_streak_without_losing_total():
    store = EngagementStore(store=InMemoryKeyValueStore())
    store.record_visit(today=TODAY - timedelta(days=10))
    store.record_visit(today=TODAY - timedelta(days=9))
    # big gap, then playing again today
    store.record_visit(today=TODAY)
    assert store.current_streak(today=TODAY) == 1
    assert store.total_days_played() == 3  # history is never erased


def test_last_n_days_oldest_to_newest_with_visited_flags():
    store = EngagementStore(store=InMemoryKeyValueStore())
    store.record_visit(today=TODAY)
    store.record_visit(today=TODAY - timedelta(days=2))

    days = store.last_n_days(3, today=TODAY)
    assert [d for d, _ in days] == [
        TODAY - timedelta(days=2),
        TODAY - timedelta(days=1),
        TODAY,
    ]
    assert [visited for _, visited in days] == [True, False, True]
