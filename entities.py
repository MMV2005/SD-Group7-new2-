# coins.py
import math
import random
import pygame

# Everything below already exists in settings.py
from settings import (WINDOWWIDTH, WINDOWHEIGHT, CEILING, FLOOR, FPS,
                      COIN_INTERVAL, COINS_PER_GROUP, ASSETS)


class CoinSpawner:
    """Spawns rows of coins from the right side, handles pickup and drawing."""

    # Only values that are NOT in settings.py
    RADIUS = 14          # half the size of a coin, in pixels (sprite and hitbox)
    SPACING = 43         # horizontal gap between two coins in a row (px)
    AMPLITUDE = 24       # vertical amplitude of the wave (px)

    def __init__(self):
        self.coins = []                  # list of {'rect': pygame.Rect}, same logic as baddies
        self.timer = FPS                 # frames before the first row (1 second)

        # Load the sprite once. ASSETS comes from settings.py, so the path
        # works whatever the folder the game is launched from.
        image = pygame.image.load(ASSETS / 'bonus' / 'gold_coin.png').convert_alpha()
        # Resize the sprite to the size of the hitbox
        self.image = pygame.transform.smoothscale(image, (2 * self.RADIUS, 2 * self.RADIUS))

    def reset(self):
        """Call at the start of each game."""
        self.coins.clear()
        self.timer = FPS

    def _zone_is_free(self, baddies):
        """True if no goose is in the spawn area on the right of the screen."""
        row_width = COINS_PER_GROUP * self.SPACING + 100
        zone = pygame.Rect(WINDOWWIDTH, 0, row_width, WINDOWHEIGHT)
        return not any(zone.colliderect(b['rect']) for b in baddies)

    def _spawn_row(self):
        """Creates a wavy row of coins just outside the screen, on the right."""
        # Keep the whole row (wave included) between the ceiling and the floor
        margin = self.AMPLITUDE + self.RADIUS
        y = random.randint(CEILING + margin, FLOOR - margin)

        for i in range(COINS_PER_GROUP):
            x = WINDOWWIDTH + 30 + i * self.SPACING       # off-screen, shifted for each coin
            wave = self.AMPLITUDE * math.sin(i * 0.7)     # sinusoidal wave
            rect = pygame.Rect(0, 0, 2 * self.RADIUS, 2 * self.RADIUS)
            rect.center = (x, int(y + wave))
            self.coins.append({'rect': rect})

    def update(self, player_rect, speed, baddies):
        """
        Advances one frame: spawn, move, pickup, cleanup.
        `speed` is in px/frame, the same as the geese.
        Returns the number of coins collected during this frame.
        """
        # --- Spawn ---
        self.timer -= 1
        if self.timer <= 0:
            if self._zone_is_free(baddies):
                self._spawn_row()
                # COIN_INTERVAL is in seconds in settings.py, so convert it to frames
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