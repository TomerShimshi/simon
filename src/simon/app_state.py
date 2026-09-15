from dataclasses import dataclass

from simon.session_manager import SimonSession
from simon.storage import ProgressStore


@dataclass
class AppState:
    progress: ProgressStore
    session: SimonSession | None = None
