import json
from datetime import datetime, timezone
from pathlib import Path

from simon.storage_paths import storage_dir as _default_storage_dir

PROGRESS_FILENAME = "subword_progress_v1.json"
_EMPTY_PROGRESS = {"sessions": []}


class SubWordProgressStore:
    def __init__(self, storage_dir: Path | None = None) -> None:
        self._path = (storage_dir or _default_storage_dir()) / PROGRESS_FILENAME
        self._data = self._load()

    def _load(self) -> dict:
        if not self._path.is_file():
            return json.loads(json.dumps(_EMPTY_PROGRESS))
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return json.loads(json.dumps(_EMPTY_PROGRESS))

    def _save(self) -> None:
        self._path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

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

    def best_words_found_count(self) -> int | None:
        counts = [s["words_found_count"] for s in self._data["sessions"]]
        return max(counts, default=None)
