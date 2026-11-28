"""Shared configuration for the game. Distances use metres; screen coordinates use pixels."""
from pathlib import Path

from reglages_personnages import *  # Other modules import character settings through this module.

# settings.1 — Locate resources relative to this file.
# Use the folder containing settings.py, even when the game starts from another directory.
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'                        # Join the project folder and the assets folder with the Path / operator.
# Path reserved for the record file. This assignment alone does not save a score.
RECORD_FILE = ROOT / 'record.json'

# settings.2 — Window dimensions, target frame rate and playable vertical bounds.
# Window width and height in pixels, followed by the target frames per second.
WINDOWWIDTH, WINDOWHEIGHT, FPS = 960, 540, 60
WIDTH, HEIGHT = WINDOWWIDTH, WINDOWHEIGHT                   # Short names used by modules that read the same window dimensions.
CEILING, FLOOR = 90, 475                                    # Top and bottom of the playable area. Larger y values are lower on screen.
TEXTCOLOR = (255, 255, 255)                                 # White text, expressed as red, green and blue values.

# settings.3 — Horizontal speed (px/s), acceleration per metre and distance conversion.
START_SPEED, MAX_SPEED = 300, 580                           # Initial and maximum scrolling speeds (px/s).
SPEED_PER_METER = 0.045                                     # Every 1,000 metres adds 45 px/s until the speed cap is reached.
METERS_PER_PIXEL = 0.1                                      # Ten pixels of scrolling count as one metre of progress.

# settings.4 — Portal spacing (m), transition duration and safe time (s).
# Random distance added to the current distance for the next ordinary portal (m).
PORTAL_MIN, PORTAL_MAX = 600, 700
TRANSITION_SECONDS = 1.6                                    # Duration setting for the world-change animation (s).
SAFE_SECONDS = 1.0                                          # Grace period after a transition before hazards can spawn or hit the player (s).

# settings.5 — Coin patterns: counts and geometry (px); intervals are in seconds.
COIN_INTERVAL = (3.4, 4.8)                                  # Range of delays between groups of coins in ordinary worlds (s).
COINS_PER_WAVE = 5                                          # Number of coins in a wave.
RADIUS = 12                                                 # Half the width of a coin sprite and its square pickup rectangle (px).
SPACING = 43                                                # Horizontal distance between neighbouring coin centres in a wave or zigzag (px).
WAVE_AMPLITUDE = 24                                         # Maximum vertical offset from the centre of the wave (px).
CIRCLE_R = 50                                               # Distance from the centre of a circular pattern to each coin centre (px).
CIRCLE_N = 8                                                # Number of coins distributed around the circle.
CROSS_UNIT = 36                                             # Distance from the centre coin to each arm of the cross (px).
ZIGZAG_AMPLITUDE = 15                                       # Vertical offset above or below the middle of the zigzag (px).
COINS_PER_ZIGZAG = 7                                        # Number of coins in a zigzag.

# settings.6 — Spawn intervals (s), distance thresholds (m) and horizontal spacing.
OBSTACLE_INTERVAL_START = 1.6                               # Starting interval used to schedule the next obstacle after a successful spawn (s).
OBSTACLE_INTERVAL_MIN = 0.60                                # Lower limit on that interval as difficulty increases (s).
DENSITY_MAX_DISTANCE = 3500                                 # Distance at which the base spawn interval reaches its minimum (m).
TWO_OBSTACLES_DISTANCE = 2000                               # From this distance, two hazards may be active at once (m).
THREE_OBSTACLES_DISTANCE = 3500                             # From this distance, three hazards may be active at once (m).
OBSTACLE_GAP_MIN = 260                                      # Minimum horizontal centre-to-centre gap between moving hazards at spawn (px).
OBSTACLE_GAP_SECONDS = 0.60                                 # Multiply by scroll speed to get the speed-dependent gap (px).

# Repeated heights make those vertical positions more likely when sampled.
MEADOW_HEIGHTS = (130, 130, 175, 200, 285, 285, 365, 385)
PUB_HEIGHTS = (130, 130, 130, 165, 200, 240, 285, 285, 365, 375)

# settings.7 — Barrel acceleration (px/s²), scroll multiplier, upward impulse (px/s) and mug spin (deg/s).
BARREL_GRAVITY = 800                                        # Downward acceleration applied during each barrel bounce (px/s²).
BARREL_SPEED_RANGE = (0.85, 1.25)                           # A barrel moves at 85% to 125% of the world's scroll speed.
BARREL_JUMP_RANGE = (220.0, 500.0)                          # Range of upward launch speeds drawn for a barrel bounce (px/s).
MUG_SPIN_SPEED = 210.0                                      # Rotation speed of a flying mug (degrees/s).

# settings.8 — Launcher sprite bounds and muzzle location as fractions of width and height.
LAUNCHERS = {'cannon': ((210, 150), (0.09, 0.53)),
             'flame': ((220, 200), (0.24, 0.59))}

# The jet is active from JET_WARNING until JET_END, measured from spawn (s).
JET_WARNING, JET_END = 1.5, 2.5                             # The jet starts firing at age 1.5 s and stops at age 2.5 s.
JET_HEIGHT = 60                                             # Height of the scaled jet pattern (px).
LASER_SCROLL_SPEED = 500.0                                  # Speed at which the jet pattern moves to the left (px/s).
LASER_TILE_GAP = 0                                          # Horizontal space between repeated jet tiles (px). Zero joins them edge to edge.
LAUNCHER_HOLD_SECONDS = 0.6                                 # Time the launcher stays fully visible after firing (s).
LAUNCHER_FADE_SECONDS = 0.35                                # Time for the launcher to fade out after the hold period (s).

# Launcher eligibility (m), simultaneous launcher count and firing-line separation (px).
# First distance at which each world's launcher can be drawn as a candidate (m).
LAUNCHER_MIN_DISTANCE = {'pub': 0,  'cave': 0}              # Minimum distance for each world to have a launcher
LAUNCHER_MIX_DISTANCE = 6000                                # From this distance, launchers can share the screen with other hazards (m).
MAX_LAUNCHERS = 2                                           # Maximum active launchers, subject to firing-line spacing.
LAUNCHER_VERTICAL_GAP = 150                                 # Minimum distance between the heights of two jets (px).

# settings.9 — Maximum sprite bounds; each fence variant gets its own lookup key.
# Each width-height pair sets the bounds for one fence variant (px).
FENCE_SIZES = ((112, 72), (208, 72), (112, 112), (208, 112))
OBSTACLE_SIZES = {
    'goose': (100, 90), 'red_goose': (100, 90), 'bat': (85, 60),
    'barrel': (80, 72), 'mug': (44, 48),
    'rock_floor': (88, 143), 'rock_ceiling': (88, 143),
    'rock_horizontal': (160, 60), 'rock_vertical': (52, 138),
    'rock_diagonal': (145, 132),
    'cannon': LAUNCHERS['cannon'][0], 'flame': LAUNCHERS['flame'][0],
    # Build fence_0 through fence_3 from the four sizes above.
    **{f'fence_{i}': size for i, size in enumerate(FENCE_SIZES)}}

# settings.10 — Gold world: entry requirement, pot sprite, spawn timing and bonus-world pace.
POT_REQUIRED = 3                                            # Number of pots needed to enter the gold world.
POT_FILE = ASSETS / 'bonus' / 'pot_of_gold.png'             # File path for the pot of gold asset.
POT_SIZE = (52, 52)                                         # Maximum width and height of the pot sprite (px).
POT_SPAWN_INTERVAL = (1, 2)                          # Range of delays between pot spawn attempts (s).
GOLD_SECONDS = 1.0                                         # Playable time in the gold world (s).
GOLD_SPEED = 500.0                                          # Scroll speed during the gold bonus (px/s).
GOLD_COIN_INTERVAL = (1.7, 2.0)                             # Shorter delay between coin groups in the gold world (s).

# settings.11 — Enabled pickups and their effects. Collecting a timed pickup refreshes its duration.
GUINNESS_TIME = 6.0                                         # Duration of the beer's double-coin effect (s).
CLOVER_TIME = 5.0                                           # Duration of the clover shield (s).
BONUS_DEFINITIONS = {
    'pot': {
        'enabled': True, 'file': POT_FILE, 'size': POT_SIZE,
        'interval': POT_SPAWN_INTERVAL, 'worlds': ('meadow', 'pub', 'cave'),
        'effect': 'count', 'limit': POT_REQUIRED,},
    
    'beer': {
        'enabled': True, 'file': ASSETS / 'bonus' / 'beer_mug.png',
        'size': (44, 48), 'interval': (12.0, 18.0),
        'worlds': ('pub',),  # The trailing comma makes this a tuple containing one world.
        'effect': 'coin_multiplier', 'duration': GUINNESS_TIME, 'value': 2,},
    'clover': {
        'enabled': True, 'file': ASSETS / 'bonus' / 'clover.png',
        'size': (44, 44), 'interval': (15.0, 22.0),
        'worlds': ('meadow', 'pub', 'cave'),
        'effect': 'shield', 'duration': CLOVER_TIME,}}

# settings.12 — Reserved tuning values retained for compatibility; unused by the current game loop.
ITEM_INTERVAL = (10.0, 15.0)
MAGNET_SECONDS = 6.0
# Reserved horizontal radius, vertical radius and forward offset (px).
MAGNET_RX, MAGNET_RY, MAGNET_OFFSET = 180, 110, 45
REVIVE_COSTS = (50, 100)                                    # Reserved prices for the first and second revives, in coins.
POT_TIME = 7.0
PAIR_DISTANCE = 800                                         # Older pair threshold (m). The active cap uses TWO_OBSTACLES_DISTANCE.
MIN_REACTION_SECONDS = 0.80
BARREL_BOUNCES = (220, 480)
LAUNCHER_EVERY = 6                                          # Reserved obstacle count. The current spawn rules draw launchers randomly.
LAUNCHER_BY_WORLD = {'pub': 'cannon',
                      'cave': 'flame'}

# settings.13 — Roue de la fortune (affichée juste avant le Game Over).
WHEEL_GOLD_VISITS_REQUIRED = 1                       # Passages en cité d'or (par partie) pour débloquer la roue.
WHEEL_FILE = ASSETS / 'wheel' / 'wheel.png'           # Images à copier dans assets/wheel/ (renommées sans accents).
WHEEL_POINTER_FILE = ASSETS / 'wheel' / 'arrow.png'
WHEEL_DIAMETER = 400                                 # Diamètre de la roue à l'écran (px).
WHEEL_JACKPOT_COINS = 300                            # Pièces gagnées avec le jackpot (en plus du revive).

# ORDRE = celui de l'image, dans le sens horaire en partant du haut. Ne pas le changer.
# weight = poids de tirage ; la probabilité d'un segment est weight / somme des poids (ici 100).
WHEEL_SEGMENTS = [
    {'label': '+50',     'kind': 'coins',   'value': 50,  'weight': 20},
    {'label': '+1 Luck', 'kind': 'luck',    'value': 1,   'weight': 12},
    {'label': '+100',    'kind': 'coins',   'value': 100, 'weight': 10},
    {'label': 'Jackpot', 'kind': 'jackpot', 'value': WHEEL_JACKPOT_COINS, 'weight': 2},
    {'label': 'Revive',  'kind': 'revive',  'value': 0,   'weight': 8},
    {'label': '+25',     'kind': 'coins',   'value': 25,  'weight': 25},
    {'label': '+1 Luck', 'kind': 'luck',    'value': 1,   'weight': 12},
    {'label': '+75',     'kind': 'coins',   'value': 75,  'weight': 11},
]

def clamp(number, minimum, maximum):
    """Return the nearest bound when the number lies outside the interval."""
    return max(minimum, min(maximum, number))