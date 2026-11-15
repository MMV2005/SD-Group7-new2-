"""Visuals - player 3-frame animation, loaded when Visuals() is created."""
import pygame, math, random
from settings import *
from reglages_personnages import *

PLAYER_FRAMES_FOLDER = ASSETS / 'Skins' / 'classic'

#--- fond ---
BACKGROUND_FILE = ASSETS / 'world' / 'bg_meadow.png'
BACKGROUND_HORIZON = 800 # y of the ground line in the SOURCE image (pixels).
GOOSE_FRAMES_FOLDER = ASSETS / 'goose'
ANIMATION_FPS = 9           # Nombre d'images par seconde pour l'animation du personnage (FPS).


class Visuals:
    def __init__(self):
        self.frames = [
            pygame.image.load(str(PLAYER_FRAMES_FOLDER / f'vol_{i}.png')).convert_alpha()
            for i in range(3)]
        
        self.masks = [pygame.mask.from_surface(frame) for frame in self.frames]

        #Image and mask of the pose currently displayed. They are refreshed
        # by update_pose(), which must be called once per game loop turn.
        self.image = self.frames[0]
        self.mask = self.masks[0]

        # --- fond, chargé une seule fois ---
        self.background = self.load_background()

        self.goose_frames = [
            pygame.image.load(str(GOOSE_FRAMES_FOLDER / f'goose_{i}.png')).convert_alpha()
            for i in range(2)]
        # Un seul masque fixe (les ailes qui battent ne modifient pas la hitbox)
        self.goose_mask = pygame.mask.from_surface(self.goose_frames[0])

        self.coins = []               # particules actuellement à l'écran
        self.jet_accumulator = 0.0    # reste fractionnaire : JET_RATE / FPS n'est pas entier

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

    def reset_jet(self):
        """Vide le jet : à appeler au début de chaque partie."""
        self.coins = []
        self.jet_accumulator = 0.0

    def update_jet(self, player_rect, thrusting):
        """Crée et fait avancer les pièces : à appeler une fois par image."""
        dt = 1 / FPS    # pas de temps fixe (FPS vient de settings)

        # Création : JET_RATE pièces par seconde, plafonnées à JET_MAX
        if thrusting:
            self.jet_accumulator += JET_RATE * dt
            while self.jet_accumulator >= 1 and len(self.coins) < JET_MAX:
                self.jet_accumulator -= 1
                life = random.uniform(*JET_LIFE)
                self.coins.append({
                    'x': player_rect.left + JET_OFFSET_X,
                    'y': player_rect.centery + player_rect.height * JET_OFFSET_Y,
                    'vx': -random.uniform(*JET_SPEED),    # projetée vers l'arrière
                    'vy': random.uniform(*JET_SPREAD),    # dispersion verticale
                    'life': life, 'initial': life,        # 'initial' sert au rétrécissement
                    'angle': random.uniform(0, math.tau), # phase de rotation aléatoire
                })
            if len(self.coins) >= JET_MAX:
                self.jet_accumulator = 0.0                # évite l'accumulation au plafond

        # Mise à jour physique : intégration d'Euler en secondes
        for c in self.coins:
            c['vy'] += JET_GRAVITY * dt
            c['x'] += c['vx'] * dt
            c['y'] += c['vy'] * dt
            c['angle'] += 24 * dt     # environ 0,4 rad par image à 60 FPS
            c['life'] -= dt

        # Suppression des pièces expirées ou arrivées au sol
        self.coins = [c for c in self.coins if c['life'] > 0 and c['y'] <= FLOOR]

    def draw_jet(self, screen):
        """Dessine les pièces du jet."""
        for c in self.coins:
            # Hauteur proportionnelle à la vie restante : la pièce rétrécit
            h = max(3, round(10 * c['life'] / c['initial']))
            # Largeur en |cos(angle)| : effet de pièce qui tourne sur elle-même
            w = max(2, round(h * abs(math.cos(c['angle']))))
            rect = (round(c['x']), round(c['y']), w, h)
            pygame.draw.ellipse(screen, COIN_FILL, rect)
            pygame.draw.ellipse(screen, COIN_EDGE, rect, 1)

    def draw_player(self, screen, player_rect):
        """Dessine le jet, puis la pose actuelle du joueur."""
        self.draw_jet(screen)                  # d'abord les pièces : elles passent derrière le sprite
        screen.blit(self.image, player_rect)
    
    #Visuals.14 
    def get_goose_rect(self, center_x, center_y): #Return a rect for a new goose centered on (center_x, center_y).
        return self.goose_frames[0].get_rect(center=(center_x, center_y))
    def draw_goose(self, screen, baddie): #Draw goose_0 or goose_1 depending on the goose's age (GOOSE_FPS = 6).
        index = int(baddie['age'] * GOOSE_FPS) % 2
        screen.blit(self.goose_frames[index], baddie['rect'])
