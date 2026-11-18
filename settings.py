# settings.1 : Préparation du module.
from pathlib import Path
from reglages_personnages import *

# settings.2 : Fenetre et limites jouables.
WINDOWWIDTH, WINDOWHEIGHT, FPS = 960, 540, 60           # Taille de la fenetre (largeur et hauteur en pixels) et nombre d'images par seconde (FPS).
WIDTH, HEIGHT = WINDOWWIDTH, WINDOWHEIGHT
CEILING, FLOOR = 90, 475                    # Limites jouables (en pixels) : plafond et sol. Le personnage ne peut pas depasser ces limites.
ROOT = Path(__file__).resolve().parent      # Trouver le dossier contenant ce fichier Python.
                                        #__file__ : contient le chemin du fichier Python dans lequel cette ligne est écrite. Ici, elle désigne settings.py.
                                        #Path(__file__) : transforme ce chemin en un objet Path, sur lequel on peut utiliser des opérations liées aux fichiers.
                                        #.resolve() : obtient le chemin absolu (c’est-à-dire le chemin complet depuis la racine du disque).
                                        #.parent : récupère le dossier contenant le fichier.
ASSETS = ROOT / 'assets'                    # Définir le chemin du dossier des ressources du jeu.
RECORD_FILE = ROOT / 'record.json'          # Définir le chemin du fichier utilisé pour sauvegarder le record.


# settings.3 : Paramètres de déplacements (augmentation de vitesse).
START_SPEED, MAX_SPEED = 300, 580          # Vitesse de départ et vitesse maximale (en pixels par seconde).
SPEED_PER_METER = 0.045                    # +45 pixels/seconde tous les 1000 metres
METERS_PER_PIXEL = 0.1                     # Conversion de pixels à metres (1 pixel = 0.1 metre)

# settings.4 : Mondes et transitions.
PORTAL_MIN, PORTAL_MAX = 600, 700          # Distance minimale et maximale entre deux portails (en metres).
TRANSITION_SECONDS = 1.6                   # Durée de la transition entre deux mondes (en secondes).
SAFE_SECONDS = 1.0                         # Durée de la zone de sécurité après un portail (en secondes).
GOLD_SECONDS = 10.0                        # Durée de la zone de bonus dans le monde cité d'or (en secondes).

# settings.5 : Recompenses et objets.
#coins 
COIN_INTERVAL = (3.4, 4.8)                 # Délai aléatoire entre deux groupes de pièces (en secondes).
COINS_PER_WAVE = 5                        # Nombre de pièces dans la vague.
RADIUS = 12          # half the size of a coin, in pixels (sprite and hitbox)
SPACING = 43         # horizontal gap between two coins in a wave (px)
WAVE_AMPLITUDE = 24       # vertical amplitude of the wave (px)
CIRCLE_R = 50        # radius of the circle of coins (px)
CIRCLE_N = 8        # number of coins in the circle
CROSS_UNIT = 36      # distance between the center coin and each arm coin for the cross shape (px)
ZIGZAG_AMPLITUDE = 15  # vertical amplitude of the zigzag (px)
COINS_PER_ZIGZAG = 7   # number of coins in the zigzag pattern


ITEM_INTERVAL = (10.0, 15.0)               # Délai aléatoire entre deux objets (en secondes).
MAGNET_SECONDS = 6.0                       # Durée d'activation du aimant (en secondes).
MAGNET_RX, MAGNET_RY, MAGNET_OFFSET = 180, 110, 45  # Rayons horizontal et vertical de l’aimant, puis décalage vers l’avant, en pixels.
GUINNESS_TIME = 6.0                        # Durée d'activation de la bière (en secondes).
REVIVE_COSTS = (50, 100)                    # Coût de la réanimation (en pièces d'or) : 1ère et 2ème réanimation.
CLOVER_TIME = 5.0                          # Durée d'activation du trèfle (en secondes).
POT_TIME = 7.0                             # Durée d'activation de la marmite (en secondes).


# settings.6 : Dessin des lanceurs : taille et bouche mesuree dans chaque sprite.
LAUNCHERS = {'cannon': ((210, 150), (0.09, 0.53)),
             'flame': ((220, 200), (0.24, 0.59))}     # Définition des lanceurs : (largeur, hauteur), (position relative de la bouche depuis le coin haut gauche).
JET_WARNING, JET_END = 1.5, 2.5                       # Durée de l'avertissement et de la fin du jet (en secondes).
JET_HEIGHT = 60                                       # Hauteur du jet (en pixels).

# settings.7 : Borne une valeur entre deux limites.
def clamp(number, minimum, maximum):
    """Limite un nombre a l'intervalle choisi."""
    return max(minimum, min(maximum, number))

# settings.8 : Difficulté : fréquence et espace entre obstacles
OBSTACLE_INTERVAL_START = 1.6                       # Délai initial entre deux obstacles (en secondes). Ce délai diminue progressivement jusqu'à OBSTACLE_INTERVAL_MIN.
OBSTACLE_INTERVAL_MIN = 0.60                        # Délai minimal entre deux obstacles (en secondes). Ce délai est atteint lorsque la vitesse du jeu est maximale.
PAIR_DISTANCE = 800                                 # Distance minimal avant d'autoriser les paires d'obstacles (en mètres).
MIN_REACTION_SECONDS = 0.80                         # Temps minimal de réaction entre obstacles (en secondes). 
FENCE_SIZES = ((112, 72), (208, 72), (112, 112), (208, 112))        # Différentes tailles de barrière (largeur, hauteur) en pixels. Ces dimensions sont utilisées pour calculer les collisions avec le personnage.
BARREL_GRAVITY = 800                                # Gravité appliquée aux tonneaux (en pixels/seconde²).
BARREL_BOUNCES = (220, 480)                         # Vitesse initiale verticale de chaque rebond.

# settings.9 : Régler la présence des lanceurs dans chaque monde.
LAUNCHER_EVERY = 6                                  # Réserver un lanceur après ce nombre d'obstacles ordinaires.
LAUNCHER_MIN_DISTANCE = {'pub': 0,  'cave': 0}      # Distance minimale (en mètres) d'apparition d'un lanceurpour chaque monde. 
LAUNCHER_BY_WORLD = {'pub': 'cannon',
                      'cave': 'flame'}              # Type de lanceur pour chaque monde. Le type de lanceur doit correspondre à une clé du dictionnaire LAUNCHERS.

# settings.10 : Régler la densité progressive des obstacles.
TWO_OBSTACLES_DISTANCE = 2000                       # Jusqu'à 2 obstacles maximum dès 2000 m.
THREE_OBSTACLES_DISTANCE = 3500                     # Jusqu'à 3 obstacles maximum dès 3500 m.

DENSITY_MAX_DISTANCE = 3500                        # Densité maximum des objets atteint à 3500 m (difficulté max).

OBSTACLE_GAP_MIN = 260                              # Distance minimale entre centres des objets, en pixels.
OBSTACLE_GAP_SECONDS = 0.60                         # Distance minimale lié à la vitesse cette fois (en secondes, quand le jeu va plus vite).

# settings.11 : Autoriser les combinaisons de lanceurs.
LAUNCHER_MIX_DISTANCE = 7000                        # Distance minimale pour autoriser les combinaisons de lanceurs (en mètres).
MAX_LAUNCHERS = 2                                   # Nombre maximum de lanceurs autorisés dans une combinaison.
LAUNCHER_VERTICAL_GAP = 150                         # Écart minimal entre deux axes de tir.

MEADOW_HEIGHTS = (130, 130, 175, 200, 285, 285, 365, 385)          # Hauteur des obstacles dans le monde prairie par probabilité . Repetition of 130 increases its probability of appearance.
PUB_HEIGHTS = (130, 130, 130, 165, 200, 240, 285, 285, 365, 375)                        # Hauteur des obstacles dans le monde pub par probabilité (répéter 130 augmente la probabilité d'apparition.

TEXTCOLOR = (255, 255, 255)
# settings.12 : Défilement des motifs de laser et rotation des chopes.
LASER_SCROLL_SPEED = 500.0   # Pixels/seconde, vers la gauche.
LASER_TILE_GAP = 0         # 0 : motifs contigus ; > 0 : espaces transparents.
MUG_SPIN_SPEED = 210.0      # Degrés/seconde (0 pour désactiver la rotation).

# settings.13 : Chaudrons et cité d'or.
POT_REQUIRED = 3
POT_FILE = ASSETS / 'bonus' / 'pot_of_gold.png'
POT_SIZE = (52, 52)
POT_SPAWN_INTERVAL = (12.0, 14.0)
GOLD_SPEED = 360.0
GOLD_COIN_INTERVAL = (0.7, 1.0)

# settings.14 : Tonneaux et fin du tir des lanceurs.
BARREL_SPEED_RANGE = (0.85, 1.25)  # Multiplicateur de la vitesse du monde.
BARREL_JUMP_RANGE = (220.0, 500.0) # Impulsion verticale, pixels/seconde.
LAUNCHER_HOLD_SECONDS = 0.6       # Reste visible après la fin du tir.
LAUNCHER_FADE_SECONDS = 0.35      # Disparaît progressivement ensuite.

# settings.15 : Boîtes maximales communes ; proportions toujours conservées.
OBSTACLE_SIZES = {
    'goose': (100, 90), 'red_goose': (100, 90), 'bat': (85, 60),
    'barrel': (80, 72), 'mug': (44, 48),
    'rock_floor': (88, 143), 'rock_ceiling': (88, 143),
    'rock_horizontal': (160, 60), 'rock_vertical': (52, 138),
    'rock_diagonal': (145, 132),
    'cannon': LAUNCHERS['cannon'][0], 'flame': LAUNCHERS['flame'][0],
    **{f'fence_{i}': size for i, size in enumerate(FENCE_SIZES)},
}

# settings.16 : Définition des objets. Seuls les objets enabled=True sont chargés.
# Les effets temporaires se renouvellent à chaque collecte, sans cumul de puissance.
BONUS_DEFINITIONS = {
    'pot': {
        'enabled': True, 'file': POT_FILE, 'size': POT_SIZE,
        'interval': POT_SPAWN_INTERVAL, 'worlds': ('meadow', 'pub', 'cave'),
        'effect': 'count', 'limit': POT_REQUIRED,
    },
    # Exemples prêts à activer après définition/validation des règles et des images.
    'beer': {
        'enabled': True, 'file': ASSETS / 'bonus' / 'beer_mug.png',
        'size': (44, 48), 'interval': (12.0, 18.0),
        'worlds': ('pub'),
        'effect': 'coin_multiplier', 'duration': GUINNESS_TIME, 'value': 2,
    },
    'clover': {
        'enabled': True, 'file': ASSETS / 'bonus' / 'clover.png',
        'size': (44, 44), 'interval': (15.0, 22.0),
        'worlds': ('meadow', 'pub', 'cave'),
        'effect': 'shield', 'duration': CLOVER_TIME,
    },
}