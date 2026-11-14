"""Visuals - player 3-frame animation, loaded when Visuals() is created."""
import pygame
from settings import *
from reglages_personnages import ANIMATION_FPS,GOOSE_FPS
PLAYER_FRAMES_FOLDER = ASSETS / 'Skins' / 'classic'
ANIMATION_FPS = 9 # Nombre d'images par seconde pour l'animation du personnage (FPS).
FRAME_SEQUENCE = (0, 1, 2, 1) # Order in which the 3 poses are played.

#--- fond ---
BACKGROUND_FILE = ASSETS / 'world' / 'bg_meadow.png'
BACKGROUND_HORIZON = 800 # y of the ground line in the SOURCE image (pixels).
GOOSE_FRAMES_FOLDER = ASSETS / 'goose'
ANIMATION_FPS = 9           # Nombre d'images par seconde pour l'animation du personnage (FPS).
FRAME_SEQUENCE = (0, 1, 2, 1)  # Order in which the 3 poses are played.

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

        #Image and mask of the pose currently displayed. They are refreshed
        # by update_pose(), which must be called once per game loop turn.
        self.image = self.frames[0]
        self.mask = self.masks[0]

        # --- fond, chargé une seule fois ---
        self.background = self.load_background()

        self.goose_frames = [
            pygame.image.load(str(GOOSE_FRAMES_FOLDER / f'goose_{i}.png')).convert_alpha()
            for i in range(2)
        ]
        # Un seul masque fixe (les ailes qui battent ne modifient pas la hitbox)
        self.goose_mask = pygame.mask.from_surface(self.goose_frames[0])
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

    
    @staticmethod
    def load_background():
        """Load the image once, then align its ground line on FLOOR."""
        source = pygame.image.load(str(BACKGROUND_FILE)).convert()
        w, h = source.get_size()

        # Cut the source in two at the horizon: landscape above, soil below.
        top = source.subsurface((0, 0, w, BACKGROUND_HORIZON))
        bottom = source.subsurface((0, BACKGROUND_HORIZON, w, h - BACKGROUND_HORIZON))

        # Stretch each part so the horizon lands exactly on FLOOR.
        background = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))
        background.blit(pygame.transform.scale(top, (WINDOWWIDTH, FLOOR)), (0, 0))
        background.blit(pygame.transform.scale(bottom, (WINDOWWIDTH, WINDOWHEIGHT - FLOOR)), (0, FLOOR))
        return background

    def draw_background(self, screen):
        """Draw the background. Must be called BEFORE anything else each frame."""
        screen.blit(self.background, (0, 0))

    # visuals.12 : Dessine jet de pièces.
    def player(self, screen, player, time, skin='classic'):
        self.effect_glow(screen, player, time)
        # Beaucoup de petites pieces projetees, plus denses pres de la sortie.
        for x, y, vx, vy, life, initial, angle in player.particles:
            height = max(3, round(10 * life / initial))
            width = max(2, round(height * abs(math.cos(angle))))
            pygame.draw.ellipse(screen, (242, 171, 24), (round(x), round(y), width, height))
            pygame.draw.ellipse(screen, GOLD, (round(x), round(y), width, height), 1)
            if width > 4:
                pygame.draw.line(screen, WHITE, (round(x + 2), round(y + 2)), (round(x + 2), round(y + height - 2)))
    def draw_player(self, screen, player_rect): #Draw the current pose at the position given by player_rect.
        screen.blit(self.image, player_rect)
    #Visuals.14 
    def get_goose_rect(self, center_x, center_y): #Return a rect for a new goose centered on (center_x, center_y).
        return self.goose_frames[0].get_rect(center=(center_x, center_y))
    def draw_goose(self, screen, baddie): #Draw goose_0 or goose_1 depending on the goose's age (GOOSE_FPS = 6).
        index = int(baddie['age'] * GOOSE_FPS) % 2
        screen.blit(self.goose_frames[index], baddie['rect'])
