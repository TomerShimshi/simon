from simon.kv_store import InMemoryKeyValueStore
from simon.storage import new_session_id
from simon.subword_storage import SubWordProgressStore


def test_no_last_session_when_empty():
    store = SubWordProgressStore(store=InMemoryKeyValueStore())
    assert store.last_session() is None


def test_record_and_read_last_session():
    store = SubWordProgressStore(store=InMemoryKeyValueStore())
    store.record_session(new_session_id(), base_words=["שלום"], words_found_count=2, hints_used=1)
    last = store.last_session()
    assert last["base_words"] == ["שלום"]
    assert last["words_found_count"] == 2
    assert last["hints_used"] == 1


def test_persists_across_instances():
    backend = InMemoryKeyValueStore()
    store1 = SubWordProgressStore(store=backend)
    store1.record_session(new_session_id(), base_words=["שלום"], words_found_count=1, hints_used=0)

    store2 = SubWordProgressStore(store=backend)
    assert store2.last_session()["words_found_count"] == 1


def test_best_words_found_count_none_when_empty():
    store = SubWordProgressStore(store=InMemoryKeyValueStore())
    assert store.best_words_found_count() is None


def test_best_words_found_count_tracks_the_max():
    store = SubWordProgressStore(store=InMemoryKeyValueStore())
    store.record_session(new_session_id(), base_words=["שלום"], words_found_count=1, hints_used=0)
    store.record_session(new_session_id(), base_words=["מכתב"], words_found_count=3, hints_used=1)
    assert store.best_words_found_count() == 3
