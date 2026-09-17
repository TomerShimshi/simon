import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import flet as ft

from simon.app_state import AppState
from simon.memory_storage import MemoryProgressStore
from simon.screens.home import build_home_view
from simon.screens.memory_game import build_memory_game_view
from simon.screens.memory_summary import build_memory_summary_view
from simon.screens.simon_game import build_simon_game_view
from simon.screens.simon_summary import build_simon_summary_view
from simon.storage import ProgressStore

ROUTE_BUILDERS = {
    "/": build_home_view,
    "/simon": build_simon_game_view,
    "/simon/summary": build_simon_summary_view,
    "/memory": build_memory_game_view,
    "/memory/summary": build_memory_summary_view,
}


def main(page: ft.Page) -> None:
    page.title = "משחקי אימון"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 420
    page.window.height = 780

    state = AppState(progress=ProgressStore(), memory_progress=MemoryProgressStore())

    def render_current_route(*_args) -> None:
        builder = ROUTE_BUILDERS.get(page.route, build_home_view)
        # reset per-screen handlers so a stale closure from the previous
        # screen never outlives its view
        page.on_resize = None
        page.views.clear()
        page.views.append(builder(page, state))
        page.update()

    page.on_route_change = render_current_route
    render_current_route()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
