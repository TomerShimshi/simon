import flet as ft

from simon.app_state import AppState
from simon.storage import new_session_id
from simon.subword_session import CheckResult, SubWordSession
from simon.ui_helpers import ACCENT, primary_button, rtl_text

TILE_COLOR = ACCENT
TILE_USED_COLOR = "#C7D7EE"

FEEDBACK_TEXT = {
    CheckResult.FOUND: "מצוין! מצאת מילה",
    CheckResult.ALREADY_FOUND: "כבר מצאת את המילה הזאת",
    CheckResult.NOT_A_WORD: "זאת לא מילה תקנית, בואו ננסה שוב",
    CheckResult.TOO_SHORT: "צריך לבחור לפחות שתי אותיות",
}


def build_subword_game_view(page: ft.Page, state: AppState) -> ft.View:
    session = state.subword_session
    if session is None:
        session = SubWordSession(state.subword_bank, state.subword_clues)
        state.subword_session = session

    session_log_id = new_session_id()

    base_word_label = rtl_text("", size=32, weight=ft.FontWeight.BOLD)
    attempt_label = rtl_text("", size=28)
    feedback_label = rtl_text("", size=18)
    found_words_label = rtl_text("", size=18)
    tiles: dict[int, ft.Container] = {}

    def render_tile(index: int) -> None:
        tile = tiles[index]
        tile.bgcolor = TILE_USED_COLOR if index in session.current_attempt else TILE_COLOR

    def render_all() -> None:
        base_word_label.value = session.base_word
        for i in tiles:
            render_tile(i)
        attempt_label.value = session.current_attempt_display()
        found_words_label.value = (
            "מילים שמצאת במילה הזאת: " + ", ".join(session.found_words)
            if session.found_words
            else "עדיין לא מצאת מילים במילה הזאת -- נסו לגעת באותיות!"
        )

    def build_tile(index: int) -> ft.Container:
        async def on_click(_: ft.ControlEvent) -> None:
            session.tap_tile(index)
            render_all()
            page.update()

        tile = ft.Container(
            content=rtl_text(session.tiles[index], size=30, color="#FFFFFF"),
            bgcolor=TILE_COLOR,
            border_radius=12,
            width=64,
            height=64,
            alignment=ft.Alignment(0, 0),
            on_click=on_click,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )
        tiles[index] = tile
        return tile

    tile_row = ft.Row(
        [build_tile(i) for i in range(len(session.tiles))],
        wrap=True,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
        run_spacing=10,
    )

    def rebuild_tiles() -> None:
        tiles.clear()
        tile_row.controls = [build_tile(i) for i in range(len(session.tiles))]

    async def check(_: ft.ControlEvent) -> None:
        result = session.check_attempt()
        feedback_label.value = FEEDBACK_TEXT[result]
        render_all()
        page.update()

    async def undo(_: ft.ControlEvent) -> None:
        session.undo_last()
        render_all()
        page.update()

    async def clear(_: ft.ControlEvent) -> None:
        session.clear_attempt()
        render_all()
        page.update()

    async def show_clue(_: ft.ControlEvent) -> None:
        clue = session.get_clue()
        feedback_label.value = f'רמז: "{clue}"' if clue else "כבר מצאת את כל המילים!"
        render_all()
        page.update()

    async def reveal(_: ft.ControlEvent) -> None:
        revealed = session.reveal_word()
        feedback_label.value = f'המילה הייתה: "{revealed}"' if revealed else "כבר מצאת את כל המילים!"
        render_all()
        page.update()

    async def new_word(_: ft.ControlEvent) -> None:
        session.new_base_word()
        rebuild_tiles()
        feedback_label.value = ""
        render_all()
        page.update()

    async def finish_session(_: ft.ControlEvent) -> None:
        state.subword_progress.record_session(
            session_log_id,
            base_words=session.base_words_shown,
            words_found_count=session.total_found_count,
            hints_used=session.hints_used,
        )
        await page.push_route("/subword/summary")

    async def exit_to_home(_: ft.ControlEvent) -> None:
        state.subword_session = None
        await page.push_route("/")

    render_all()

    return ft.View(
        route="/subword",
        controls=[
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.TextButton(content=rtl_text("סיום", size=16), on_click=finish_session),
                            ft.TextButton(
                                content=rtl_text("חזרה לתפריט", size=16), on_click=exit_to_home
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    rtl_text("בנו מילים מהאותיות", size=18),
                    base_word_label,
                    ft.Container(content=tile_row, padding=16),
                    attempt_label,
                    ft.Row(
                        [
                            primary_button("בדוק", check),
                            ft.TextButton(content=rtl_text("נקה", size=16), on_click=clear),
                            ft.TextButton(content=rtl_text("ביטול", size=16), on_click=undo),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        [
                            ft.TextButton(content=rtl_text("רמז", size=16), on_click=show_clue),
                            ft.TextButton(content=rtl_text("גלה מילה", size=16), on_click=reveal),
                            ft.TextButton(content=rtl_text("מילה חדשה", size=16), on_click=new_word),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    feedback_label,
                    found_words_label,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )
