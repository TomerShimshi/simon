import flet as ft

BACKGROUND = "#FFFFFF"
TEXT_PRIMARY = "#1A1A1A"
ACCENT = ft.Colors.BLUE_600

# Unlit / lit pairs per pad -- the lit shade is a brightened version of the
# same hue so the flash reads clearly even to a viewer with reduced contrast
# sensitivity, without changing which color is which.
PAD_COLORS = {
    "red": "#C62828",
    "blue": "#1565C0",
    "green": "#2E7D32",
    "yellow": "#F9A825",
}
PAD_COLORS_LIT = {
    "red": "#FF6E63",
    "blue": "#66A3FF",
    "green": "#66BB6A",
    "yellow": "#FFE066",
}


def rtl_text(
    value: str,
    size: int = 20,
    weight: ft.FontWeight | None = None,
    color: str | None = None,
) -> ft.Text:
    return ft.Text(
        value,
        rtl=True,
        size=size,
        weight=weight,
        color=color or TEXT_PRIMARY,
        text_align=ft.TextAlign.CENTER,
    )


def primary_button(label: str, on_click) -> ft.ElevatedButton:
    return ft.ElevatedButton(
        content=rtl_text(label, size=26, color="#FFFFFF"),
        on_click=on_click,
        bgcolor=ACCENT,
        height=76,
        width=280,
    )
