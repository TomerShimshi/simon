import flet as ft

from simon.app_state import AppState
from simon.ui_helpers import TEXT_SECONDARY, primary_button, rtl_text
from simon.user_profile import PROFILES


def build_profile_picker_view(page: ft.Page, state: AppState) -> ft.View:
    def make_handler(slug: str):
        async def handler(_: ft.ControlEvent) -> None:
            state.activate_profile(slug)
            # Setting ?user=<slug> here means bookmarking the page right
            # after this tap gives a URL that skips this screen forever.
            await page.push_route("/", user=slug)

        return handler

    buttons: list[ft.Control] = []
    for slug, label in PROFILES.items():
        buttons.append(primary_button(label, make_handler(slug)))
        buttons.append(ft.Container(height=14))

    return ft.View(
        route="/profile",
        controls=[
            ft.Column(
                [
                    rtl_text("מי משחק היום?", size=32, weight=ft.FontWeight.BOLD),
                    ft.Container(height=6),
                    rtl_text("בחרו את השם שלכם כדי לשמור את ההתקדמות שלכם", size=15, color=TEXT_SECONDARY),
                    ft.Container(height=28),
                    *buttons,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )
