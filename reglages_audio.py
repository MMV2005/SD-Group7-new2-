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

# None = détecte automatiquement la musique présente dans chaque dossier.
# Si plusieurs fichiers existent, remplacer None par leur nom exact.
MUSIC_FILES = {
    "menu": None,
    "meadow": None,
    "pub": None,
    "cave": None,
    "gold": None,
}

MUSIC_EXTENSIONS = (".ogg", ".mp3", ".wav", ".mid", ".midi")

MUSIC_VOLUME = 0.7
MUSIC_FADE_IN_MS = 350
GAMEOVER_VOLUME = 1.0
PICKUP_VOLUME = 1
PICKUP_COOLDOWN_MS = 60

# Sons ponctuels rangés directement dans assets/.
GAMEOVER_SOUND = ASSETS_AUDIO / "gameover.mp3"
PICKUP_SOUND = ASSETS_AUDIO / "pickup.mp3"
