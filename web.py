"""ASGI entrypoint for hosting the app as a persistent web service (Render).

Run with: uvicorn web:app --host 0.0.0.0 --port $PORT
Separate from main.py (the desktop dev entrypoint via `flet run`/`python
main.py`) because export_asgi_app=True returns a FastAPI app for a real
server to serve, rather than blocking to run Flet's own dev/desktop loop.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import flet as ft

from main import main

app = ft.run(main, assets_dir="assets", export_asgi_app=True)
