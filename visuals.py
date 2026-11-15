"""Visuals - player 3-frame animation, loaded when Visuals() is created."""
import pygame
from settings import *
from transitions import draw_fog   # AJOUT : nuage de fumée du portail
#from reglages_personnages import ANIMATION_FPS, FRAME_SEQUENCE
PLAYER_FRAMES_FOLDER = ASSETS / 'Skins' / 'classic'
ANIMATION_FPS = 9           # Nombre d'images par seconde pour l'animation du personnage (FPS).
FRAME_SEQUENCE = (0, 1, 2, 1)  # Order in which the 3 poses are played.

# --- AJOUT : fonds (un par monde) ---
BACKGROUND_FOLDER = ASSETS / 'world'
# y de la ligne du sol dans chaque image SOURCE (pixels), valeurs de l'ancien jeu.
BACKGROUND_HORIZONS = {'meadow': 800, 'pub': 830, 'cave': 805, 'gold': 755}

# --- AJOUT : portail ---
PORTAL_FILE = ASSETS / 'transition' / 'portal.png'
PORTAL_SIZE = (210, 425)              # taille du portail à l'écran (valeur de l'ancien jeu)

class Visuals:
    def __init__(self):
        # IMPORTANT: convert_alpha() needs the display to exist already,
        # so Visuals() must be created AFTER pygame.display.set_mode(...).

        # Load the 3 frames once at startup (never inside the game loop).
        # convert_alpha() keeps PNG transparency and speeds up drawing.
        self.frames = [
            pygame.image.load(str(PLAYER_FRAMES_FOLDER / f'vol_{i}.png')).convert_alpha()
            for i in range(3)
        ]
        # One pixel-perfect mask per frame: each pose has a slightly
        # different silhouette, so each needs its own collision mask.
        self.masks = [pygame.mask.from_surface(frame) for frame in self.frames]

        # Image and mask of the pose currently displayed. They are refreshed
        # by update_pose(), which must be called once per game loop turn.
        self.image = self.frames[0]
        self.mask = self.masks[0]

        # --- AJOUT : tous les fonds, chargés une seule fois ---
        self.backgrounds = {name: self.load_background(name) for name in BACKGROUND_HORIZONS}

        # --- AJOUT : image du portail, chargée une seule fois ---
        portal = pygame.image.load(str(PORTAL_FILE)).convert_alpha()
        portal = portal.subsurface(portal.get_bounding_rect(min_alpha=20))   # enlève les bords transparents
        self.portal_image = pygame.transform.scale(portal, PORTAL_SIZE)

    def get_rect(self):
        """Return a new rect of the player's size (same for the 3 poses)."""
        return self.frames[0].get_rect()

    def update_pose(self):
        """Choose the current pose from the elapsed time."""
        # get_ticks() = milliseconds since pygame.init(); /1000 -> seconds.
        elapsed_seconds = pygame.time.get_ticks() / 1000
        # elapsed_seconds * ANIMATION_FPS = number of animation steps so far.
        # int() keeps the whole part, so the pose only changes every
        # 1 / ANIMATION_FPS seconds.
        step = int(elapsed_seconds * ANIMATION_FPS)
        # The modulo makes the sequence loop forever and keeps the index
        # inside the list.
        index = FRAME_SEQUENCE[step % len(FRAME_SEQUENCE)]
        self.image = self.frames[index]
        self.mask = self.masks[index]

    def draw_player(self, screen, player_rect):
        """Draw the current pose at the position given by player_rect."""
        screen.blit(self.image, player_rect)

    # --- AJOUT : fonds ---
    @staticmethod
    def load_background(name):
        """Load bg_<name>.png once, then align its ground line on FLOOR."""
        source = pygame.image.load(str(BACKGROUND_FOLDER / f'bg_{name}.png')).convert()
        horizon = BACKGROUND_HORIZONS[name]
        w, h = source.get_size()

        # Cut the source in two at the horizon: landscape above, soil below.
        top = source.subsurface((0, 0, w, horizon))
        bottom = source.subsurface((0, horizon, w, h - horizon))

        # Stretch each part so the horizon lands exactly on FLOOR.
        background = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))
        background.blit(pygame.transform.scale(top, (WINDOWWIDTH, FLOOR)), (0, 0))
        background.blit(pygame.transform.scale(bottom, (WINDOWWIDTH, WINDOWHEIGHT - FLOOR)), (0, FLOOR))
        return background

    def draw_background(self, screen, world='meadow'):
        """Draw the background of the given world. Call it BEFORE anything else each frame."""
        screen.blit(self.backgrounds[world], (0, 0))

    # --- AJOUT : portail ---
    def draw_portal(self, screen, portal_x):
        """Draw the fog cloud trailing the portal, then the portal itself."""
        draw_fog(screen, portal_x - 20)
        screen.blit(self.portal_image, self.portal_image.get_rect(center=(round(portal_x + 26), 282)))