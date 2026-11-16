"""Obstacles : mouvements, animation et collisions par masque."""
import math
import random
import pygame

from settings import (
    WINDOWWIDTH, CEILING, FLOOR,
    BARREL_GRAVITY, BARREL_BOUNCES,
    LAUNCHERS, JET_WARNING, JET_END, JET_HEIGHT,
    LASER_SCROLL_SPEED, LASER_TILE_GAP, MUG_SPIN_SPEED,
)
# entities.1 : Représenter tous les obstacles du jeu.
class Hazard:
    # Ressources partagées entre tous les obstacles.
    frames_by_kind = {}
    masks_by_kind = {}
    jet_images = {}

    # entities.2 : Recevoir les ressources chargées par Visuals.
    @classmethod
    def configure(cls, frames, masks, jets):
        cls.frames_by_kind = frames
        cls.masks_by_kind = masks
        cls.jet_images = jets

    # entities.3 : Créer un obstacle compatible avec worlds.py.
    def __init__(self, kind, y=280, shape='floor', variant=0):
        self.kind = kind
        self.shape = shape
        self.variant = variant

        # Choisir la clé correspondant à l’image.
        if kind == 'rock':
            key = f'rock_{shape}'
        elif kind == 'fence':
            key = f'fence_{variant}'
        else:
            key = kind

        self.frames = self.frames_by_kind[key]
        self.masks = self.masks_by_kind[key]

        self.image = self.frames[0]
        self.mask = self.masks[0]

        self.x = float(WINDOWWIDTH + 80)
        self.y = float(y)
        self.base_y = float(y)

        self.age = 0.0
        self.vy = 0.0
        self.finished = False
        self.spin = random.choice((-1, 1)) * MUG_SPIN_SPEED
        self.jet_tile = None

        # Paramètres particuliers des tonneaux.
        self.bounce_speed = random.choice(BARREL_BOUNCES)

        # État du jet des lanceurs.
        self.jet_surface = None
        self.jet_mask = None
        self.jet_rect = None

        # Obstacles placés sur le sol.
        if kind in ('barrel', 'fence'):
            self.y = FLOOR - self.image.get_height() / 2

        if kind == 'barrel':
            self.vy = -self.bounce_speed

        # Les chopes partent du bas et visent la hauteur base_y.
        if kind == 'mug':
            self.y = FLOOR - self.image.get_height() / 2

        # Rochers attachés au sol ou au plafond.
        if kind == 'rock':
            if shape == 'floor':
                self.y = FLOOR - self.image.get_height() / 2
            elif shape == 'ceiling':
                self.y = CEILING + self.image.get_height() / 2

        # Les lanceurs apparaissent directement à droite.
        if kind in ('cannon', 'flame'):
            self.x = WINDOWWIDTH - 75.0

        self.sync_rect()

    # entities.4 : Aligner le rectangle avec la position de l’obstacle.
    def sync_rect(self):
        if self.kind in ('cannon', 'flame'):
            anchor = LAUNCHERS[self.kind][1]
            mouth_x, mouth_y = self.muzzle

            self.rect = self.image.get_rect(
                topleft=(
                    round(mouth_x - self.image.get_width() * anchor[0]),
                    round(mouth_y - self.image.get_height() * anchor[1]),
                )
            )
        else:
            self.rect = self.image.get_rect(
                center=(round(self.x), round(self.y))
            )

    # entities.5 : Donner la position de la bouche du lanceur.
    @property
    def muzzle(self):
        return round(self.x - 50), round(self.y)

    # entities.6 : Indiquer si le jet est actuellement dangereux.
    @property
    def firing(self):
        return (
            self.kind in ('cannon', 'flame')
            and JET_WARNING <= self.age < JET_END
        )
    
    # entities.7 : Préparer le jet après le choix définitif de la hauteur.
    def prepare_jet(self):
        """Redimensionner un motif à hauteur fixe, sans modifier ses proportions."""
        source = self.jet_images[self.kind]
        bounds = source.get_bounding_rect(min_alpha=20)
        if bounds.width and bounds.height:
            source = source.subsurface(bounds)
        tile_width = max(1, round(source.get_width() * JET_HEIGHT / source.get_height()))
        self.jet_tile = pygame.transform.scale(source, (tile_width, JET_HEIGHT))
        mouth_x, mouth_y = self.muzzle
        self.jet_surface = pygame.Surface((max(1, mouth_x), JET_HEIGHT), pygame.SRCALPHA)
        self.jet_rect = self.jet_surface.get_rect(midright=(mouth_x, mouth_y))
        self.refresh_jet()

    def refresh_jet(self):
        """Répéter le motif en le faisant défiler ; le masque suit les pixels dessinés."""
        self.jet_surface.fill((0, 0, 0, 0))
        step = self.jet_tile.get_width() + max(0, LASER_TILE_GAP)
        phase = int(max(0.0, self.age - JET_WARNING) * LASER_SCROLL_SPEED) % step
        for x in range(-phase, self.jet_surface.get_width(), step):
            self.jet_surface.blit(self.jet_tile, (x, 0))
        self.jet_mask = pygame.mask.from_surface(self.jet_surface)

    # entities.8 : Faire évoluer les mouvements et les animations.
    def update(self, dt, speed, player_rect):
        first_update = self.age == 0.0

        # Initialisation particulière au premier déplacement.
        if first_update:
            if self.kind in ('cannon', 'flame'):
                self.prepare_jet()

            elif self.kind == 'mug':
                # Durée estimée pour rejoindre la position horizontale du joueur.
                travel = (self.x - player_rect.centerx) / max(speed, 1.0)
                travel = max(travel, 0.1)

                # y_final = y_initial + vy*t + 0.5*g*t².
                self.vy = (
                    self.base_y - self.y - 0.5 * 100 * travel ** 2
                ) / travel

        self.age += dt

        # Les lanceurs restent fixes pendant l’avertissement et le tir.
        if self.kind in ('cannon', 'flame'):
            if self.firing:
                self.refresh_jet()
            self.finished = self.age >= JET_END
            self.sync_rect()
            return

        # Déplacement commun des autres obstacles.
        self.x -= speed * dt

        if self.kind == 'barrel':
            self.vy += BARREL_GRAVITY * dt
            self.y += self.vy * dt

            ground_y = FLOOR - self.image.get_height() / 2

            if self.y >= ground_y:
                self.y = ground_y
                self.vy = -self.bounce_speed

        elif self.kind == 'red_goose':
            # L’oie arrête de poursuivre après avoir dépassé le joueur.
            if self.x > player_rect.centerx:
                difference = player_rect.centery - self.y
                maximum_move = 70 * dt

                self.y += max(
                    -maximum_move,
                    min(maximum_move, difference)
                )

                half_height = self.image.get_height() / 2
                self.y = max(
                    CEILING + half_height,
                    min(FLOOR - half_height, self.y)
                )

        elif self.kind == 'bat':
            self.y = self.base_y + 32 * math.sin(self.age * 3.5)

        elif self.kind == 'mug':
            self.vy += 100 * dt
            self.y += self.vy * dt

        # Sélectionner ensemble l’image et son masque.
        animation_fps = 8 if self.kind == 'bat' else 6
        index = int(self.age * animation_fps) % len(self.frames)

        self.image = self.frames[index]
        self.mask = self.masks[index]
        if self.kind == 'mug':
            # Toujours repartir de l'image source : aucune dégradation cumulée.
            self.image = pygame.transform.rotate(self.frames[index], self.age * self.spin)
            self.mask = pygame.mask.from_surface(self.image)

        self.sync_rect()

    # entities.9 : Vérifier le contact avec le masque du personnage.
    def collides_with(self, player_rect, player_mask):
        if self.kind in ('cannon', 'flame'):
            # Seul le jet actif provoque une collision.
            if not self.firing or self.jet_mask is None:
                return False

            obstacle_rect = self.jet_rect
            obstacle_mask = self.jet_mask
        else:
            obstacle_rect = self.rect
            obstacle_mask = self.mask

        # Écarter les objets dont les rectangles ne se touchent pas.
        if not player_rect.colliderect(obstacle_rect):
            return False

        offset = (
            obstacle_rect.left - player_rect.left,
            obstacle_rect.top - player_rect.top
        )

        return player_mask.overlap(obstacle_mask, offset) is not None

    # entities.10 : Indiquer si l’obstacle doit être supprimé.
    def offscreen(self):
        if self.finished:
            return True

        if self.rect.right < 0:
            return True                        # Suppression de l’obstacle lorsque son bord droit est à gauche de l’écran.

        if self.kind == 'mug' and self.rect.top > FLOOR + 100:
            return True                        # Suppression de la chope lorsqu’elle est tombée bien en dessous du sol.

        return False

