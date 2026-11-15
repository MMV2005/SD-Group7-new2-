import pygame, random, sys
from game_strip import GameStrip
from pygame.locals import *
from entities import *
from coins import CoinSpawner
from menu import show_menu
from settings import*
from gravity import JetpackPhysics
from visuals import Visuals
from entities import Hazard
from worlds import next_hazard, next_gate, other_world
from transitions import Transition


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
pygame.mouse.set_visible(True)

# Set up the fonts.
font = pygame.font.SysFont(None, 48)

# Set up sounds.
gameOverSound = pygame.mixer.Sound('assets/gameover.wav')
pygame.mixer.music.load('assets/background.mid')

# Set up images.
visuals = Visuals()               # loads the 3 frames and their masks
hud = GameStrip()
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
coins = CoinSpawner()
coin_count = 0

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

    # main.1 : Réinitialiser la partie et le monde.
    hazards = []
    world = 'meadow'
    distance = 0.0
    score = 0
    speed = START_SPEED

    # Délais avant les obstacles.
    danger_timer = 1.5
    safe_timer = 0.0

    # Position et mouvement du personnage.
    playerRect.center = (WINDOWWIDTH / 3 - 100, WINDOWHEIGHT / 2)
    gravity.reset(playerRect.centery)
    thrusting = False

    # Effets visuels, pièces et bandeau.
    visuals.reset_jet()
    coins.reset()
    coin_count = 0
    hud.reset()

    # Préparation des portails.
    next_portal = next_gate(distance)
    portal_x = None
    portal_destination = None
    transition = None

    pygame.mixer.music.play(-1, 0.0)
    # main.2 : Boucle de la partie.
    while True:
        # Pas de temps fixe, compatible avec notre physique actuelle.
        dt = 1 / FPS

        # Aucune collision détectée au début de cette image.
        collision = False
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

                # main.3 : Faire avancer une transition en cours.
        if transition is not None:

            # Changer le monde lorsque le nuage couvre l'écran.
            if transition.update(dt):
                world = transition.destination

            # Terminer la transition et préparer la suite.
            if transition.done:
                transition = None
                portal_destination = None

                safe_timer = SAFE_SECONDS
                danger_timer = 0.0

                next_portal = next_gate(distance)

        # main.4 : Faire avancer le jeu seulement hors transition.
        else:
            safe_timer = max(0.0, safe_timer - dt)

            # Augmenter progressivement la vitesse.
            speed = min(
                MAX_SPEED,
                START_SPEED + distance * SPEED_PER_METER
            )

            distance += speed * dt * METERS_PER_PIXEL
            score = int(distance)

            # Animation et mouvement du personnage.
            visuals.update_pose()
            playerRect.centery = gravity.update(
                thrusting,
                playerRect.height,
                WINDOWHEIGHT
            )
            visuals.update_jet(playerRect, thrusting)

            # main.5 : Déplacer les obstacles déjà présents.
            for obstacle in hazards:
                obstacle.update(dt, speed, playerRect)

            # Retirer les obstacles sortis ou ayant terminé leur tir.
            hazards = [
                obstacle
                for obstacle in hazards
                if not obstacle.offscreen()
            ]

            # main.6 : Déterminer si un portail doit arriver.
            gate_pending = distance >= next_portal

            # Attendre la sortie des obstacles avant de créer le portail.
            if gate_pending and portal_x is None and not hazards:
                portal_x = WINDOWWIDTH + 140
                portal_destination = other_world(world)

            # main.7 : Déplacer le portail vers la gauche.
            if portal_x is not None:
                portal_x -= speed * dt

                # Déclencher la transition quand il atteint le joueur.
                if portal_x <= playerRect.centerx:
                    transition = Transition(
                        portal_destination,
                        start_x=portal_x - 20,
                        portal_x=portal_x
                    )

                    # La transition dessine désormais le portail.
                    portal_x = None
                    coins.reset()

            # main.8 : Autoriser ou bloquer les nouveaux obstacles.
            can_spawn = (
                not gate_pending
                and portal_x is None
                and transition is None
                and safe_timer <= 0
            )

            if can_spawn:
                danger_timer -= dt

                if danger_timer <= 0:
                    obstacle = next_hazard(
                        world,
                        distance,
                        hazards,
                        speed,
                        playerRect.centerx
                    )

                    if obstacle is not None:
                        hazards.append(obstacle)

                        # Réduire progressivement le délai d'apparition.
                        progress = min(
                            1.0,
                            distance / DENSITY_MAX_DISTANCE
                        )

                        interval = (
                            OBSTACLE_INTERVAL_START
                            + (
                                OBSTACLE_INTERVAL_MIN
                                - OBSTACLE_INTERVAL_START
                            ) * progress
                        )

                        danger_timer = max(
                            OBSTACLE_INTERVAL_MIN,
                            interval * random.uniform(0.9, 1.1)
                        )

                    else:
                        # Réessayer si aucun obstacle n'était autorisé.
                        danger_timer = 0.15

            # main.9 : Vérifier les collisions hors transition et sécurité.
            if transition is None and safe_timer <= 0:
                for obstacle in hazards:
                    if obstacle.collides_with(playerRect, visuals.mask):
                        collision = True
                        break
                # main.10 : Dessiner le fond du monde actuel.
        visuals.draw_background(windowSurface, world)

        # Dessiner les obstacles et le personnage.
        for obstacle in hazards:
            visuals.draw_obstacle(windowSurface, obstacle)

        visuals.draw_player(windowSurface, playerRect)

        # main.11 : Dessiner le portail pendant son approche.
        if portal_x is not None:
            visuals.draw_portal(windowSurface, portal_x)

        # main.12 : Dessiner la transition par-dessus le décor.
        if transition is not None:
            transition.draw(
                windowSurface,
                visuals.portal_image
            )

        # main.13 : Dessiner le bandeau au-dessus de la transition.
        pygame.draw.rect(
            windowSurface,
            (10, 35, 38),
            (0, 0, WINDOWWIDTH, CEILING)
        )

        pygame.draw.line(
            windowSurface,
            (25, 60, 60),
            (0, CEILING),
            (WINDOWWIDTH, CEILING),
            2
        )

        drawText(
            f'Distance : {score} m',
            font,
            windowSurface,
            10,
            0
        )

        drawText(
            f'Record : {topScore} m',
            font,
            windowSurface,
            10,
            40
        )

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

    drawText('GAME OVER', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))
    drawText('Press a key to play again.', font, windowSurface, (WINDOWWIDTH / 3) - 80, (WINDOWHEIGHT / 3) + 50)
    pygame.display.update()
    waitForPlayerToPressKey()


    # Save the latest score before returning to the menu.
    last_score = score