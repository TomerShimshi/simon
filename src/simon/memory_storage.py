from datetime import datetime, timezone

from simon.kv_store import KeyValueStore, get_default_store

PROGRESS_KEY = "memory_progress_v1"
_EMPTY_PROGRESS = {"sessions": []}


class MemoryProgressStore:
    def __init__(self, store: KeyValueStore | None = None) -> None:
        self._store = store or get_default_store()
        self._data = self._store.load(PROGRESS_KEY, _EMPTY_PROGRESS)

    def _save(self) -> None:
        self._store.save(PROGRESS_KEY, self._data)

    def record_session(self, session_id: str, pair_count: int, moves: int, mismatches: int) -> None:
        self._data["sessions"].append(
            {
                "id": session_id,
                "date": datetime.now(timezone.utc).isoformat(),
                "pair_count": pair_count,
                "moves": moves,
                "mismatches": mismatches,
            }
        )
        self._save()

    def last_session(self) -> dict | None:
        sessions = self._data["sessions"]
        return sessions[-1] if sessions else None

    def best_moves_for(self, pair_count: int) -> int | None:
        """Fewest moves ever taken to complete a grid of this exact size --
        move counts aren't comparable across different grid sizes, so the
        record is tracked per size rather than as one overall best."""
        moves = [
            s["moves"] for s in self._data["sessions"] if s["pair_count"] == pair_count
        ]
        return min(moves, default=None)
