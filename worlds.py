"""3. MONDES — choix aleatoires limites pour garder des passages evitables."""
# worlds.1 : Préparation du module.
import random
from turtle import shape
from entities import Hazard
from settings import WIDTH, FLOOR, PORTAL_MIN, PORTAL_MAX, PAIR_DISTANCE, MIN_REACTION_SECONDS, LAUNCHER_MIN_DISTANCE
from settings import TWO_OBSTACLES_DISTANCE, THREE_OBSTACLES_DISTANCE, OBSTACLE_GAP_MIN, OBSTACLE_GAP_SECONDS
from settings import LAUNCHER_MIX_DISTANCE, MAX_LAUNCHERS, LAUNCHER_VERTICAL_GAP
from settings import MEADOW_HEIGHTS, PUB_HEIGHTS

NAMES = {"meadow": "LES PRAIRIES", "pub": "LE PUB",
         "cave": "LA GROTTE DU DRAGON", "gold": "LA CITE D'OR"}             # Indexes disponibles worlds, with their names (in capitals) for the title screen.
NORMAL_WORLDS = ("meadow", "pub", "cave")                                   # Definition of the normal worlds (without the gold one, which is a bonus world).

# worlds.2 : Choose the distance randomly between PORTAL_MIN and PORTAL_MAX, then add it to the current distance to get the next portal's distance.
def next_gate(distance):
    return distance + random.randint(PORTAL_MIN, PORTAL_MAX)

# worlds.3 : Choose a different world from actual one.
def other_world(current):
    return random.choice([world for world in NORMAL_WORLDS if world != current])

# worlds.4 : Representing the mandatory portal : only its X coordinate counts.
class Portal:
    # worlds.5 : Creating portal out of the screen and remembering its destination.
    def __init__(self, destination):
        self.x = float(WIDTH + 140)
        self.destination = destination

    # worlds.6 : Moving portal to the left.
    def update(self, dt, speed):
        self.x -= speed * dt

# worlds.7 : Define disponibles types of obstacles for each world. Draw a new obstacle adapted to the world and distance.
def new_hazard(world, distance):
    if world == 'meadow':
        choices = ['goose', 'goose']     # 'barrel', 'fence',       # list of the disponible obstracles for the meadow world. The repetition of 'goose' increases its probability of appearance.
#        if distance > 450:
#            choices += ['red_goose']
    elif world == 'pub':
        choices = []   #'barrel', 'mug', 'mug'                      # List of the disponible obstracles for the pub world. The repetition of 'mug' increases its probability of appearance.
#        if distance >= LAUNCHER_MIN_DISTANCE['pub']:
#            choices += ['cannon']                                  # Adding the cannon to the list of available obstacles for the pub world, if the distance is greater than or equal to the minimum distance for the launcher in the pub world.
    else:
        choices = []    #'rock', 'rock', 'bat', 'bat'               # List of the disponible obstracles for the cave world. The repetition of 'rock' and 'bat' increases their probability of appearance.
#        if distance >= LAUNCHER_MIN_DISTANCE['cave']:
#            choices += ['flame']                                   # Adding the flame to the list of available obstacles for the cave world, if the distance is greater than or equal to the minimum distance for the launcher in the cave world.
    kind = random.choice(choices)                                   # Choose the obstacle's type among those authorized.
    shape = random.choice(('floor', 'ceiling', 'horizontal', 'vertical', 'diagonal'))          # Choose a disposition, used for rocks.
#   # Choose a reference height according to the world.
    if world == 'meadow':
        y = random.choice(MEADOW_HEIGHTS)
    elif world == 'pub':
        y = random.choice(PUB_HEIGHTS)
    else:
        y = random.choice((200, 285, 365))      
        
    if kind == 'bat':                           # Replace the height with a value adapted to the bats.
        y = random.choice((155, 210, 290, 370))
       
    return Hazard(kind, y, shape, random.randrange(4))        # Create and send the obstacles with a variant between 0 and 3


# worlds.8 : Limit the combinations of obstacles to keep a passage in the middle of the screen.
# Generates up to three obstacles and combine the launchers after the threshold. The function returns None if no new obstacle can be added, or a new obstacle if it can be added.
def next_hazard(world, distance, hazards, speed, player_x):

    if world == "gold":
        return None                                                                     # The gold world has no obstacles.

    mixed = distance >= LAUNCHER_MIX_DISTANCE
    launchers = [h for h in hazards if h.kind in ("cannon", "flame")]                   # Combine launchers only after the threshold, and keep a minimum distance between their axes of fire.

    # Before the threshold, do not add anything when a launcher is present.
    if launchers and not mixed:
        return None

    # Progessive limit: one, two, then three obstacles.
    if distance < TWO_OBSTACLES_DISTANCE:
        maximum = 1
    elif distance < THREE_OBSTACLES_DISTANCE:
        maximum = 2
    else:
        maximum = 3

    if len(hazards) >= maximum:
        return None

    candidate = new_hazard(world, distance)

    # Launchers's specifics checks.
    if candidate.kind in ("cannon", "flame"):

        if hazards and not mixed:
            return None                                         # Do not add a launcher if there is already one present, before the threshold.

        if len(launchers) >= MAX_LAUNCHERS:
            return None                                         # Do not add a launcher if there are already the maximum number of launchers present.      

        # Keep enough space between the two lines of fire.
        available_heights = [
            y for y in (200, 285, 365)
            if all(
                abs(y - launcher.y) >= LAUNCHER_VERTICAL_GAP
                for launcher in launchers
            )
        ]                                                       # Calculate the available heights for the new launcher, keeping enough space between the two lines of fire.

        if not available_heights:
            return None                                         # Return None if there is no available height for the new launcher.

        candidate.y = random.choice(available_heights)          # Choose a random available height for the new launcher in the available heights.
        candidate.base_y = candidate.y                          # Set the base_y of the new launcher to its y coordinate, to keep it fixed at that height.
        return candidate                                        # Return the new launcher if it can be added.

    # Spacing the moving obstacles, without counting the fixed launchers.
    moving = [h for h in hazards if h.kind not in ("cannon", "flame")]

    if moving:
        last = max(moving, key=lambda h: h.x)
        minimum_gap = max(OBSTACLE_GAP_MIN, speed * OBSTACLE_GAP_SECONDS)       # The minimum gap is calculated based on the speed or a fixed value, depending on the highest.

        if WIDTH + 80 - last.x < minimum_gap:
            return None                                                         # Return None if the new obstacle is too close to the last one, to keep a passage in the middle of the screen.

    return candidate
