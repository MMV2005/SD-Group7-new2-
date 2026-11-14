"""Visuals - player 3-frame animation, loaded when Visuals() is created."""
import pygame
from settings import *
#from reglages_personnages import ANIMATION_FPS, FRAME_SEQUENCE
PLAYER_FRAMES_FOLDER = ASSETS / 'Skins' / 'classic'
ANIMATION_FPS = 9           # Nombre d'images par seconde pour l'animation du personnage (FPS).
FRAME_SEQUENCE = (0, 1, 2, 1)  # Order in which the 3 poses are played.

class Visuals:
    #visuals.3
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