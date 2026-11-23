
"""Réglages centralisés des musiques et effets sonores."""

from pathlib import Path

ASSETS_AUDIO = Path(__file__).resolve().parent / "assets"
MUSIC_DIR = ASSETS_AUDIO / "sound"

# Clés utilisées par le jeu -> dossiers existants.
MUSIC_FOLDERS = {
    "menu": "menu",
    "meadow": "meadow",
    "pub": "pub",
    "cave": "cave",
    "gold": "gold_city",
}

# None = détecte automatiquement le fichier audio du dossier.
# Si plusieurs musiques existent, indique par exemple "musique.mp3".
MUSIC_FILES = {
    "menu": None,
    "meadow": None,
    "pub": None,
    "cave": None,
    "gold": None,
}

MUSIC_EXTENSIONS = (".ogg", ".mp3", ".wav", ".mid", ".midi")

MUSIC_VOLUME = 0.7
GAMEOVER_VOLUME = 1.0
MUSIC_FADE_IN_MS = 350

GAMEOVER_SOUND = ASSETS_AUDIO / "gameover.wav"
