"""TRANSITIONS — garder le portail visible jusqu'a ce qu'il quitte l'ecran."""
# transitions.1 : Préparation du module.
from functools import lru_cache
import math
import pygame
from settings import WINDOWWIDTH, WINDOWHEIGHT, TRANSITION_SECONDS, ASSETS

RAINBOW = [(224, 83, 83), (242, 163, 67), (245, 212, 81),
           (88, 179, 108), (77, 159, 209), (123, 104, 185)]

# transitions.2 : Charge et mémorise le rideau de transition.
@lru_cache(maxsize=2)
def curtain_texture(name):
    source = pygame.image.load(str(ASSETS / 'transition' / (name + '.png'))).convert()
    small = pygame.transform.scale(source, (WINDOWWIDTH // 2, WINDOWHEIGHT // 2))
    return pygame.transform.scale(small, (WINDOWWIDTH, WINDOWHEIGHT))

# transitions.3 : Recouvre une portion d’écran avec une texture opaque.
def draw_fog(screen, left, right=WINDOWWIDTH, name='fog', offset=None):
    left, right = round(left), round(right)
    if right <= 0 or left >= WINDOWWIDTH:
        return
    clip = screen.get_clip()
    screen.set_clip(pygame.Rect(left, 0, max(0, right - left), WINDOWHEIGHT))
    texture = curtain_texture(name)
    origin = left if offset is None else round(offset)
    origin = origin % WINDOWWIDTH - WINDOWWIDTH
    # Repeter la texture garantit la couverture meme avec un bord gauche negatif.
    if name == 'rainbow' and not (left == 0 and right == WINDOWWIDTH):
        # Bord ondule en petits paliers : une vague, pas un rectangle colore.
        for y in range(0, WINDOWHEIGHT, 6):
            edge = left + (round(26 * math.sin(y / 55)) if left != 0 else 0)
            end = right + (round(20 * math.sin(y / 70)) if right < WINDOWWIDTH else 0)
            screen.set_clip(pygame.Rect(edge, y, max(0, end - edge), 6).clip(clip))
            for x in range(origin, end + WINDOWWIDTH, WINDOWWIDTH):
                screen.blit(texture, (x, 0))
    else:
        for x in range(origin, right, WINDOWWIDTH):
            screen.blit(texture, (x, 0))
    screen.set_clip(clip)

# transitions.4 : Conserve la progression du changement de monde.
class Transition:
    # transitions.5 : Mémorise destination, style et position initiale du portail.
    def __init__(self, destination, style=None, start_x=None, portal_x=None):
        self.destination, self.style = destination, style or destination
        self.elapsed, self.switched = 0.0, False
        self.start_x = WINDOWWIDTH if start_x is None else start_x
        self.portal_start = portal_x

    # transitions.6 : Calcule une progression de zéro à un.
    @property
    def progress(self):
        return min(1.0, self.elapsed / TRANSITION_SECONDS)

    # transitions.7 : Indique que la transition est terminée.
    @property
    def done(self):
        return self.progress >= 1

    # transitions.8 : Adoucit le début et la fin du déplacement.
    @staticmethod
    def ease(t):
        return t * t * (3 - 2 * t)

    # transitions.9 : Calcule le bord gauche du rideau.
    @property
    def left(self):
        # Le bord parcourt encore 240 px hors ecran : le portail sort entierement.
        t = min(1, self.progress / 0.45)
        return self.start_x + (-240 - self.start_x) * self.ease(t)

    # transitions.10 : Calcule la position continue du portail.
    @property
    def portal_x(self):
        if self.portal_start is None:
            return None
        return self.portal_start + self.left - self.start_x

    # transitions.11 : Avance le temps et signale le milieu une seule fois.
    def update(self, dt):
        self.elapsed += dt
        if self.progress >= 0.5 and not self.switched:
            self.switched = True
            return True
        return False

    # transitions.12 : Dessine entrée, couverture totale puis sortie.
    def draw(self, screen, portal_image=None):
        p = self.progress
        if p >= 1:
            return
        texture = 'rainbow' if self.style == 'gold' else 'fog'
        if p <= 0.45:
            draw_fog(screen, self.left, name=texture)
            if portal_image is not None and self.portal_x is not None:
                # Meme sprite, meme position au premier instant, puis translation continue.
                screen.blit(portal_image, portal_image.get_rect(center=(round(self.portal_x + 26), 282)))
        elif p <= 0.55:
            draw_fog(screen, 0, name=texture, offset=-240)
        else:
            right = WINDOWWIDTH * (1 - self.ease((p - 0.55) / 0.45))
            draw_fog(screen, 0, right, texture, offset=-240 - (WINDOWWIDTH - right))
