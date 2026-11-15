import pygame, random, sys
from pygame.locals import *
from entities import *
from coins import CoinSpawner
from menu import show_menu
from settings import*
from gravity import JetpackPhysics
from visuals import Visuals
from transitions import Transition

TEXTCOLOR = (255, 255, 255)
BACKGROUNDCOLOR = (5, 25, 30)
BADDIEMINSIZE = 100
BADDIEMAXSIZE = 100
BADDIEMINSPEED = 1
BADDIEMAXSPEED = 8
ADDNEWBADDIERATE = 50
PLAYERMOVERATE = 5

# -- AJOUT : mondes --
NORMAL_WORLDS = ('meadow', 'pub', 'cave')

def other_world(current):
    """Choisit un monde différent du monde actuel."""
    return random.choice([w for w in NORMAL_WORLDS if w != current])


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

# Source : Documentation Pygame (https://www.pygame.org/docs/ref/mask.html)
def playerHasHitBaddie(playerRect, playerMask, baddies):
    for b in baddies:
        # Calcul de la distance (offset) entre le coin haut-gauche du joueur et celui de l'ennemi
        offset_x = b['rect'].left - playerRect.left
        offset_y = b['rect'].top - playerRect.top

        # Vérifie si les pixels non-transparents des deux masques se superposent
        if playerMask.overlap(b['mask'], (offset_x, offset_y)) is not None:
            return True
    return False

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

# Set up images.
visuals = Visuals()               # loads the 3 frames and their masks
playerRect = visuals.get_rect()
playerMask = pygame.mask.from_surface(visuals.frames[0]) # Crée la hitbox au pixel près du joueur

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

    # Set up the start of the game.
    baddies = []
    score = 0
    coins.reset()
    coin_count = 0
    playerRect.center = (WINDOWWIDTH / 3 - 100, WINDOWHEIGHT /2)
    gravity.reset(playerRect.centery)
    thrusting = False
    baddieAddCounter = 0
    visuals.reset_jet()        # vide le jet à chaque nouvelle partie
    pygame.mixer.music.play(-1, 0.0)

    # --- AJOUT : mondes et portails ---
    world = 'meadow'                                    # monde affiché
    distance = 0                                        # distance parcourue (en mètres)
    next_portal = random.randint(PORTAL_MIN, PORTAL_MAX)  # distance du prochain portail
    transition = None                                   # transition en cours (ou None)
    portal_x = None                                     # position du portail à l'écran (None = pas de portail)
    portal_destination = None                           # monde où mène le portail


    while True: # The game loop runs while the game part is playing.
        score += 1 # Increase score.

        visuals.update_pose()

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

        # Nombre maximum d'oies à l'écran selon l'avancement (worlds.11)
        distance_meters = score 
        if distance_meters < TWO_OBSTACLES_DISTANCE:
            max_baddies = 1
        elif distance_meters < THREE_OBSTACLES_DISTANCE:
            max_baddies = 2
        else: 
            max_baddies = 3
        # 2. Vérifier l'écart minimal (OBSTACLE_GAP_MIN = 280 px) avec la dernière oie
        can_spawn = True
        if baddies:
            last_x = max(b['rect'].centerx for b in baddies)
            if (WINDOWWIDTH + 80) - last_x < OBSTACLE_GAP_MIN:
                can_spawn = False

        # --- AJOUT : portail dû, en approche ou transition en cours : plus aucune nouvelle oie ---
        # Le portail n'apparaît que lorsque la dernière oie a quitté l'écran : aucune oie n'est rattrapée ni supprimée.
        gate_pending = portal_x is not None or transition is not None or distance >= next_portal
        if gate_pending:
            can_spawn = False

        
        #3. Faire apparaître une nouvelle oie dès que le quota (< max_baddies) et l'écart (280 px) le permettent
        if len(baddies) < max_baddies and can_spawn:
            goose_y = random.choice(MEADOW_HEIGHTS)
            newBaddie = {
                'rect': visuals.get_goose_rect(WINDOWWIDTH + 80, goose_y),
                'speed': round(START_SPEED / FPS),
                'mask': visuals.goose_mask,
                'age': 0.0,
            }
            baddies.append(newBaddie)

        # Move the player.
        playerRect.centery = gravity.update(thrusting, playerRect.height, WINDOWHEIGHT)

        visuals.update_jet(playerRect, thrusting)    # crée et fait avancer les pièces

        # --- AJOUT : portail + changement de monde ---
        dt = 1 / FPS
        distance += START_SPEED * dt * METERS_PER_PIXEL
        if portal_x is None and transition is None and distance >= next_portal and not baddies:   # écran vide
            portal_x = WINDOWWIDTH + 140                    # le portail arrive par la droite, avec son nuage
            portal_destination = other_world(world)
        if portal_x is not None:
            portal_x -= START_SPEED * dt                    # le portail avance vers le joueur
            if portal_x <= playerRect.right:                # le joueur atteint le portail : la transition démarre
                transition = Transition(portal_destination, start_x=portal_x - 20, portal_x=portal_x)
                portal_x = None
        if transition:
            if transition.update(dt):                       # True une seule fois : écran entièrement couvert
                world = transition.destination              # on change le fond
            if transition.done:
                transition = None
                # Le portail suivant se calcule APRÈS la transition : deux transitions ne peuvent pas s'enchaîner.
                next_portal = distance + random.randint(PORTAL_MIN, PORTAL_MAX)


        # Move the baddies from the right side of the screen.
        for b in baddies:
            b['rect'].move_ip(-b['speed'], 0)
            b['age'] += 1 / FPS  # Incrémenter l'âge de l'oie pour l'animation des ailes

        # Coin speed matches the geese speed (pixels per frame)
        coin_speed = round(START_SPEED / FPS)
        # Update coins (spawn, move, collect) and add the collected ones to the counter
        coin_count += coins.update(playerRect, coin_speed, baddies)

        # Supprimer les obstacles entièrement sortis à gauche.
        for b in baddies[:]:
            if b['rect'].right < 0:
                baddies.remove(b)

        # Draw the game world on the window.
        visuals.draw_background(windowSurface, world)

        # Bandeau du plafond (de 0 à CEILING)
        pygame.draw.rect(windowSurface, (10, 35, 38), (0, 0, WINDOWWIDTH, CEILING))
        pygame.draw.line(windowSurface, (25, 60, 60), (0, CEILING), (WINDOWWIDTH, CEILING), 2)

        # Draw the score and top score.
        drawText('Score: %s' % (score), font, windowSurface, 10, 0)
        drawText('Top Score: %s' % (topScore), font, windowSurface, 10, 40)

        # Draw the coins after the background and ceiling, but before the player
        # so that the player is displayed in front of them
        coins.draw(windowSurface)

        # Draw the player.
        visuals.draw_player(windowSurface, playerRect)

        # Draw each baddie.
        for b in baddies:
            visuals.draw_goose(windowSurface, b)
            # --- AJOUT : portail avec son nuage, puis rideau de transition (par-dessus tout le reste) ---
        if portal_x is not None:
            visuals.draw_portal(windowSurface, portal_x)
        if transition:
            transition.draw(windowSurface, visuals.portal_image)   # le portail est emporté avec le rideau

        pygame.display.update()

        # Check if any of the baddies have hit the player.
        if playerHasHitBaddie(playerRect, visuals.mask, baddies):
            if score > topScore:
                topScore = score # set new top score
            break

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