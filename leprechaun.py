import random
import sys

import pygame
from pygame.locals import *

from gravity import JetpackPhysics
from menu import afficher_menu
from settings import (WINDOWWIDTH, WINDOWHEIGHT, FPS, ASSETS, RECORD_FILE,
                      START_SPEED, MAX_SPEED, CEILING, FLOOR,
                      CLOVER_TIME, POT_TIME, GUINNESS_TIME)

TEXTCOLOR = (0, 0, 0)
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
                if event.key == K_ESCAPE:
                    terminate()
                return


# Source : Documentation Pygame (https://www.pygame.org/docs/ref/mask.html)
def playerHasHitBaddie(playerRect, playerMask, baddies):
    for b in baddies:
        offset_x = b['rect'].left - playerRect.left
        offset_y = b['rect'].top - playerRect.top

        if playerMask.overlap(b['mask'], (offset_x, offset_y)) is not None:
            return True
    return False


def drawText(text, font, surface, x, y):
    textobj = font.render(str(text), True, TEXTCOLOR)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def initGameAssets():
    pygame.init()
    pygame.mixer.init()
    mainClock = pygame.time.Clock()
    windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('leprauchen')
    pygame.mouse.set_visible(False)

    font = pygame.font.SysFont(None, 48)
    gameOverSound = pygame.mixer.Sound('gameover.wav')
    pygame.mixer.music.load('background.mid')

    playerImage = pygame.image.load('player.png').convert_alpha()
    playerRect = playerImage.get_rect()
    playerMask = pygame.mask.from_surface(playerImage)
    baddieImage = pygame.image.load('baddie.png').convert_alpha()

    return mainClock, windowSurface, font, gameOverSound, playerImage, playerRect, playerMask, baddieImage


def playGame(windowSurface, font, gameplayClock, gameOverSound, playerImage, playerRect, playerMask, baddieImage, bestScore):
    gravity = JetpackPhysics()
    baddies = []
    score = 0
    playerRect.center = (WINDOWWIDTH // 3 - 100, WINDOWHEIGHT // 2)
    gravity.reset(playerRect.centery)
    thrusting = False
    reverseCheat = slowCheat = False
    baddieAddCounter = 0
    pygame.mixer.music.play(-1, 0.0)

    while True:
        score += 1

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            if event.type == KEYDOWN:
                if event.key == K_z:
                    reverseCheat = True
                if event.key == K_x:
                    slowCheat = True
                if event.key == K_SPACE:
                    thrusting = True

            if event.type == KEYUP:
                if event.key == K_z:
                    reverseCheat = False
                    score = 0
                if event.key == K_x:
                    slowCheat = False
                    score = 0
                if event.key == K_ESCAPE:
                    terminate()
                if event.key == K_SPACE:
                    thrusting = False

        if not reverseCheat and not slowCheat:
            baddieAddCounter += 1
        if baddieAddCounter >= ADDNEWBADDIERATE:
            baddieAddCounter = 0
            baddieSize = random.randint(BADDIEMINSIZE, BADDIEMAXSIZE)
            scaledBaddie = pygame.transform.scale(baddieImage, (baddieSize, baddieSize))
            newBaddie = {
                'rect': pygame.Rect(WINDOWWIDTH, random.randint(0, WINDOWHEIGHT - baddieSize), baddieSize, baddieSize),
                'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                'surface': scaledBaddie,
                'mask': pygame.mask.from_surface(scaledBaddie),
            }
            baddies.append(newBaddie)

        playerRect.centery = gravity.update(thrusting, playerRect.height, WINDOWHEIGHT)

        for b in baddies:
            if not reverseCheat and not slowCheat:
                b['rect'].move_ip(-b['speed'], 0)
            elif reverseCheat:
                b['rect'].move_ip(5, 0)
            elif slowCheat:
                b['rect'].move_ip(-1, 0)

        for b in baddies[:]:
            if b['rect'].right < 0 or b['rect'].top > WINDOWHEIGHT:
                baddies.remove(b)

        windowSurface.fill(BACKGROUNDCOLOR)
        drawText(f'Score: {score}', font, windowSurface, 10, 0)
        drawText(f'Top Score: {max(bestScore, score)}', font, windowSurface, 10, 40)
        windowSurface.blit(playerImage, playerRect)

        for b in baddies:
            windowSurface.blit(b['surface'], b['rect'])

        pygame.display.update()

        if playerHasHitBaddie(playerRect, playerMask, baddies):
            if score > bestScore:
                bestScore = score
            break

        gameplayClock.tick(FPS)

    pygame.mixer.music.stop()
    gameOverSound.play()
    pygame.time.wait(400)
    return bestScore, score


def main():
    mainClock, windowSurface, font, gameOverSound, playerImage, playerRect, playerMask, baddieImage = initGameAssets()
    bestScore = 0
    lastScore = None

    while True:
        start = afficher_menu(windowSurface, bestScore, lastScore)
        if not start:
            terminate()

        bestScore, lastScore = playGame(windowSurface, font, mainClock, gameOverSound, playerImage, playerRect, playerMask, baddieImage, bestScore)


if __name__ == '__main__':
    main()