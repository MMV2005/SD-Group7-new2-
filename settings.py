"""Reglages faciles a modifier pour Leprechaun Escape (Groupe 7)."""
from pathlib import Path

WINDOWWIDTH = 1000
WINDOWHEIGHT = 540
FPS = 60
CEILING = 95
FLOOR = 475

# Physique en pixels par seconde (les calculs utilisent dt).
GRAVITY = 750
COIN_THRUST = 1510
MAX_RISE_SPEED = -390
MAX_FALL_SPEED = 420

# La difficulte evolue avec la distance parcourue.
START_SPEED = 240
MAX_SPEED = 425

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