"""Reglages faciles a modifier pour Leprechaun Escape (Groupe 7)."""
from pathlib import Path

WINDOWWIDTH = 1000
WINDOWHEIGHT = 540
FPS = 60
CEILING = 95
FLOOR = 475

# La difficulte evolue avec la distance parcourue.
START_SPEED = 240
MAX_SPEED = 425

GRAVITY = 0.7        # accélération vers le bas, en pixels par frame au carré
THRUST = 1.4         # accélération vers le haut quand espace est maintenue
MAX_FALL_SPEED = 10  # vitesse de chute maximale (évite une chute trop violente)
MAX_RISE_SPEED = 9   # vitesse de montée maximale

# Bonus: durees en secondes.
CLOVER_TIME = 5.0
POT_TIME = 7.0
GUINNESS_TIME = 6.0

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
RECORD_FILE = ROOT / 'record.json'


def clamp(number, minimum, maximum):
    """Limite un nombre a l'intervalle choisi."""
    return max(minimum, min(maximum, number))
