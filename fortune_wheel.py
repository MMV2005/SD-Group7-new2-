"""FortuneWheel : roue de la fortune affichée juste avant le Game Over.

Comme show_pause() et show_game_over(), la roue est BLOQUANTE : run() prend la
main, fait tourner sa propre boucle, puis renvoie le gain au main.
Les réglages (segments, poids, jackpot, images) sont dans settings.py.
"""
import random
import sys
import pygame
from pygame.locals import *
from menu import FONTS_DIR, MENU_ASSETS_DIR, MENU_ASSETS_DIR, draw_text, load_image

from settings import (WINDOWWIDTH, WINDOWHEIGHT, FPS, WHEEL_FILE,
                      WHEEL_POINTER_FILE, WHEEL_DIAMETER, WHEEL_SEGMENTS)
from sprite_assets import resolve_image_path

# Chaque segment occupe le même angle (45 degrés pour 8 segments).
SEGMENT_ANGLE = 360 / len(WHEEL_SEGMENTS)


def _scale_keep_ratio(image, target, by='max'):
    """Redimensionne en gardant les proportions (by='max' : plus grand côté,
    by='width' : largeur)."""
    w, h = image.get_size()
    factor = target / (max(w, h) if by == 'max' else w)
    return pygame.transform.smoothscale(image, (int(w * factor), int(h * factor)))


class FortuneWheel:
    SPIN_SECONDS = 4.5          # durée de rotation (s)
    RESULT_SECONDS = 2.0        # durée d'affichage du résultat (s)
    INPUT_DELAY = 0.6           # touches ignorées à l'apparition (évite le spam d'espace en mourant)
    MIN_TURNS, MAX_TURNS = 4, 6 # tours complets avant l'arrêt
    POINTER_TIP = 0.17          # hauteur de la POINTE du pointeur (fraction du diamètre depuis le haut de l'image)
    PANEL_W = 800               # largeur des panneaux (px)
    PANEL_H = 150               # hauteur des panneaux (px)

    # fb.1 : Chargement des images une seule fois (à appeler avant la boucle du jeu).
    def __init__(self):
        wheel = pygame.image.load(str(WHEEL_FILE)).convert_alpha()
        pointer = pygame.image.load(str(WHEEL_POINTER_FILE)).convert_alpha()
        self.wheel_img = _scale_keep_ratio(wheel, WHEEL_DIAMETER, 'max')
        self.pointer_img = _scale_keep_ratio(pointer, int(WHEEL_DIAMETER * 0.17), 'width')

        self.center = (WINDOWWIDTH // 2, WINDOWHEIGHT // 2 + 10)
        self.overlay = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 170))

        # Custom fonts matching the main menu
        self.title_font = pygame.font.Font(str(FONTS_DIR / "press_start.ttf"), 20)
        self.hint_font = pygame.font.Font(str(FONTS_DIR / "tiny5_duo.ttf"), 24)
        self.result_font = pygame.font.Font(str(FONTS_DIR / "pixelify.ttf"), 24)
        self.reset()

        # Wooden panels from the main menu
        panel_path = resolve_image_path(MENU_ASSETS_DIR / "wooden_button.png")
        panel = pygame.image.load(str(panel_path)).convert_alpha()
        w = min(self.PANEL_W, WINDOWWIDTH - 20) # min(...) évite que le panneau dépasse de la fenêtre si elle est étroite
        self.title_panel = pygame.transform.smoothscale(panel, (w, self.PANEL_H))
        self.bottom_panel = pygame.transform.smoothscale(panel, (w, self.PANEL_H))  

    # fb.2 : Remise à zéro à chaque nouvelle apparition de la roue.
    def reset(self):
        self.state = 'idle'        # idle -> spinning -> result -> (spinning si Luck) -> done
        self.angle = 0.0           # rotation actuelle (degrés, sens anti-horaire)
        self.target_angle = 0.0
        self.spin_t = 0.0
        self.result_t = 0.0
        self.age = 0.0
        self.result = None         # segment gagné lors du dernier spin
        # Gains cumulés sur toute la séance de roue (plusieurs spins possibles avec Luck).
        self.coins = 0
        self.revive = False
        self.jackpot = False

    @property
    def done(self):
        return self.state == 'done'

    # fb.3 : Tirage pondéré PUIS animation vers le segment tiré.
    def _start_spin(self):
        weights = [s['weight'] for s in WHEEL_SEGMENTS]
        index = random.choices(range(len(WHEEL_SEGMENTS)), weights=weights, k=1)[0]
        self.result = WHEEL_SEGMENTS[index]

        # pygame tourne une image dans le sens ANTI-horaire pour un angle positif.
        # Le segment i est centré à 45*i degrés (sens horaire) depuis le haut :
        # tourner la roue de 45*i degrés anti-horaire l'amène sous le pointeur.
        # Le décalage aléatoire garde 5 degrés de marge avec les bords du segment.
        half = SEGMENT_ANGLE / 2
        offset = random.uniform(-(half - 5), half - 5)
        turns = random.randint(self.MIN_TURNS, self.MAX_TURNS)
        # L'angle de départ est conservé (cas d'un respin) : on repart de l'angle actuel
        # modulo 360 pour que l'animation reste de 4 à 6 tours complets.
        self.angle %= 360
        self.target_angle = self.angle + 360 * turns + (index * SEGMENT_ANGLE + offset - self.angle) % 360
        self.start_angle = self.angle
        self.spin_t = 0.0
        self.state = 'spinning'

    # fb.4 : Application du gain d'un segment.
    def _resolve(self):
        kind, value = self.result['kind'], self.result['value']
        if kind == 'coins':
            self.coins += value
        elif kind == 'revive':
            self.revive = True
        elif kind == 'jackpot':
            self.coins += value
            self.revive = True
            self.jackpot = True
        # kind == 'luck' : aucun gain direct, la roue se relance (voir update).

    # fb.5 : Entrées : espace, entrée ou clic.
    def handle_event(self, event):
        if self.age < self.INPUT_DELAY:
            return
        pressed = (event.type == MOUSEBUTTONDOWN
                   or (event.type == KEYDOWN and event.key in (K_SPACE, K_RETURN)))
        if not pressed:
            return
        if self.state == 'idle':
            self._start_spin()
        elif self.state == 'result':
            self.result_t = self.RESULT_SECONDS   # passe l'écran de résultat

    # fb.6 : Mise à jour (dt en secondes).
    def update(self, dt):
        self.age += dt

        if self.state == 'spinning':
            self.spin_t += dt
            p = min(self.spin_t / self.SPIN_SECONDS, 1.0)
            eased = 1 - (1 - p) ** 3          # ease-out cubique : rapide au début, lent à la fin
            self.angle = self.start_angle + (self.target_angle - self.start_angle) * eased
            if p >= 1.0:
                self.angle = self.target_angle
                self._resolve()
                self.result_t = 0.0
                self.state = 'result'

        elif self.state == 'result':
            self.result_t += dt
            if self.result_t >= self.RESULT_SECONDS:
                if self.result['kind'] == 'luck':
                    self._start_spin()          # +1 Luck : relance automatique
                else:
                    self.state = 'done'

    # fb.7 : Dessin (sur le jeu figé, copié par run()).
    def _text(self, screen, font, text, color, y):
    # Render text with a dark outline
        surface = font.render(text, True, color)
        outline = font.render(text, True, (45, 20, 10))
        x = WINDOWWIDTH // 2
        # Draw the outline
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            screen.blit(outline, outline.get_rect(center=(x + dx, y + dy)))
        # Draw the main text
        screen.blit(surface, surface.get_rect(center=(x, y)))

    def _result_message(self):
        kind, value = self.result['kind'], self.result['value']
        if kind == 'coins':
            return f'+{value} coins!'
        if kind == 'luck':
            return '+1 Luck! Spin again!'
        if kind == 'revive':
            return 'Free revive!'
        return f'JACKPOT! +{value} coins and a free revive!'

    def draw(self, screen):
        screen.blit(self.overlay, (0, 0))

        # rotozoom : rotation lisse ; on recentre car la taille de l'image varie.
        rotated = pygame.transform.rotozoom(self.wheel_img, self.angle, 1.0)
        screen.blit(rotated, rotated.get_rect(center=self.center))

        # Pointeur fixe en haut, pointe vers le bas.
        top = self.center[1] - WHEEL_DIAMETER // 2
        pointer_rect = self.pointer_img.get_rect(
            midbottom=(self.center[0], top + int(WHEEL_DIAMETER * self.POINTER_TIP)))
        screen.blit(self.pointer_img, pointer_rect)

        # Draw the title panel
        title_rect = self.title_panel.get_rect(midtop=(WINDOWWIDTH // 2, -15))
        screen.blit(self.title_panel, title_rect)
        self._text(screen,self.title_font,"WHEEL OF FORTUNE",(255, 205, 35),title_rect.centery)

        # Draw the bottom instruction panel
        bottom_rect = self.bottom_panel.get_rect(midbottom=(WINDOWWIDTH // 2, WINDOWHEIGHT + 25))
        if self.state == 'idle' and self.age >= self.INPUT_DELAY:
            screen.blit(self.bottom_panel, bottom_rect)
            self._text(screen,self.hint_font,"PRESS SPACE TO SPIN",(255, 245, 220),bottom_rect.centery)
        elif self.state == 'result':
            screen.blit(self.bottom_panel, bottom_rect)
            self._text(screen,self.result_font,self._result_message(),(255, 205, 35),bottom_rect.centery)

    # fb.8 : Boucle bloquante. Renvoie les gains au main.
    def run(self, screen, clock):
        background = screen.copy()      # dernière image du jeu, figée derrière la roue
        self.reset()
        while not self.done:
            dt = min(clock.tick(FPS) / 1000, 0.05)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                self.handle_event(event)
            self.update(dt)
            screen.blit(background, (0, 0))
            self.draw(screen)
            pygame.display.update()
        return {'coins': self.coins, 'revive': self.revive, 'jackpot': self.jackpot}