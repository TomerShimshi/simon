from dataclasses import dataclass

from simon.memory_session import MemoryGameSession
from simon.memory_storage import MemoryProgressStore
from simon.session_manager import SimonSession
from simon.storage import ProgressStore
from simon.subword_session import SubWordSession
from simon.subword_storage import SubWordProgressStore


@dataclass
class AppState:
    progress: ProgressStore
    memory_progress: MemoryProgressStore
    subword_bank: dict[str, list[str]]
    subword_clues: dict[str, str]
    subword_progress: SubWordProgressStore
    session: SimonSession | None = None
    memory_session: MemoryGameSession | None = None
    subword_session: SubWordSession | None = None
