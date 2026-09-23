from datetime import datetime, timezone

from simon.kv_store import KeyValueStore, get_default_store

PROGRESS_KEY = "subword_progress_v1"
_EMPTY_PROGRESS = {"sessions": []}


class SubWordProgressStore:
    def __init__(self, store: KeyValueStore | None = None) -> None:
        self._store = store or get_default_store()
        self._data = self._store.load(PROGRESS_KEY, _EMPTY_PROGRESS)

    def _save(self) -> None:
        self._store.save(PROGRESS_KEY, self._data)

    def record_session(
        self,
        session_id: str,
        base_words: list[str],
        words_found_count: int,
        hints_used: int,
    ) -> None:
        self._data["sessions"].append(
            {
                "id": session_id,
                "date": datetime.now(timezone.utc).isoformat(),
                "base_words": base_words,
                "words_found_count": words_found_count,
                "hints_used": hints_used,
            }
        )
        self._save()

    def last_session(self) -> dict | None:
        sessions = self._data["sessions"]
        return sessions[-1] if sessions else None

    def recent_sessions(self, n: int = 10) -> list[dict]:
        return self._data["sessions"][-n:]

    def best_words_found_count(self) -> int | None:
        counts = [s["words_found_count"] for s in self._data["sessions"]]
        return max(counts, default=None)
