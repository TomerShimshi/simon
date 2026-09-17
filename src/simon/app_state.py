from dataclasses import dataclass

from simon.memory_session import MemoryGameSession
from simon.memory_storage import MemoryProgressStore
from simon.session_manager import SimonSession
from simon.storage import ProgressStore


@dataclass
class AppState:
    progress: ProgressStore
    memory_progress: MemoryProgressStore
    session: SimonSession | None = None
    memory_session: MemoryGameSession | None = None
