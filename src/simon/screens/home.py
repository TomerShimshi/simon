import flet as ft

from simon.app_state import AppState
from simon.ui_helpers import ACCENT, rtl_text


def _simon_caption(state: AppState) -> str:
    last = state.progress.last_session()
    if last is None:
        return "עדיין לא שיחקת"
    return f"בפעם הקודמת: רצף באורך {last['best_length']}"


def _memory_caption(state: AppState) -> str:
    last = state.memory_progress.last_session()
    if last is None:
        return "עדיין לא שיחקת"
    return f"בפעם הקודמת: {last['moves']} צעדים"


def _game_card(title: str, subtitle: str, caption: str, on_click) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                rtl_text(title, size=26, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Container(height=4),
                rtl_text(subtitle, size=16, color="#FFFFFF"),
                ft.Container(height=8),
                rtl_text(caption, size=14, color="#FFFFFF"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=ACCENT,
        border_radius=16,
        padding=24,
        width=300,
        on_click=on_click,
    )


def build_home_view(page: ft.Page, state: AppState) -> ft.View:
    async def start_simon(_: ft.ControlEvent) -> None:
        state.session = None  # let /simon build a fresh session starting at length 1
        await page.push_route("/simon")

    async def start_memory(_: ft.ControlEvent) -> None:
        state.memory_session = None  # let /memory build a fresh grid
        await page.push_route("/memory")

    return ft.View(
        route="/",
        controls=[
            ft.Column(
                [
                    rtl_text("משחקי אימון", size=40, weight=ft.FontWeight.BOLD),
                    ft.Container(height=8),
                    rtl_text("בחר משחק לתרגול", size=18),
                    ft.Container(height=24),
                    _game_card(
                        "סיימון",
                        "משחק זיכרון צבעים ורצפים",
                        _simon_caption(state),
                        start_simon,
                    ),
                    ft.Container(height=16),
                    _game_card(
                        "זיכרון קלפים",
                        "מצא את הזוגות התואמים",
                        _memory_caption(state),
                        start_memory,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )
