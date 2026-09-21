import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import flet as ft

from simon.app_state import AppState
from simon.engagement_storage import EngagementStore
from simon.memory_storage import MemoryProgressStore
from simon.screens.home import build_home_view
from simon.screens.memory_game import build_memory_game_view
from simon.screens.memory_summary import build_memory_summary_view
from simon.screens.simon_game import build_simon_game_view
from simon.screens.simon_summary import build_simon_summary_view
from simon.screens.subword_game import build_subword_game_view
from simon.screens.subword_summary import build_subword_summary_view
from simon.storage import ProgressStore
from simon.subword_bank import load_bank, load_clues
from simon.subword_storage import SubWordProgressStore
from simon.ui_helpers import BACKGROUND

ROUTE_BUILDERS = {
    "/": build_home_view,
    "/simon": build_simon_game_view,
    "/simon/summary": build_simon_summary_view,
    "/memory": build_memory_game_view,
    "/memory/summary": build_memory_summary_view,
    "/subword": build_subword_game_view,
    "/subword/summary": build_subword_summary_view,
}


def main(page: ft.Page) -> None:
    page.title = "משחקי אימון"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = BACKGROUND
    page.window.width = 420
    page.window.height = 780

    state = AppState(
        progress=ProgressStore(),
        memory_progress=MemoryProgressStore(),
        subword_bank=load_bank(),
        subword_clues=load_clues(),
        subword_progress=SubWordProgressStore(),
        engagement=EngagementStore(),
    )
    state.engagement.record_visit()  # once per app session, i.e. once per day opened

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
