"""reglages_audio.py : toutes les options audio du jeu.
"""

from pathlib import Path

ASSETS_AUDIO = Path(__file__).resolve().parent / "assets"
MUSIC_DIR = ASSETS_AUDIO / "sound"

MUSIC_TRACKS = {
    "menu": "menu/menu.mp3",
    "meadow": "meadow/meadow.mp3",
    "pub": "pub/pub.mp3",
    "cave": "cave/cave.mp3",
    "gold": "gold_city/gold.mp3",
}

MUSIC_VOLUME = 0.7
GAMEOVER_VOLUME = 1.0
MUSIC_FADE_IN_MS = 350

FALLBACK_MUSIC = None
GAMEOVER_SOUND = ASSETS_AUDIO / "gameover.wav"
