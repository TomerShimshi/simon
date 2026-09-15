import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROGRESS_FILENAME = "progress_v1.json"
_EMPTY_PROGRESS = {"sessions": []}

DEFAULT_STEP_MS = 900
MIN_STEP_MS = 500
MAX_STEP_MS = 1100
SESSIONS_FOR_ADAPTATION = 3


def _storage_dir() -> Path:
    # Set synchronously by the Flet runtime (desktop and Android alike).
    # Fall back to a local dir for plain `python main.py` / tests outside Flet.
    env_dir = os.environ.get("FLET_APP_STORAGE_DATA")
    storage_dir = Path(env_dir) if env_dir else Path(__file__).resolve().parents[2] / ".local_data"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir


class ProgressStore:
    def __init__(self, storage_dir: Path | None = None) -> None:
        self._path = (storage_dir or _storage_dir()) / PROGRESS_FILENAME
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
        best_length: int,
        rounds_played: int,
        rounds_correct: int,
        step_ms: int,
    ) -> None:
        """Persisted once at session end -- unlike a long multi-scene practice
        session, a Simon session is a short handful of rounds, so there is
        little to lose by saving here rather than per-round."""
        self._data["sessions"].append(
            {
                "id": session_id,
                "date": datetime.now(timezone.utc).isoformat(),
                "best_length": best_length,
                "rounds_played": rounds_played,
                "rounds_correct": rounds_correct,
                "step_ms": step_ms,
            }
        )
        self._save()

    def last_session(self) -> dict | None:
        sessions = self._data["sessions"]
        return sessions[-1] if sessions else None

    def best_length_ever(self) -> int:
        sessions = self._data["sessions"]
        return max((s["best_length"] for s in sessions), default=0)

    def recent_sessions(self, n: int = SESSIONS_FOR_ADAPTATION) -> list[dict]:
        return self._data["sessions"][-n:]

    def adaptive_step_ms(self) -> int:
        """Returns the playback speed (ms per flash) for a new session.

        Every session always starts a fresh sequence at length 1 -- a stroke
        survivor re-practicing memory should get the same clean restart each
        time, not be dropped into a longer sequence because a past session
        went well. Only *playback speed* adapts: faster after recent strong
        accuracy, slower after recent struggling, so no caregiver has to
        tune a difficulty setting by hand.
        """
        recent = self.recent_sessions()
        if not recent:
            return DEFAULT_STEP_MS

        total_played = sum(s["rounds_played"] for s in recent)
        total_correct = sum(s["rounds_correct"] for s in recent)
        avg_accuracy = total_correct / total_played if total_played else 0.0

        step_ms = DEFAULT_STEP_MS
        if avg_accuracy >= 0.75:
            step_ms -= 150
        elif avg_accuracy < 0.6:
            step_ms += 150
        return max(MIN_STEP_MS, min(MAX_STEP_MS, step_ms))


def new_session_id() -> str:
    return str(uuid.uuid4())
