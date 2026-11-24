"""Obstacle movement, animation and pixel-mask collisions."""
import math
import random
import pygame

from settings import ( WINDOWWIDTH, CEILING, FLOOR, BARREL_GRAVITY, BARREL_SPEED_RANGE, BARREL_JUMP_RANGE, LAUNCHER_HOLD_SECONDS, 
                      LAUNCHER_FADE_SECONDS, LAUNCHERS, JET_WARNING, JET_END, JET_HEIGHT, LASER_SCROLL_SPEED, LASER_TILE_GAP, MUG_SPIN_SPEED,)


# entities.1 — Shared resources and per-obstacle state.
class Hazard:
    # Visuals supplies these images and matching masks once for the entire class.
    frames_by_kind = {}
    masks_by_kind = {}
    jet_images = {}

    @classmethod
    def configure(cls, frames, masks, jets):
        cls.frames_by_kind = frames
        cls.masks_by_kind = masks
        cls.jet_images = jets

    def __init__(self, kind, y=280, shape='floor', variant=0):
        self.kind = kind
        self.shape = shape
        self.variant = variant

        # Rock shapes and fence variants select different sprite sets.
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

        # Keep subpixel positions for physics; round only when aligning the rectangle.
        self.x = float(WINDOWWIDTH + 80)
        self.y = float(y)
        self.base_y = float(y)  # Keep the reference height for a bat's oscillation or a mug's target.

        self.age = 0.0  # Time since this obstacle appeared, in seconds.
        self.vy = 0.0  # Vertical speed in px/s. Negative values move the sprite upwards.
        self.finished = False  # The main loop can remove a launcher once its firing and fading phases end.
        self.spin = random.choice((-1, 1)) * MUG_SPIN_SPEED  # Pick a rotation direction for the mug.
        self.jet_tile = None

        self.bounce_speed = random.uniform(*BARREL_JUMP_RANGE)
        self.speed_factor = random.uniform(*BARREL_SPEED_RANGE) if kind == 'barrel' else 1.0

        self.jet_surface = None
        self.jet_mask = None
        self.jet_rect = None

        if kind in ('barrel', 'fence'):
            self.y = FLOOR - self.image.get_height() / 2 # Initialize the height of the object at half his height (center) up the floor.

        if kind == 'barrel':
            self.vy = -self.bounce_speed  # Start the upward part of the bounce.

        if kind == 'mug':
            self.y = FLOOR - self.image.get_height() / 2

        if kind == 'rock':
            if shape == 'floor':
                self.y = FLOOR - self.image.get_height() / 2
            elif shape == 'ceiling':
                self.y = CEILING + self.image.get_height() / 2

        if kind in ('cannon', 'flame'):
            anchor_x = LAUNCHERS[kind][1][0]
            self.x = WINDOWWIDTH - 12 - self.image.get_width() * (1 - anchor_x) + 50

        self.sync_rect()

    # entities.2 — Align ordinary sprites by their centre and launchers by their muzzle.
    def sync_rect(self):
        if self.kind in ('cannon', 'flame'):
            anchor = LAUNCHERS[self.kind][1]
            mouth_x, mouth_y = self.muzzle

            self.rect = self.image.get_rect(
                topleft=(
                    round(mouth_x - self.image.get_width() * anchor[0]), 
                    round(mouth_y - self.image.get_height() * anchor[1])))  ## Position the sprite so its muzzle lines up with the start of the jet.
        
        else:
            self.rect = self.image.get_rect(center=(round(self.x), round(self.y)))
            if (self.kind == 'fence' or (self.kind == 'rock' and self.shape == 'floor')):
                self.rect.bottom = FLOOR  # Anchor the sprite's bottom edge to the floor.

            elif (self.kind == 'rock' and self.shape == 'ceiling'):
                self.rect.top = CEILING  # Attach the top edge of a hanging rock to the ceiling.

    @property
    def muzzle(self):
        # Return the screen coordinates of the point where the jet begins.
        return round(self.x - 50), round(self.y)

    @property
    def firing(self):
        return (self.kind in ('cannon', 'flame') and JET_WARNING <= self.age < JET_END)

    @property
    def opacity(self):
        elapsed = self.age - JET_END - LAUNCHER_HOLD_SECONDS  # Measure how long the launcher has been fading.
        if elapsed <= 0:
            return 255  # Full opacity during the warning, firing and hold phases.
        if LAUNCHER_FADE_SECONDS <= 0:
            return 0
        return round(255 * max(0.0, 1.0 - elapsed / LAUNCHER_FADE_SECONDS))


    # entities.3 — Build the jet after the spawning rules have selected a firing height.
    def prepare_jet(self):
        """Scale the visible jet tile to a fixed height and anchor the beam at the muzzle."""
        source = self.jet_images[self.kind]
        # Find the visible part of the source image before scaling its height.
        bounds = source.get_bounding_rect(min_alpha=20)
        if bounds.width and bounds.height:
            source = source.subsurface(bounds)
        tile_width = max(1, round(source.get_width() * JET_HEIGHT / source.get_height()))
        self.jet_tile = pygame.transform.scale(source, (tile_width, JET_HEIGHT))
        mouth_x, mouth_y = self.muzzle
        self.jet_surface = pygame.Surface((max(1, mouth_x), JET_HEIGHT), pygame.SRCALPHA)
        # Place the right end of the beam at the mouth so the jet extends left.
        self.jet_rect = self.jet_surface.get_rect(midright=(mouth_x, mouth_y))
        self.refresh_jet()

    def refresh_jet(self):
        """Scroll the repeating jet pattern and rebuild the mask from the visible pixels."""
        self.jet_surface.fill((0, 0, 0, 0))
        step = self.jet_tile.get_width() + max(0, LASER_TILE_GAP)
        phase = int(max(0.0, self.age - JET_WARNING) * LASER_SCROLL_SPEED) % step
        for x in range(-phase, self.jet_surface.get_width(), step):
            self.jet_surface.blit(self.jet_tile, (x, 0))
        self.jet_mask = pygame.mask.from_surface(self.jet_surface)

    # entities.4 — Advance one simulation step, then select the matching image and mask.
    def update(self, dt, speed, player_rect):
        first_update = self.age == 0.0

        if first_update:
            if self.kind in ('cannon', 'flame'):
                self.prepare_jet()

            elif self.kind == 'mug':
                # Estimate the flight time to the player’s x-coordinate at the current speed.
                travel = (self.x - player_rect.centerx) / max(speed, 1.0)
                travel = max(travel, 0.1)

                # Solve the constant-acceleration equation to reach the chosen target height.
                self.vy = (self.base_y - self.y - 0.5 * 100 * travel ** 2) / travel

        self.age += dt

        if self.kind in ('cannon', 'flame'):
            if self.firing:
                self.refresh_jet()
            self.finished = self.age >= JET_END + LAUNCHER_HOLD_SECONDS + LAUNCHER_FADE_SECONDS
            self.sync_rect()
            return

        # Only moving obstacles reach this point. Launchers return above.
        self.x -= speed * self.speed_factor * dt

        if self.kind == 'barrel':
            self.vy += BARREL_GRAVITY * dt
            self.y += self.vy * dt

            ground_y = FLOOR - self.image.get_height() / 2

            if self.y >= ground_y:
                self.y = ground_y
                self.bounce_speed = random.uniform(*BARREL_JUMP_RANGE)
                # Screen y increases downwards, so a negative velocity sends the barrel upwards.
                self.vy = -self.bounce_speed

        elif self.kind == 'red_goose':
            # Stop tracking vertically once the goose has passed the player.
            if self.x > player_rect.centerx:
                difference = player_rect.centery - self.y
                maximum_move = 100 * dt  # The red goose can change height by at most 100 pixels per second.

                self.y += max(-maximum_move, 
                              min(maximum_move, difference))

                half_height = self.image.get_height() / 2
                self.y = max(
                    CEILING + half_height, 
                    min(FLOOR - half_height, self.y))

        elif self.kind == 'bat':
            # The bat moves up and down by up to 32 pixels around its starting height.
            self.y = self.base_y + 32 * math.sin(self.age * 3.5)

        elif self.kind == 'mug':
            self.vy += 100 * dt  # Gravity bends the mug's path downwards after launch.
            self.y += self.vy * dt

        animation_fps = 8 if self.kind == 'bat' else 6
        # Modulo wraps the frame index back to zero at the end of the animation.
        index = int(self.age * animation_fps) % len(self.frames)

        self.image = self.frames[index]
        self.mask = self.masks[index]
        if self.kind == 'mug':
            # Rotate the original frame and rebuild its collision mask for this angle.
            self.image = pygame.transform.rotate(self.frames[index], self.age * self.spin)
            self.mask = pygame.mask.from_surface(self.image)

        self.sync_rect()

    # entities.5 — Check rectangle overlap before testing individual mask pixels.
    def collides_with(self, player_rect, player_mask):
        if self.kind in ('cannon', 'flame'):
            # Only the active jet can hit the player; its launcher body is decorative.
            if not self.firing or self.jet_mask is None:
                return False

            obstacle_rect = self.jet_rect
            obstacle_mask = self.jet_mask
        else:
            obstacle_rect = self.rect
            obstacle_mask = self.mask

        if not player_rect.colliderect(obstacle_rect):
            return False

        # The obstacle mask must be positioned relative to the player mask’s top-left corner.
        offset = (obstacle_rect.left - player_rect.left, obstacle_rect.top - player_rect.top)

        return player_mask.overlap(obstacle_mask, offset) is not None

    # entities.6 — Retire finished launchers, offscreen sprites and fallen mugs.
    def offscreen(self):
        if self.finished:
            return True

        if self.rect.right < 0:  # Once the right edge passes x = 0, the whole obstacle is off screen.
            return True

        # Remove the mug when even its top edge is well below the floor.
        if self.kind == 'mug' and self.rect.top > FLOOR + 100:
            return True

        return False
