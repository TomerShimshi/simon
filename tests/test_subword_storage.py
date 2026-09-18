from simon.storage import new_session_id
from simon.subword_storage import SubWordProgressStore


def test_no_last_session_when_empty(tmp_path):
    store = SubWordProgressStore(storage_dir=tmp_path)
    assert store.last_session() is None


def test_record_and_read_last_session(tmp_path):
    store = SubWordProgressStore(storage_dir=tmp_path)
    store.record_session(new_session_id(), base_words=["שלום"], words_found_count=2, hints_used=1)
    last = store.last_session()
    assert last["base_words"] == ["שלום"]
    assert last["words_found_count"] == 2
    assert last["hints_used"] == 1


def test_persists_across_instances(tmp_path):
    store1 = SubWordProgressStore(storage_dir=tmp_path)
    store1.record_session(new_session_id(), base_words=["שלום"], words_found_count=1, hints_used=0)

    store2 = SubWordProgressStore(storage_dir=tmp_path)
    assert store2.last_session()["words_found_count"] == 1


def test_best_words_found_count_none_when_empty(tmp_path):
    store = SubWordProgressStore(storage_dir=tmp_path)
    assert store.best_words_found_count() is None


def test_best_words_found_count_tracks_the_max(tmp_path):
    store = SubWordProgressStore(storage_dir=tmp_path)
    store.record_session(new_session_id(), base_words=["שלום"], words_found_count=1, hints_used=0)
    store.record_session(new_session_id(), base_words=["מכתב"], words_found_count=3, hints_used=1)
    assert store.best_words_found_count() == 3
