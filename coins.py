import math
import random
import pygame
from settings import *

class CoinSpawner:
    """Spawns coin patterns from the right side, handles pickup and drawing."""

    PATTERNS = ('wave', 'circle', 'cross', 'zigzag')  # All available coin patterns
    GOLD_PATTERNS = ('gold_stream', 'gold_rain', 'gold_spiral', 'gold_arch')  # Patterns used in the gold world

    def __init__(self):
        self.coins = []  # Stores all active coins (position and collision rectangle)
        self.timer = FPS  # Wait one second before spawning the first pattern
        self.next_kind = random.choice(self.PATTERNS)  # Randomly select the first pattern

        # Load the coin image once and resize it to match the collision rectangle
        image = pygame.image.load(ASSETS / 'bonus' / 'gold_coin.png').convert_alpha()
        self.image = pygame.transform.smoothscale(image, (2 * RADIUS, 2 * RADIUS))

    def reset(self):
        """Call at the start of each game."""
        self.coins.clear()  # Remove all existing coins
        self.timer = FPS  # Reset the spawning timer
        self.next_kind = random.choice(self.PATTERNS)  # Choose a new random pattern

    def _width(self, kind):
        """Returns the horizontal size of a pattern in pixels."""
        if kind == 'circle':
            return 2 * CIRCLE_R + 2 * RADIUS  # Circle diameter + coin width
        if kind == 'cross':
            return 2 * CROSS_UNIT + 2 * RADIUS  # Full width of the cross
        if kind == 'zigzag':
            return COINS_PER_ZIGZAG * SPACING  # Total width of the zigzag
        if kind == 'gold_stream':
            return 15 * SPACING + 2 * RADIUS  # Width of three dense rows
        if kind == 'gold_rain':
            return 8 * SPACING + 2 * RADIUS  # Width of the coin shower
        if kind == 'gold_spiral':
            return 29 * 22 + 2 * RADIUS  # Width of the spiral
        if kind == 'gold_arch':
            return 23 * SPACING + 2 * RADIUS  # Width of the large arch
        return COINS_PER_WAVE * SPACING  # Default width: wave pattern

    def _zone_is_free(self, baddies, kind):
        """Checks whether the spawn area is free of hazards."""
        # Create a rectangle covering the area where the pattern will appear
        zone = pygame.Rect(WINDOWWIDTH, 0, self._width(kind) + 100, WINDOWHEIGHT)

        # Return True only if no hazard overlaps the spawn area
        return not any(zone.colliderect(b.rect) for b in baddies)

    def _add_coin(self, x, y):
        """Creates one coin centered at the given coordinates."""
        rect = pygame.Rect(0, 0, 2 * RADIUS, 2 * RADIUS)  # Create its collision rectangle
        rect.center = (int(x), int(y))  # Position the rectangle around the coin's center
        self.coins.append({'rect': rect, 'x': float(x)})  # Store the rectangle and exact x position

    def _spawn_wave(self):
        """Creates a wavy row of coins outside the screen."""
        # Leave enough space for the wave and the coin radius to stay within the limits (ceiling and floor)
        margin = WAVE_AMPLITUDE + RADIUS
        y = random.randint(CEILING + margin, FLOOR - margin)  # Random vertical center

        for i in range(COINS_PER_WAVE):
            x = WINDOWWIDTH + 30 + i * SPACING  # Place coins outside the right edge
            wave = WAVE_AMPLITUDE * math.sin(i * 0.7)  # Calculate the vertical wave offset
            self._add_coin(x, y + wave)  # Add the coin at its final position

    def _spawn_circle(self):
        """Creates a circle of coins outside the screen."""
        # Position the center so the entire circle starts outside the right edge
        cx = WINDOWWIDTH + 30 + CIRCLE_R + RADIUS

        # Keep the entire circle between the ceiling and the floor
        margin = CIRCLE_R + RADIUS
        cy = random.randint(CEILING + margin, FLOOR - margin)  # Random vertical center

        for k in range(CIRCLE_N):
            angle = 2 * math.pi * k / CIRCLE_N  # Calculate the angle of each coin in radians
            x = cx + CIRCLE_R * math.cos(angle)  # Calculate the horizontal position
            y = cy + CIRCLE_R * math.sin(angle)  # Calculate the vertical position
            self._add_coin(x, y)

    def _spawn_cross(self):
        """Creates a cross of five coins: one center coin and four arms."""
        # Position the center so the entire cross starts outside the right edge
        cx = WINDOWWIDTH + 30 + CROSS_UNIT + RADIUS

        # Keep the entire cross between the ceiling and the floor
        margin = CROSS_UNIT + RADIUS
        cy = random.randint(CEILING + margin, FLOOR - margin)  # Random vertical center

        # Each pair defines a coin's horizontal and vertical offset from the center
        for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
            self._add_coin(cx + dx * CROSS_UNIT, cy + dy * CROSS_UNIT)

    def _spawn_zigzag(self):
        """Creates a zigzag row of coins outside the screen."""
        # Keep all coins between the ceiling and the floor
        margin = ZIGZAG_AMPLITUDE + RADIUS
        y = random.randint(CEILING + margin, FLOOR - margin)  # Random vertical center

        for i in range(COINS_PER_ZIGZAG):
            x = WINDOWWIDTH + 30 + i * SPACING  # Place coins outside the right edge

            # Alternate between upper and lower positions to create the zigzag
            offset = ZIGZAG_AMPLITUDE if i % 2 == 0 else -ZIGZAG_AMPLITUDE
            self._add_coin(x, y + offset)

    def _spawn_gold_stream(self):
        """Creates three dense horizontal rows of coins."""
        # Keep all three rows between the ceiling and the floor
        margin = 2 * RADIUS + 8
        y = random.randint(CEILING + RADIUS + margin, FLOOR - RADIUS - margin)

        for row in range(3):
            for col in range(16):
                x = WINDOWWIDTH + 30 + col * SPACING
                coin_y = y + (row - 1) * margin
                self._add_coin(x, coin_y)

    def _spawn_gold_rain(self):
        """Creates a dense shower of coins across the playable area."""
        columns = 9
        rows = 5

        for col in range(columns):
            x = WINDOWWIDTH + 30 + col * SPACING

            for row in range(rows):
                # Spread the rows evenly while keeping every coin inside the playable area
                y = CEILING + RADIUS + row * (FLOOR - CEILING - 2 * RADIUS) / (rows - 1)
                self._add_coin(x, y)

    def _spawn_gold_spiral(self):
        """Creates a long spiral made of gold coins."""
        count = 30
        center_y = (CEILING + FLOOR) // 2

        for i in range(count):
            angle = i * 0.55
            x = WINDOWWIDTH + 30 + i * 22
            y = center_y + 135 * math.sin(angle)
            self._add_coin(x, y)

    def _spawn_gold_arch(self):
        """Creates a large arch made of gold coins."""
        count = 20
        center_y = random.randint(CEILING + RADIUS + 120, FLOOR - RADIUS)

        for i in range(count):
            x = WINDOWWIDTH + 30 + i * SPACING
            progress = i / (count - 1)
            y = center_y - 120 * math.sin(math.pi * progress)
            self._add_coin(x, y)

    def _spawn(self, kind):
        """Calls the generator corresponding to the selected pattern."""
        if kind == 'gold_stream':
            self._spawn_gold_stream()
        elif kind == 'gold_rain':
            self._spawn_gold_rain()
        elif kind == 'gold_spiral':
            self._spawn_gold_spiral()
        elif kind == 'gold_arch':
            self._spawn_gold_arch()
        elif kind == 'circle':
            self._spawn_circle()
        elif kind == 'cross':
            self._spawn_cross()
        elif kind == 'zigzag':
            self._spawn_zigzag()
        else:
            self._spawn_wave()  # Default pattern

    def update(self, player_rect, speed, baddies, blocked=False, dt=1 / FPS, interval=COIN_INTERVAL, gold=False):
        """
        Updates spawning, movement, collection and removal.
        Returns the number of coins collected during this frame.
        """
        # --- Spawn new patterns (paused when spawning is blocked) ---
        if not blocked:
            # Select the pattern family that matches the current world
            patterns = self.GOLD_PATTERNS if gold else self.PATTERNS

            # Make sure the next pattern belongs to the current world
            if self.next_kind not in patterns:
                self.next_kind = random.choice(patterns)

            self.timer -= dt * FPS  # Decrease the timer using elapsed time

            if self.timer <= 0:
                if self._zone_is_free(baddies, self.next_kind):
                    self._spawn(self.next_kind)  # Spawn the selected pattern

                    # Select the next pattern and set the delay before the next spawn
                    self.next_kind = random.choice(patterns)
                    self.timer = random.randint(int(interval[0] * FPS), int(interval[1] * FPS))
                else:
                    self.timer = 10  # Try again in 10 frames if a hazard blocks the area

        # --- Move existing coins and check for collisions ---
        collected = 0 # Count how many coins the player collects this frame

        # Use a copy so coins can safely be removed while looping
        for coin in self.coins[:]:
            coin['x'] -= speed * dt  # Move the coin to the left
            coin['rect'].centerx = round(coin['x'])  # Update its collision rectangle

            if coin['rect'].colliderect(player_rect):  # Check whether the player collects it
                self.coins.remove(coin)
                collected += 1
            elif coin['rect'].right < 0:  # Remove coins that have left the screen
                self.coins.remove(coin)

        return collected  # Send the number of coins collected for this frame back to the game

    def draw(self, surface):
        """Draws all active coins on the screen."""
        for coin in self.coins:
            surface.blit(self.image, coin['rect'])  # Draw the sprite at its position
