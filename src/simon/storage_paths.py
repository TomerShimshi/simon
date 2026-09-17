import os
from pathlib import Path


def storage_dir() -> Path:
    # Set synchronously by the Flet runtime (desktop and Android alike).
    # Fall back to a local dir for plain `python main.py` / tests outside Flet.
    env_dir = os.environ.get("FLET_APP_STORAGE_DATA")
    result = Path(env_dir) if env_dir else Path(__file__).resolve().parents[2] / ".local_data"
    result.mkdir(parents=True, exist_ok=True)
    return result
