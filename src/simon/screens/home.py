import flet as ft

from simon.app_state import AppState
from simon.ui_helpers import primary_button, rtl_text


def _last_session_summary(state: AppState) -> str:
    last = state.progress.last_session()
    if last is None:
        return "עדיין לא שיחקת. בואו נתחיל!"
    return f"בפעם הקודמת הגעת לרצף באורך {last['best_length']}"


def build_home_view(page: ft.Page, state: AppState) -> ft.View:
    summary_text = rtl_text(_last_session_summary(state), size=18)

    async def start_game(_: ft.ControlEvent) -> None:
        state.session = None  # let /game build a fresh session starting at length 1
        await page.push_route("/game")

    return ft.View(
        route="/",
        controls=[
            ft.Column(
                [
                    rtl_text("סיימון", size=44, weight=ft.FontWeight.BOLD),
                    ft.Container(height=8),
                    rtl_text("משחק זיכרון צבעים", size=20),
                    ft.Container(height=24),
                    summary_text,
                    ft.Container(height=32),
                    primary_button("התחל משחק", start_game),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )
