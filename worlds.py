"""World selection and obstacle spawning rules."""
import random

from entities import Hazard
from settings import (WIDTH, PORTAL_MIN, PORTAL_MAX, MEADOW_HEIGHTS, PUB_HEIGHTS, LAUNCHER_MIN_DISTANCE, TWO_OBSTACLES_DISTANCE, 
                      THREE_OBSTACLES_DISTANCE, OBSTACLE_GAP_MIN, OBSTACLE_GAP_SECONDS, LAUNCHER_MIX_DISTANCE, MAX_LAUNCHERS, LAUNCHER_VERTICAL_GAP)


# worlds.1 — Display names and destinations available through ordinary portals.
NAMES = {"meadow": "LES PRAIRIES", "pub": "LE PUB", "cave": "LA GROTTE DU DRAGON", "gold": "LA CITE D'OR"}
# Ordinary portals choose from these three worlds. Pots unlock the gold world.
NORMAL_WORLDS = ("meadow", "pub", "cave")

# worlds.2 — Schedule the next portal by adding a random distance in metres.
def next_gate(distance):
    return distance + random.randint(PORTAL_MIN, PORTAL_MAX)

# Exclude the current world so a portal always changes the scenery.
def other_world(current):
    return random.choice([world for world in NORMAL_WORLDS if world != current])

# worlds.3 — Portal position and destination. The current main loop tracks these directly.
class Portal:
    def __init__(self, destination):
        self.x = float(WIDTH + 140)  # Start the portal 140 pixels beyond the right edge.
        self.destination = destination

    def update(self, dt, speed):
        self.x -= speed * dt  # Convert speed in pixels per second to distance travelled this frame.

# worlds.4 — Draw a candidate. Repeated entries give a type more weight.
def new_hazard(world, distance):
    if world == 'meadow':
        # Two goose entries out of four give the ordinary goose a 50% chance initially.
        choices = ['barrel', 'fence', 'goose', 'goose']
        if distance > 450:  # Add the chasing goose only after the player passes 450 metres.
            choices += ['red_goose']
    elif world == 'pub':
        choices = ['barrel', 'mug', 'mug']  # Two mug entries make a mug twice as likely to be drawn as a barrel.
        if distance >= LAUNCHER_MIN_DISTANCE['pub']:
            choices += ['cannon']  # Include the pub's cannon once its distance requirement is met.
    else:
        choices = ['rock', 'rock', 'bat', 'bat']
        if distance >= LAUNCHER_MIN_DISTANCE['cave']:
            choices += ['flame']  # Include the cave's flame launcher once its distance requirement is met.
    kind = random.choice(choices)
    # Choose how a rock is placed if the obstacle drawn is a rock.
    shape = random.choice(('floor', 'ceiling', 'horizontal', 'vertical', 'diagonal'))
    if world == 'meadow':
        y = random.choice(MEADOW_HEIGHTS)
    elif world == 'pub':
        y = random.choice(PUB_HEIGHTS)
    else:
        y = random.choice((200, 285, 365))

    # Bats have their own set of starting heights.
    if kind == 'bat':
        y = random.choice((155, 210, 290, 370))

    return Hazard(kind, y, shape, random.randrange(4))  # Create the candidate. Fence variants are numbered 0 to 3.


# worlds.5 — Return an allowed candidate, or None so the main loop can retry.
def next_hazard(world, distance, hazards, speed):
    """Keep player_x in the public signature used by the main loop."""
    if world == "gold":  # Keep the bonus world free of hazards.
        return None

    # Launchers must appear alone until the mixing threshold is reached.
    mixed = distance >= LAUNCHER_MIX_DISTANCE
    launchers = [h for h in hazards if h.kind in ("cannon", "flame")]

    if launchers and not mixed:
        return None

    # Limit the total number of active hazards as distance increases.
    if distance < TWO_OBSTACLES_DISTANCE:
        maximum = 1
    elif distance < THREE_OBSTACLES_DISTANCE:
        maximum = 2  # Allow up to two active hazards from 2,000 m until 3,500 m.
    else:
        maximum = 3

    if len(hazards) >= maximum:  # Wait for an active hazard to leave before adding another.
        return None

    candidate = new_hazard(world, distance)

    if candidate.kind in ("cannon", "flame"):
        if hazards and not mixed:  # An incoming launcher needs an empty screen before 7,000 m.
            return None
        if len(launchers) >= MAX_LAUNCHERS:
            return None
        # A firing line must clear every active launcher by the configured vertical gap.
        available_heights = [y for y in (200, 285, 365) if all(abs(y - launcher.y) >= LAUNCHER_VERTICAL_GAP for launcher in launchers)]

        if not available_heights:  # Skip this spawn when every firing line would be too close to an existing one.
            return None

        candidate.y = random.choice(available_heights)
        candidate.base_y = candidate.y  # Store the accepted firing height as the launcher's reference height.
        return candidate

    # Fixed launchers are excluded from the horizontal gap check.
    moving = [h for h in hazards if h.kind not in ("cannon", "flame")]

    if moving:
        # Measure from the rightmost moving obstacle to the new spawn position.
        last = max(moving, key=lambda h: h.x)
        # Use the larger of a fixed pixel gap and a speed-dependent gap.
        minimum_gap = max(OBSTACLE_GAP_MIN, speed * OBSTACLE_GAP_SECONDS)

        # Reject the candidate if its spawn point is too close to the rightmost moving hazard.
        if WIDTH + 80 - last.x < minimum_gap:
            return None

    return candidate
