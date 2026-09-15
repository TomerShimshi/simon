from simon.storage import ProgressStore, new_session_id


def test_no_last_session_when_empty(tmp_path):
    store = ProgressStore(storage_dir=tmp_path)
    assert store.last_session() is None


def test_record_and_read_last_session(tmp_path):
    store = ProgressStore(storage_dir=tmp_path)
    store.record_session(
        new_session_id(), best_length=4, rounds_played=5, rounds_correct=4, step_ms=900
    )
    last = store.last_session()
    assert last["best_length"] == 4
    assert last["rounds_played"] == 5
    assert last["rounds_correct"] == 4
    assert last["step_ms"] == 900


def test_persists_across_instances(tmp_path):
    store1 = ProgressStore(storage_dir=tmp_path)
    store1.record_session(
        new_session_id(), best_length=3, rounds_played=3, rounds_correct=3, step_ms=900
    )

    store2 = ProgressStore(storage_dir=tmp_path)
    assert store2.last_session()["best_length"] == 3


def test_adaptive_step_ms_defaults_when_no_history(tmp_path):
    store = ProgressStore(storage_dir=tmp_path)
    assert store.adaptive_step_ms() == 900


def test_adaptive_step_ms_speeds_up_after_strong_accuracy(tmp_path):
    store = ProgressStore(storage_dir=tmp_path)
    for _ in range(3):
        store.record_session(
            new_session_id(), best_length=10, rounds_played=10, rounds_correct=10, step_ms=900
        )
    assert store.adaptive_step_ms() == 750


def test_adaptive_step_ms_slows_down_after_poor_accuracy(tmp_path):
    store = ProgressStore(storage_dir=tmp_path)
    for _ in range(3):
        store.record_session(
            new_session_id(), best_length=4, rounds_played=10, rounds_correct=3, step_ms=900
        )
    assert store.adaptive_step_ms() == 1050


def test_best_length_ever_tracks_the_max(tmp_path):
    store = ProgressStore(storage_dir=tmp_path)
    assert store.best_length_ever() == 0
    store.record_session(new_session_id(), best_length=5, rounds_played=5, rounds_correct=5, step_ms=900)
    store.record_session(new_session_id(), best_length=3, rounds_played=3, rounds_correct=3, step_ms=900)
    store.record_session(new_session_id(), best_length=8, rounds_played=8, rounds_correct=8, step_ms=900)
    assert store.best_length_ever() == 8


def test_recent_sessions_limited_to_window(tmp_path):
    store = ProgressStore(storage_dir=tmp_path)
    for i in range(5):
        store.record_session(
            new_session_id(), best_length=i, rounds_played=1, rounds_correct=1, step_ms=900
        )
    recent = store.recent_sessions()
    assert len(recent) == 3
    assert [s["best_length"] for s in recent] == [2, 3, 4]
