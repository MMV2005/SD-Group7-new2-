# settings.1 : Préparation du module.
from pathlib import Path
from reglages_personnages import GRAVITY, THRUST, MAX_RISE, MAX_FALL

# settings.2 : Fenetre et limites jouables.
WIDTH, HEIGHT, FPS = 960, 540, 60           # Taille de la fenetre (largeur et hauteur en pixels) et nombre d'images par seconde (FPS).
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
SPEED_PER_METRE = 0.045                    # +45 pixels/seconde tous les 1000 metres
METRES_PER_PIXEL = 0.1                     # Conversion de pixels à metres (1 pixel = 0.1 metre)

# settings.4 : Mondes et transitions.
PORTAL_MIN, PORTAL_MAX = 1000, 1400        # Distance minimale et maximale entre deux portails (en metres).
TRANSITION_SECONDS = 1.6                   # Durée de la transition entre deux mondes (en secondes).
SAFE_SECONDS = 1.5                         # Durée de la zone de sécurité après un portail (en secondes).
GOLD_SECONDS = 10.0                        # Durée de la zone de bonus dans le monde cité d'or (en secondes).

# settings.5 : Recompenses et objets.
COIN_INTERVAL = (3.4, 4.8)                 # Délai aléatoire entre deux groupes de pièces (en secondes).
COINS_PER_GROUP = 5                        # Nombre de pièces par groupe.
ITEM_INTERVAL = (10.0, 15.0)               # Délai aléatoire entre deux objets (en secondes).
MAGNET_SECONDS = 6.0                       # Durée d'activation du aimant (en secondes).
MAGNET_RX, MAGNET_RY, MAGNET_OFFSET = 180, 110, 45  # Rayons horizontal et vertical de l’aimant, puis décalage vers l’avant, en pixels.
GUINNESS_TIME = 6.0                        # Durée d'activation de la bière (en secondes).
REVIVE_COSTS = (30, 60)                    # Coût de la réanimation (en pièces d'or) : 1ère et 2ème réanimation.
CLOVER_TIME = 5.0                          # Durée d'activation du trèfle (en secondes).
POT_TIME = 7.0                             # Durée d'activation de la marmite (en secondes).


# settings.6 : Dessin des lanceurs : taille et bouche mesuree dans chaque sprite.
LAUNCHERS = {'cannon': ((138, 84), (0.09, 0.53)),
             'flame': ((152, 128), (0.24, 0.59))}     # Définition des lanceurs : (largeur, hauteur), (position relative de la bouche depuis le coin haut gauche).
JET_WARNING, JET_END = 1.5, 2.5                       # Durée de l'avertissement et de la fin du jet (en secondes).
JET_HEIGHT = 24                                       # Hauteur du jet (en pixels).

# settings.7 : Borne une valeur entre deux limites.
def clamp(number, minimum, maximum):
    """Limite un nombre a l'intervalle choisi."""
    return max(minimum, min(maximum, number))

# settings.8 : Difficulté : fréquence et espace entre obstacles
OBSTACLE_INTERVAL_START = 1.6                       # Délai initial entre deux obstacles (en secondes). Ce délai diminue progressivement jusqu'à OBSTACLE_INTERVAL_MIN.
OBSTACLE_INTERVAL_MIN = 0.65                        # Délai minimal entre deux obstacles (en secondes). Ce délai est atteint lorsque la vitesse du jeu est maximale.
PAIR_DISTANCE = 800                                 # Distance minimal avant d'autoriser les paires d'obstacles (en mètres).
MIN_REACTION_SECONDS = 0.85                         # Temps minimal de réaction entre obstacles (en secondes). 
FENCE_SIZES = ((112, 72), (208, 72), (112, 112), (208, 112))        # Différentes tailles de barrière (largeur, hauteur) en pixels. Ces dimensions sont utilisées pour calculer les collisions avec le personnage.
BARREL_GRAVITY = 950                                # Gravité appliquée aux tonneaux (en pixels/seconde²).
BARREL_BOUNCES = (220, 340)                         # Vitesse initiale verticale de chaque rebond.

# settings.9 : Régler la présence des lanceurs dans chaque monde.
LAUNCHER_EVERY = 6                                  # Réserver un lanceur après ce nombre d'obstacles ordinaires.
LAUNCHER_MIN_DISTANCE = {'pub': 0,  'cave': 0}      # Distance minimale (en mètres) d'apparition d'un lanceurpour chaque monde. 
LAUNCHER_BY_WORLD = {'pub': 'cannon',
                      'cave': 'flame'}              # Type de lanceur pour chaque monde. Le type de lanceur doit correspondre à une clé du dictionnaire LAUNCHERS.

# settings.10 : Régler la densité progressive des obstacles.
TWO_OBSTACLES_DISTANCE = 600                        # Jusqu'à 2 obstacles maximum dès 600 m.
THREE_OBSTACLES_DISTANCE = 1800                     # Jusqu'à 3 obstacles maximumdès 1800 m.

DENSITY_MAX_DISTANCE = 3500                         # Densité maximum des objets atteint à 3500 m (difficulté max).

OBSTACLE_GAP_MIN = 280                              # Distance minimale entre centres des objets, en pixels.
OBSTACLE_GAP_SECONDS = 0.65                         # Distance minimale lié à la vitesse cette fois (en secondes, quand le jeu va plus vite).

# settings.11 : Autoriser les combinaisons de lanceurs.
LAUNCHER_MIX_DISTANCE = 7000                        # Distance minimale pour autoriser les combinaisons de lanceurs (en mètres).
MAX_LAUNCHERS = 2                                   # Nombre maximum de lanceurs autorisés dans une combinaison.
LAUNCHER_VERTICAL_GAP = 150                         # Écart minimal entre deux axes de tir.

MEADOW_HEIGHTS = (130, 130, 200, 285, 365)          # Hauteur des obstacles dans le monde prairie par probabilité (40%, 20%, 20%, 20% respectivement). Repetition of 130 increases its probability of appearance.
PUB_HEIGHTS = (130, 130, 200, 285, 365)             # Hauteur des obstacles dans le monde pub par probabilité (répéter 130 augmente la probabilité d'apparition : 20% ici, et pour (130, 130, 200, 285, 365) : 40%, 20%, 20%, 20% respectivement)
