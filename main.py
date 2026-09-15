import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import flet as ft

from simon.app_state import AppState
from simon.screens.game import build_game_view
from simon.screens.home import build_home_view
from simon.screens.summary import build_summary_view
from simon.storage import ProgressStore

ROUTE_BUILDERS = {
    "/": build_home_view,
    "/game": build_game_view,
    "/summary": build_summary_view,
}


def main(page: ft.Page) -> None:
    page.title = "סיימון"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 420
    page.window.height = 780

    state = AppState(progress=ProgressStore())

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
