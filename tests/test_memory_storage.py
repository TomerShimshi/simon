from simon.kv_store import InMemoryKeyValueStore
from simon.memory_storage import MemoryProgressStore
from simon.storage import new_session_id


def test_no_last_session_when_empty():
    store = MemoryProgressStore(store=InMemoryKeyValueStore())
    assert store.last_session() is None


def test_record_and_read_last_session():
    store = MemoryProgressStore(store=InMemoryKeyValueStore())
    store.record_session(new_session_id(), pair_count=3, moves=5, mismatches=2)
    last = store.last_session()
    assert last["pair_count"] == 3
    assert last["moves"] == 5
    assert last["mismatches"] == 2


def test_persists_across_instances():
    backend = InMemoryKeyValueStore()
    store1 = MemoryProgressStore(store=backend)
    store1.record_session(new_session_id(), pair_count=3, moves=4, mismatches=1)

    store2 = MemoryProgressStore(store=backend)
    assert store2.last_session()["moves"] == 4


def test_best_moves_for_returns_none_when_no_sessions_at_that_size():
    store = MemoryProgressStore(store=InMemoryKeyValueStore())
    assert store.best_moves_for(3) is None


def test_best_moves_for_tracks_fewest_per_grid_size():
    store = MemoryProgressStore(store=InMemoryKeyValueStore())
    store.record_session(new_session_id(), pair_count=3, moves=8, mismatches=5)
    store.record_session(new_session_id(), pair_count=3, moves=4, mismatches=1)
    store.record_session(new_session_id(), pair_count=5, moves=3, mismatches=0)

    assert store.best_moves_for(3) == 4
    assert store.best_moves_for(5) == 3
