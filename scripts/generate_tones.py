"""Generates the 4 pad tones + error cue as WAV files into assets/sounds/.

Stdlib-only (wave + math), no audio libraries needed. Re-run after changing
NOTES/DURATIONS below to regenerate the committed assets.
"""

import math
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 44100
ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets" / "sounds"

# A bright major-chord arpeggio (C5-E5-G5-C6) rather than the harsh buzzer
# tones of a classic Simon toy -- pleasant to listen to across dozens of
# repetitions in a practice session, which matters for a rehab exercise
# that's meant to be played daily.
NOTES = {
    "tone_green": 523.25,  # C5
    "tone_red": 659.25,  # E5
    "tone_yellow": 783.99,  # G5
    "tone_blue": 1046.50,  # C6
}
NOTE_DURATION_S = 0.6

# Piano-ish timbre: a handful of harmonics, each decaying faster than the
# one below it (as on a real piano, higher partials die out first), summed
# under a short attack + exponential decay envelope. Plain sine tones read
# as an alarm/buzzer; this reads as a struck note.
HARMONICS = [  # (multiple of fundamental, relative amplitude, decay rate)
    (1, 1.00, 2.2),
    (2, 0.55, 3.2),
    (3, 0.30, 4.4),
    (4, 0.15, 5.8),
]
ATTACK_S = 0.005
RELEASE_S = 0.03  # final linear fade to zero, avoids a click at the cutoff


def _piano_samples(freq: float, duration_s: float) -> list[float]:
    n = int(SAMPLE_RATE * duration_s)
    attack_n = int(SAMPLE_RATE * ATTACK_S)
    release_n = int(SAMPLE_RATE * RELEASE_S)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        value = sum(
            amp * math.exp(-decay * t) * math.sin(2 * math.pi * freq * mult * t)
            for mult, amp, decay in HARMONICS
        )
        if i < attack_n:
            value *= i / attack_n
        elif i > n - release_n:
            value *= (n - i) / release_n
        samples.append(value)
    peak = max(abs(v) for v in samples) or 1.0
    return [v / peak for v in samples]


def _to_pcm16(samples: list[float], volume: float = 0.6) -> list[int]:
    return [int(max(-1.0, min(1.0, v)) * volume * 32767) for v in samples]


def _write_wav(path: Path, pcm_samples: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(struct.pack(f"<{len(pcm_samples)}h", *pcm_samples))


def main() -> None:
    for name, freq in NOTES.items():
        _write_wav(ASSETS_DIR / f"{name}.wav", _to_pcm16(_piano_samples(freq, NOTE_DURATION_S)))

    # error cue: a soft, gentle two-note descending phrase (G4 -> C4) rather
    # than a harsh buzz -- feedback for a wrong answer should never feel
    # punitive, per rehab-game design guidance.
    g4 = _piano_samples(392.00, 0.28)
    c4 = _piano_samples(261.63, 0.35)
    gap = [0.0] * int(SAMPLE_RATE * 0.05)
    _write_wav(ASSETS_DIR / "error.wav", _to_pcm16(g4 + gap + c4, volume=0.5))

    print(f"Wrote {len(NOTES) + 1} sound files to {ASSETS_DIR}")


if __name__ == "__main__":
    main()
