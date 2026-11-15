import pygame, random, sys, math
from pygame.locals import *

from menu import show_menu
from settings import*
from gravity import JetpackPhysics
from visuals import Visuals
from entities import Hazard
from worlds import next_hazard


def terminate():
    pygame.quit()
    sys.exit()

def waitForPlayerToPressKey():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: # Pressing ESC quits.
                    terminate()
                return


def drawText(text, font, surface, x, y):
    textobj = font.render(text, 1, TEXTCOLOR)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Set up pygame, the window, and the mouse cursor.
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption("Leprechaun Escape")
pygame.mouse.set_visible(False)

# Set up the fonts.
font = pygame.font.SysFont(None, 48)

# Set up sounds.
gameOverSound = pygame.mixer.Sound('assets/gameover.wav')
pygame.mixer.music.load('assets/background.mid')

# Set up visuals and mask.
visuals = Visuals()
playerRect = visuals.get_rect()

# Provide the shared resources to all hazards.
Hazard.configure(
    visuals.obstacle_frames,
    visuals.obstacle_masks,
    visuals.jet_images)

topScore = 0
last_score = None
sound_enabled = True
gravity = JetpackPhysics()

while True:
    # Show the menu before each game.
    sound_enabled = show_menu(
        windowSurface,
        high_score=topScore,
        last_score=last_score,
        sound_enabled=sound_enabled
    )

    # Apply the selected sound setting.
    pygame.mixer.music.set_volume(1.0 if sound_enabled else 0.0)
    gameOverSound.set_volume(1.0 if sound_enabled else 0.0)

    # Prepare a new game.
    hazards = []

    world = 'meadow'
    distance = 0.0
    score = 0

    # Speed in pixels per second.
    speed = START_SPEED

    # Wait a bit before the first obstacle.
    danger_timer = 1.5

    playerRect.center = (WINDOWWIDTH / 3 - 100, WINDOWHEIGHT / 2)

    gravity.reset(playerRect.centery)
    thrusting = False

    visuals.reset_jet()
    pygame.mixer.music.play(-1, 0.0)

    # Loop of a game.
    while True:
        # No fixed time step to remain consistent with the current physics.
        dt = 1 / FPS

        # 1. Read commands.
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    thrusting = True

            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminate()

                if event.key == K_SPACE:
                    thrusting = False

        # 2. Update the distance and the score. 
        distance += speed * dt * METERS_PER_PIXEL
        score = int(distance)

        # 3. Update the player’s position and the jet’s position and animation.
        visuals.update_pose()
        playerRect.centery = gravity.update(thrusting, playerRect.height, WINDOWHEIGHT)
        visuals.update_jet(playerRect, thrusting)

        # 4. Move the existing obstacles.
        for obstacle in hazards:
            obstacle.update(dt, speed, playerRect)

        # Discard the obstacles that have left the screen or finished their jet.
        hazards = [
            obstacle
            for obstacle in hazards
            if not obstacle.offscreen()]

        # 5. Try to create a new obstacle.
        danger_timer -= dt

        if danger_timer <= 0:
            obstacle = next_hazard(world, distance, hazards, speed, playerRect.centerx)

            if obstacle is not None:
                hazards.append(obstacle)

                # Avancer progressivement du délai initial au délai minimal.
                progress = min(1.0, distance / DENSITY_MAX_DISTANCE)

                interval = (OBSTACLE_INTERVAL_START + (OBSTACLE_INTERVAL_MIN - OBSTACLE_INTERVAL_START) * progress)

                danger_timer = max( OBSTACLE_INTERVAL_MIN, interval * random.uniform(0.9, 1.1))
            else:
                # Réessayer bientôt si les règles interdisent l’apparition.
                danger_timer = 0.15
 
        # 6. Verify the collisions using the mask of the player and the obstacles. The collision is detected if the masks overlap.
        collision = False

        for obstacle in hazards:
            if obstacle.collides_with(playerRect, visuals.mask):
                collision = True
                break

        # 7. Draw the game.
        visuals.draw_background(windowSurface)
        for obstacle in hazards:
            visuals.draw_obstacle(windowSurface, obstacle)
        visuals.draw_player(windowSurface, playerRect)

        # Draw the banner and the texts above the game.
        pygame.draw.rect(windowSurface, (10, 35, 38), (0, 0, WINDOWWIDTH, CEILING))

        pygame.draw.line(windowSurface, (25, 60, 60), (0, CEILING), (WINDOWWIDTH, CEILING), 2)
        drawText(f'Distance : {score} m', font, windowSurface, 10, 0)
        drawText(f'Record : {topScore} m', font, windowSurface, 10, 40)

        pygame.display.update()

        # 8. End the game if the player has collided with an obstacle. Actualize the top score if necessary.
        if collision:
            topScore = max(topScore, score)
            break

        # Limit the number of frames per second.
        mainClock.tick(FPS)

    # Stop the music and play the game-over sound.
    pygame.mixer.music.stop()
    gameOverSound.play()

    # Save the latest score before returning to the menu.
    last_score = score