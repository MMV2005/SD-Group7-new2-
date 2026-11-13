# reglages_personnages.1 : Préparation de la physique (pixel/seconde).
GRAVITY = 1400              # Gravité (Chute lorsque l'on relâche Espace) (pixel/seconde²).
THRUST = 1200               # Poussée (lorsque l'on maintien Espace enfoncé) (pixel/seconde²).
MAX_RISE = -510             # Vitesse maximale de montée (nombre négatif)(pixel/seconde).
MAX_FALL = 520              # Vitesse maximale de chute (pixel/seconde).

# reglages_personnages.2 : Animation : 3 poses, jouees dans l'ordre 0, 1, 2, 1.
ANIMATION_FPS = 9           # Nombre d'images par seconde pour l'animation du personnage (FPS).

# reglages_personnage.3 : Jet decoratif : ces pieces ne sont ni gagnées, ni depensées.
JET_RATE = 145              # Nombre de particules par seconde à pleine puissance.
JET_MAX = 110               # Limite de particules à l'écran (pour garder le jeu fluide).
JET_SPEED = (250, 490)      # Projection vers l'arriere.
JET_SPREAD = (-50, 170)     # Dispersion verticale des particules (surtout vers le bas).
JET_LIFE = (0.35, 0.65)     # Durée de vie de chaque pièce (secondes).
JET_GRAVITY = 500           # Gravité appliquée aux pièces.

# reglages_personnages.4 : Effets visuels 
GOOSE_FPS = 6               # Images par seconde ; deux poses par oie.
MAGNET_GLOW_COLOR = (255, 4, 4) # Couleur du halo de l'aimant bonus (RGB).
BEER_GLOW_COLOR = (255, 208, 12) # Couleur du halo de la bière bonus (RGB).
GLOW_OPACITY = 190          # Alpha maximal du halo, entre 0 et 255.
