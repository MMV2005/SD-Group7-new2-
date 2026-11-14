import pygame, random, sys, math
from pygame.locals import *

from menu import afficher_menu
from settings import*
from gravity import JetpackPhysics
from visuals import Visuals

TEXTCOLOR = (255, 255, 255)
BACKGROUNDCOLOR = (255, 255, 255)
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
baddieImage = pygame.image.load('assets/baddie.png').convert_alpha()

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
    coins = []                 # particules du jet de pièces
    jet_accumulator = 0.0      # reste fractionnaire : 145/60 = 2,4 pièces par image
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

        # Add new baddies at the right of the screen, if needed.
        baddieAddCounter += 1
        if baddieAddCounter == ADDNEWBADDIERATE:
            baddieAddCounter = 0
            baddieSize = random.randint(BADDIEMINSIZE, BADDIEMAXSIZE)
            # On redimensionne l'image d'abord pour pouvoir créer son masque juste après
            scaledBaddie = pygame.transform.scale(baddieImage, (baddieSize, baddieSize))
            newBaddie = {'rect': pygame.Rect(
                WINDOWWIDTH,
                random.randint(CEILING, FLOOR - baddieSize), baddieSize, baddieSize),
            'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
            'surface': scaledBaddie,
            'mask': pygame.mask.from_surface(scaledBaddie), # Hitbox au pixel près de l'ennemi
            }

            baddies.append(newBaddie)

        # Move the player.
        playerRect.centery = gravity.update(thrusting, playerRect.height, WINDOWHEIGHT)

        #jet de pièces 
        dt = 1 / FPS               # pas de temps fixe, puisque main.py tourne à FPS constant
        # Création : JET_RATE particules par seconde, plafonnées à JET_MAX
        if thrusting:
            jet_accumulator += JET_RATE * dt
            while jet_accumulator >= 1 and len(coins) < JET_MAX:
                jet_accumulator -= 1
                life = random.uniform(*JET_LIFE)
                coins.append({
                    'x': playerRect.left + 8,
                    'y': playerRect.centery + playerRect.height * 0.25,
                    'vx': -random.uniform(*JET_SPEED),      # vers l'arrière
                    'vy': random.uniform(*JET_SPREAD),      # dispersion verticale
                    'life': life, 'initial': life,
                    'angle': random.uniform(0, math.tau),
                })
            if len(coins) >= JET_MAX:
                jet_accumulator = 0.0                       # évite l'accumulation quand le plafond est atteint

        # Mise à jour : mêmes équations qu'avant, mais en secondes
        for c in coins[:]:
            c['vy'] += JET_GRAVITY * dt
            c['x'] += c['vx'] * dt
            c['y'] += c['vy'] * dt
            c['angle'] += 24 * dt # environ 0,4 rad par image
            c['life'] -= dt
            if c['life'] <= 0 or c['y'] > FLOOR:
                coins.remove(c)

        # Move the baddies from the right side of the screen.
        for b in baddies:
            b['rect'].move_ip(-b['speed'], 0)

        # Supprimer les obstacles entièrement sortis à gauche.
        for b in baddies[:]:
            if b['rect'].right < 0:
                baddies.remove(b)

        # Draw the game world on the window.
        visuals.draw_background(windowSurface)

        # Bandeau du plafond (de 0 à CEILING)
        pygame.draw.rect(windowSurface, (10, 35, 38), (0, 0, WINDOWWIDTH, CEILING))
        pygame.draw.line(windowSurface, (25, 60, 60), (0, CEILING), (WINDOWWIDTH, CEILING), 2)

        # Draw the score and top score.
        drawText('Score: %s' % (score), font, windowSurface, 10, 0)
        drawText('Top Score: %s' % (topScore), font, windowSurface, 10, 40)

        
        # Dessin des pièces du jet (avant le joueur, pour qu'elles semblent en sortir)
        for c in coins:
            # Taille proportionnelle à la durée de vie restante : elles rétrécissent en fin de vie
            h = max(3, round(10 * c['life'] / c['initial']))
            # Largeur en |cos(angle)| : simule la pièce qui tourne sur elle-même
            w = max(2, round(h * abs(math.cos(c['angle']))))
            rect = (round(c['x']), round(c['y']), w, h)
            pygame.draw.ellipse(windowSurface, (242, 171, 24), rect)       # corps doré
            pygame.draw.ellipse(windowSurface, (255, 214, 99), rect, 1)    # contour clair

        # Draw the player.
        visuals.draw_player(windowSurface, playerRect)

        # Draw each baddie.
        for b in baddies:
            windowSurface.blit(b['surface'], b['rect'])

        pygame.display.update()

        # Check if any of the baddies have hit the player.
        if playerHasHitBaddie(playerRect, playerMask, baddies):
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