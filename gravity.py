from settings import CEILING, FLOOR, clamp
class JetpackPhysics():

    def __init__(self, gravity=0.3, thrust=0.5, max_fall_speed=11, max_rise_speed=17):
        # Tuning parameters (pixels per frame, or per frame squared)
        self.gravity = gravity                # downward acceleration
        self.thrust = thrust                  # upward acceleration (while Space is held)
        self.max_fall_speed = max_fall_speed  # maximum falling speed
        self.max_rise_speed = max_rise_speed  # maximum rising speed

        # Internal state
        self.y = 0.0         # exact vertical position of the player's center
        self.velocity = 0.0  # vertical velocity (negative = upward)

    def reset(self, center_y):
        """Call at the start of each game: resets at rest at the given height."""
        self.y = float(center_y)
        self.velocity = 0.0

    def update(self, thrusting, sprite_height, window_height = None):
        """Advance the physics by one frame and return the center's vertical position,
        rounded to an integer (ready to pass to a pygame.Rect)."""

        # 1. Acceleration based on the Space key state
        if thrusting:
            self.velocity -= self.thrust
        else:
            self.velocity += self.gravity

        # 2. Cap the velocity with clamp (settings.7)
        self.velocity = clamp(self.velocity, -self.max_rise_speed, self.max_fall_speed)
        # 3. Update the exact (floating-point) position
        self.y += self.velocity

        # 4. Clamp to CEILING (90) and FLOOR (475): self.y is the center position,
        #    so we keep half the sprite height as margin on each side
        half = sprite_height / 2
        if self.y < CEILING + half:
            self.y = CEILING + half
            self.velocity = 0.0
        elif self.y > FLOOR - half:
            self.y = FLOOR - half
            self.velocity = 0.0

        # 5. Integer position for rendering and collisions
        return round(self.y)