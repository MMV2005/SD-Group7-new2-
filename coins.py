import math
import random
import pygame
from settings import *
from sprite_assets import load_image

class CoinSpawner:
    """Spawns patterns of coins from the right side, handles pickup and drawing."""
    PATTERNS = ('wave', 'circle', 'cross', 'zigzag')  # available patterns of coins

    def __init__(self):
        self.coins = []                  # list of {'rect': pygame.Rect}
        self.timer = FPS                 # frames before the first pattern (1 second)
        self.next_kind = random.choice(self.PATTERNS)   # pattern that will spawn next

        image = load_image(ASSETS / 'bonus' / 'gold_coin.png').convert_alpha() # Load the sprite once (PNG with transparent background)
        self.image = pygame.transform.smoothscale(image, (2 * RADIUS, 2 * RADIUS)) # Resize the sprite to the size of the hitbox

    def reset(self):
        """Call at the start of each game."""
        self.coins.clear()
        self.timer = FPS
        self.next_kind = random.choice(self.PATTERNS)

    def _width(self, kind):
        """Horizontal size of a pattern in pixels (used to check the spawn area)."""
        if kind == 'circle':
            return 2 * CIRCLE_R + 2 * RADIUS
        if kind == 'cross':
            return 2 * CROSS_UNIT + 2 * RADIUS
        if kind == 'zigzag':
            return COINS_PER_ZIGZAG * SPACING
        return COINS_PER_WAVE * SPACING

    def _zone_is_free(self, baddies, kind):
        """True if no Hazard overlaps the spawn area for the chosen pattern."""
        zone = pygame.Rect(WINDOWWIDTH, 0, self._width(kind) + 100, WINDOWHEIGHT)
        return not any(zone.colliderect(b.rect) for b in baddies)

    def _add_coin(self, x, y):
        """Creates one coin centered on (x, y)."""
        rect = pygame.Rect(0, 0, 2 * RADIUS, 2 * RADIUS)
        rect.center = (int(x), int(y))
        self.coins.append({'rect': rect, 'x': float(x)})

    def _spawn_wave(self):
        """Wavy row of coins, just outside the screen on the right."""
        # Keep the whole row (wave included) between the ceiling and the floor
        margin = WAVE_AMPLITUDE + RADIUS
        y = random.randint(CEILING + margin, FLOOR - margin)

        for i in range(COINS_PER_WAVE):
            x = WINDOWWIDTH + 30 + i * SPACING
            wave = WAVE_AMPLITUDE * math.sin(i * 0.7)
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

    def _spawn_cross(self):
        """Cross of 5 coins (center + 4 arms), just outside the screen on the right."""
        # Center: the leftmost coin starts 30 px after the right border
        cx = WINDOWWIDTH + 30 + CROSS_UNIT + RADIUS
        # Keep the whole cross between the ceiling and the floor
        margin = CROSS_UNIT + RADIUS
        cy = random.randint(CEILING + margin, FLOOR - margin)

        # Offsets (dx, dy) of the 5 coins relative to the center, in grid units
        for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
            self._add_coin(cx + dx * CROSS_UNIT, cy + dy * CROSS_UNIT)

    def _spawn_zigzag(self):
        """Zigzag row of coins, just outside the screen on the right."""
    # Keep all coins between the ceiling and the floor
        margin = ZIGZAG_AMPLITUDE + RADIUS
        y = random.randint(CEILING + margin, FLOOR - margin)

        for i in range(COINS_PER_ZIGZAG):
            x = WINDOWWIDTH + 30 + i * SPACING

            # Alternate between upper and lower positions
            offset = ZIGZAG_AMPLITUDE if i % 2 == 0 else -ZIGZAG_AMPLITUDE

            self._add_coin(x, y + offset)

    def _spawn(self, kind):
        """Calls the right generator for the chosen pattern."""
        if kind == 'circle':
            self._spawn_circle()
        elif kind == 'cross':
            self._spawn_cross()
        elif kind == 'zigzag':
            self._spawn_zigzag()
        else:
            self._spawn_wave()

    def update(self, player_rect, speed, baddies, blocked=False, dt=1 / FPS, interval=COIN_INTERVAL):
        """
        Advances one frame: spawn, move, pickup, cleanup.
        `speed` is in pixels/second; baddies contains Hazard objects.
        `blocked` is True when no new coins may appear (portal incoming or transition).
        Returns the number of coins collected during this frame.
        """
        # --- Spawn (frozen while a portal is pending, like the geese) ---
        if not blocked:
            self.timer -= dt * FPS
            if self.timer <= 0:
                if self._zone_is_free(baddies, self.next_kind):
                    self._spawn(self.next_kind)
                    # Choose the next pattern now, so the zone check uses the right size
                    self.next_kind = random.choice(self.PATTERNS)
                    # COIN_INTERVAL is in seconds, convert it to frames
                    self.timer = random.randint(int(interval[0] * FPS), int(interval[1] * FPS))
                else:
                    self.timer = 10          # area occupied: try again in 10 frames

        # --- Move, pickup, leave the screen (always, even while blocked) ---
        collected = 0
        for coin in self.coins[:]:
            coin['x'] -= speed * dt
            coin['rect'].centerx = round(coin['x'])
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