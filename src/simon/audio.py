import flet_audio as fa

from simon.models import COLORS

TONE_FILES = {
    "red": "sounds/tone_red.wav",
    "blue": "sounds/tone_blue.wav",
    "green": "sounds/tone_green.wav",
    "yellow": "sounds/tone_yellow.wav",
}
ERROR_SOUND = "sounds/error.wav"


class SoundBoard:
    """Wraps Flet Audio controls for the 4 color tones plus the error cue.

    Audio is a "service" control (no visible UI): it must be attached via a
    View's `services=` list, not added as a regular child control or mutated
    onto `page.services` after the fact (`page.services` only proxies to
    `page.views[0].services`, so it's unusable before a view exists and is
    the wrong place to add per-screen services anyway). `controls` below is
    handed straight to `ft.View(services=...)` by the caller.
    """

    def __init__(self) -> None:
        self._tones = {color: fa.Audio(src=path) for color, path in TONE_FILES.items()}
        self._error = fa.Audio(src=ERROR_SOUND)
        self.controls = [*self._tones.values(), self._error]

    async def play_color(self, index: int) -> None:
        await self._tones[COLORS[index]].play()

    async def play_error(self) -> None:
        await self._error.play()
