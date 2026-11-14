import pygame, random, sys
from pygame.locals import *

from menu import afficher_menu
from settings import*
from gravity import JetpackPhysics
from visuals import Visuals

TEXTCOLOR = (255, 255, 255)
BACKGROUNDCOLOR = (5, 25, 30)
BADDIEMINSIZE = 100
BADDIEMAXSIZE = 100
BADDIEMINSPEED = 1
BADDIEMAXSPEED = 8
ADDNEWBADDIERATE = 50
PLAYERMOVERATE = 5

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
pygame.display.set_caption('Dodger')
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

# Show the "Start" screen.
afficher_menu(windowSurface, 0, None)
pygame.display.update()
topScore = 0
gravity = JetpackPhysics()
while True:
    # Set up the start of the game.
    baddies = []
    score = 0
    playerRect.center = (WINDOWWIDTH / 3 - 100, WINDOWHEIGHT /2)
    gravity.reset(playerRect.centery)
    thrusting = False
    baddieAddCounter = 0
    pygame.mixer.music.play(-1, 0.0)

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

        # Move the baddies from the right side of the screen.
        for b in baddies:
            b['rect'].move_ip(-b['speed'], 0)
            b['age'] += 1 / FPS  # Incrémenter l'âge de l'oie pour l'animation des ailes

        # Supprimer les obstacles entièrement sortis à gauche.
        for b in baddies[:]:
            if b['rect'].right < 0:
                baddies.remove(b)

        # Draw the game world on the window.
        windowSurface.fill(BACKGROUNDCOLOR)

        # Bandeau du plafond (de 0 à CEILING)
        pygame.draw.rect(windowSurface, (10, 35, 38), (0, 0, WINDOWWIDTH, CEILING))
        pygame.draw.line(windowSurface, (25, 60, 60), (0, CEILING), (WINDOWWIDTH, CEILING), 2)

        # Zone du sol (de FLOOR jusqu'en bas de l'écran) et ligne beige/dorée
        pygame.draw.rect(windowSurface, (4, 18, 22), (0, FLOOR, WINDOWWIDTH, WINDOWHEIGHT - FLOOR))
        pygame.draw.line(windowSurface, (180, 175, 130), (0, FLOOR), (WINDOWWIDTH, FLOOR), 2)

        # Draw the score and top score.
        drawText('Score: %s' % (score), font, windowSurface, 10, 0)
        drawText('Top Score: %s' % (topScore), font, windowSurface, 10, 40)

        # Draw the player's rectangle.
        visuals.draw_player(windowSurface, playerRect)

        # Draw each baddie.
        for b in baddies:
            visuals.draw_goose(windowSurface, b)
        pygame.display.update()

        # Check if any of the baddies have hit the player.
        if playerHasHitBaddie(playerRect, visuals.mask, baddies):
            if score > topScore:
                topScore = score # set new top score
            break

        mainClock.tick(FPS)

    # Stop the game and show the "Game Over" screen.
    pygame.mixer.music.stop()
    gameOverSound.play()

    drawText('GAME OVER', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))
    drawText('Press a key to play again.', font, windowSurface, (WINDOWWIDTH / 3) - 80, (WINDOWHEIGHT / 3) + 50)
    pygame.display.update()
    waitForPlayerToPressKey()