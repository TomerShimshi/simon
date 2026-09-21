from datetime import date, timedelta

from simon.kv_store import KeyValueStore, get_default_store

PROGRESS_KEY = "engagement_v1"
_EMPTY = {"visit_dates": []}


class EngagementStore:
    """Tracks which calendar days the app was opened, for a warm "days
    practiced" streak -- deliberately designed to never punish a missed day:
    there is no penalty state, no "you lost your streak" messaging, and
    total_days_played() only ever grows. current_streak() quietly reflects
    whatever consecutive run currently includes today; if a day was missed,
    it simply starts counting again from today with no acknowledgement of
    the gap. This matches rehab-appropriate, non-punitive gamification
    design rather than loss-aversion-driven streak mechanics.
    """

    def __init__(self, store: KeyValueStore | None = None) -> None:
        self._store = store or get_default_store()
        self._data = self._store.load(PROGRESS_KEY, _EMPTY)

    def _save(self) -> None:
        self._store.save(PROGRESS_KEY, self._data)

    def record_visit(self, today: date | None = None) -> None:
        iso = (today or date.today()).isoformat()
        if iso not in self._data["visit_dates"]:
            self._data["visit_dates"].append(iso)
            self._data["visit_dates"].sort()
            self._save()

    def total_days_played(self) -> int:
        return len(self._data["visit_dates"])

    def current_streak(self, today: date | None = None) -> int:
        """Consecutive days ending today (0 if today itself has no visit
        recorded yet -- call record_visit() first each session)."""
        today = today or date.today()
        visited = set(self._data["visit_dates"])
        streak = 0
        day = today
        while day.isoformat() in visited:
            streak += 1
            day -= timedelta(days=1)
        return streak

    def last_n_days(self, n: int = 7, today: date | None = None) -> list[tuple[date, bool]]:
        """Oldest-to-newest list of (date, was_visited) for the last n days
        including today -- feeds a simple visual calendar strip."""
        today = today or date.today()
        visited = set(self._data["visit_dates"])
        return [
            (day, day.isoformat() in visited)
            for day in (today - timedelta(days=offset) for offset in range(n - 1, -1, -1))
        ]
