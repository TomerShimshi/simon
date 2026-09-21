"""One-off generator for the PWA app icons under assets/icons/.

Not run at app runtime -- Flet's web server picks these up automatically
from assets/manifest.json + assets/icons/ once generated. Re-run after
changing ICON_BG/ICON_EMOJI below.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).resolve().parents[1] / "assets" / "icons"
ICON_BG = "#3B5BDB"  # matches the Simon game accent -- the app's "flagship" color
ICON_EMOJI = "\U0001f9e0"  # brain -- represents cognitive training generally


def _emoji_font(size: int) -> ImageFont.FreeTypeFont:
    # Windows ships Segoe UI Emoji as a color font; PIL can render it via
    # its embedded bitmap strikes when given a large enough point size.
    candidates = [
        "C:/Windows/Fonts/seguiemj.ttf",
        "/System/Library/Fonts/Apple Color Emoji.ttc",
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    raise RuntimeError("No emoji-capable font found on this system")


def _rounded_square(size: int, radius_ratio: float, bg: str) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * radius_ratio), fill=bg)
    return img


def _icon_with_emoji(size: int, radius_ratio: float, emoji_scale: float) -> Image.Image:
    img = _rounded_square(size, radius_ratio, ICON_BG)
    font_size = int(size * emoji_scale)
    font = _emoji_font(font_size)
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), ICON_EMOJI, font=font, embedded_color=True)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pos = ((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1])
    draw.text(pos, ICON_EMOJI, font=font, embedded_color=True)
    return img


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Standard icons: rounded corners, emoji fills most of the canvas.
    for size in (192, 512):
        _icon_with_emoji(size, radius_ratio=0.22, emoji_scale=0.62).save(OUT_DIR / f"icon-{size}.png")

    # Maskable icons: OS may crop to a circle, so keep content inside the
    # ~80% "safe zone" and fill the full square with no rounding of our own.
    for size in (192, 512):
        _icon_with_emoji(size, radius_ratio=0.0, emoji_scale=0.5).save(
            OUT_DIR / f"icon-maskable-{size}.png"
        )

    # Also used as the browser tab favicon.
    _icon_with_emoji(32, radius_ratio=0.22, emoji_scale=0.62).save(OUT_DIR.parent / "favicon.png")

    print(f"Wrote icons to {OUT_DIR}")


if __name__ == "__main__":
    main()
