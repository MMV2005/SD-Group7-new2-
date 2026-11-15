import math
import random
import pygame
from settings import *


class CoinSpawner:
    """Spawns patterns of coins from the right side, handles pickup and drawing."""
    PATTERNS = ('wave', 'circle')

    def __init__(self):
        self.coins = []                  # list of {'rect': pygame.Rect}
        self.timer = FPS                 # frames before the first pattern (1 second)
        self.next_kind = random.choice(self.PATTERNS)   # pattern that will spawn next

        # Load the sprite once (PNG with transparent background)
        image = pygame.image.load(ASSETS / 'bonus' / 'gold_coin.png').convert_alpha()
        # Resize the sprite to the size of the hitbox
        self.image = pygame.transform.smoothscale(
            image, (2 * RADIUS, 2 * RADIUS))

    def reset(self):
        """Call at the start of each game."""
        self.coins.clear()
        self.timer = FPS
        self.next_kind = random.choice(self.PATTERNS)

    def _width(self, kind):
        """Horizontal size of a pattern in pixels (used to check the spawn area)."""
        if kind == 'circle':
            return 2 * CIRCLE_R + 2 * RADIUS
        return COINS_PER_WAVE * SPACING

    def _zone_is_free(self, baddies, kind):
        """True if no goose is in the spawn area, sized for the chosen pattern."""
        zone = pygame.Rect(WINDOWWIDTH, 0, self._width(kind) + 100, WINDOWHEIGHT)
        return not any(zone.colliderect(b['rect']) for b in baddies)

    def _add_coin(self, x, y):
        """Creates one coin centered on (x, y)."""
        rect = pygame.Rect(0, 0, 2 * RADIUS, 2 * RADIUS)
        rect.center = (int(x), int(y))
        self.coins.append({'rect': rect})

    def _spawn_wave(self):
        """Wavy row of coins, just outside the screen on the right."""
        # Keep the whole row (wave included) between the ceiling and the floor
        margin = AMPLITUDE + RADIUS
        y = random.randint(CEILING + margin, FLOOR - margin)

        for i in range(COINS_PER_WAVE):
            x = WINDOWWIDTH + 30 + i * SPACING
            wave = AMPLITUDE * math.sin(i * 0.7)
            self._add_coin(x, y + wave)

    def _spawn_circle(self):
        """Circle of coins, entirely outside the screen when it is created."""
        # Center: the left edge of the circle starts 30 px after the right border
        cx = WINDOWWIDTH + 30 + CIRCLE_R + RADIUS
        # Keep the whole circle between the ceiling and the floor
        margin = CIRCLE_R + RADIUS
        cy = random.randint(CEILING + margin, FLOOR - margin)

        for k in range(CIRCLE_N):
            angle = 2 * math.pi * k / CIRCLE_N     # angle of coin k (radians)
            x = cx + CIRCLE_R * math.cos(angle)
            y = cy + CIRCLE_R * math.sin(angle)
            self._add_coin(x, y)

    def _spawn(self, kind):
        """Calls the right generator for the chosen pattern."""
        if kind == 'circle':
            self._spawn_circle()
        else:
            self._spawn_wave()

    def update(self, player_rect, speed, baddies):
        """
        Advances one frame: spawn, move, pickup, cleanup.
        `speed` is in px/frame, the same as the geese.
        Returns the number of coins collected during this frame.
        """
        # --- Spawn ---
        self.timer -= 1
        if self.timer <= 0:
            if self._zone_is_free(baddies, self.next_kind):
                self._spawn(self.next_kind)
                # Choose the next pattern now, so the zone check uses the right size
                self.next_kind = random.choice(self.PATTERNS)
                # COIN_INTERVAL is in seconds, convert it to frames
                self.timer = random.randint(int(COIN_INTERVAL[0] * FPS),
                                            int(COIN_INTERVAL[1] * FPS))
            else:
                self.timer = 10          # area occupied: try again in 10 frames

        # --- Move, pickup, leave the screen ---
        collected = 0
        for coin in self.coins[:]:
            coin['rect'].move_ip(-speed, 0)
            if coin['rect'].colliderect(player_rect):
                self.coins.remove(coin)
                collected += 1
            elif coin['rect'].right < 0:
                self.coins.remove(coin)
        return collected

    def draw(self, surface):
        """Draws each coin with the sprite."""
        for coin in self.coins:
            surface.blit(self.image, coin['rect'])