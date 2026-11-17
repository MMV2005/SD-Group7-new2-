"""Objets collectables ; leurs effets sont appliqués par le main."""

from collections import deque
import random
import pygame

from settings import (WINDOWWIDTH, CEILING, FLOOR, POT_FILE, POT_SIZE, POT_REQUIRED, POT_SPAWN_INTERVAL,)


# bonus.1 : Décrire les bonus disponibles.
BONUS_TYPES = {'pot': {'file': POT_FILE, 'size': POT_SIZE,}}


def remove_black_background(image):
    """Make the edge-connected black background of the pot image transparent."""
    width, height = image.get_size()
    pixels = deque(
        [(x, y) for x in range(width) for y in (0, height - 1)]
        + [(x, y) for y in range(height) for x in (0, width - 1)]
    )
    visited = set()

    while pixels:
        x, y = pixels.popleft()
        if not (0 <= x < width and 0 <= y < height) or (x, y) in visited:
            continue
        visited.add((x, y))

        red, green, blue, alpha = image.get_at((x, y))
        if alpha == 0 or max(red, green, blue) <= 18:
            image.set_at((x, y), (red, green, blue, 0))
            pixels.extend(((x - 1, y), (x + 1, y),
                           (x, y - 1), (x, y + 1)))

    return image


class BonusSpawner:

    # bonus.2 : Charger chaque image une seule fois.
    def __init__(self):
        self.images = {}
        self.masks = {}

        for kind, config in BONUS_TYPES.items():
            image = pygame.image.load(
                str(config['file'])).convert_alpha()

            if config['file'].suffix.lower() in ('.jpg', '.jpeg'):
                image = pygame.transform.smoothscale(
                    image, (config['size'][0] * 2, config['size'][1] * 2)
                )
                image = remove_black_background(image)

            # Enlever les marges transparentes.
            bounds = image.get_bounding_rect(min_alpha=20)

            if not bounds.width or not bounds.height:
                raise ValueError(f"Image de bonus vide : {config['file']}")

            image = image.subsurface(bounds).copy()

            # Garder les proportions de l'image.
            ratio = min(config['size'][0] / image.get_width(), config['size'][1] / image.get_height())

            size = (max(1, round(image.get_width() * ratio)), max(1, round(image.get_height() * ratio)))

            self.images[kind] = pygame.transform.scale(image, size)

            self.masks[kind] = pygame.mask.from_surface(self.images[kind])

        self.reset()

    # bonus.3 : Réinitialiser les objets et les chaudrons acquis.
    def reset(self):
        self.pots = 0
        self.clear()

    # bonus.4 : Retirer les objets sans perdre les chaudrons acquis.
    def clear(self):
        self.items = []
        self.timer = random.uniform(*POT_SPAWN_INTERVAL)

    @property
    def ready(self):
        """True lorsque suffisamment de chaudrons sont acquis."""
        return self.pots >= POT_REQUIRED

    # bonus.5 : Faire apparaître, déplacer et ramasser les objets.
    def update(self, player_rect, player_mask, speed, hazards, dt, blocked=False):
        if not blocked:
            self.timer = max(0.0, self.timer - dt)

            # Attendre un passage sans obstacle.
            if self.timer <= 0 and not self.items and not hazards:
                kind = 'pot'
                image = self.images[kind]

                margin = image.get_height() // 2 + 12

                y = random.randint(CEILING + margin, FLOOR - margin)

                rect = image.get_rect(center=(WINDOWWIDTH + 50, y))

                self.items.append({'kind': kind, 'rect': rect, 'x': float(rect.centerx),})

                self.timer = random.uniform(*POT_SPAWN_INTERVAL)

        collected = []

        for item in self.items[:]:
            item['x'] -= speed * dt

            rect = item['rect']
            rect.centerx = round(item['x'])

            offset = (rect.x - player_rect.x, rect.y - player_rect.y)

            if (rect.colliderect(player_rect) and player_mask.overlap(self.masks[item['kind']], offset) is not None):
                collected.append(item['kind'])
                self.items.remove(item)

            elif rect.right < 0:
                self.items.remove(item)

        return collected

    # bonus.6 : Dessiner les objets encore présents.
    def draw(self, screen):
        for item in self.items:
            screen.blit(self.images[item['kind']], item['rect'])