"""game_strip.py - Bande HUD affichée en haut du jeu.

Contenu de la bande (de gauche à droite) :
    score | pièces | trèfle (à trouver / trouvé / utilisé) | chaudron (0/3) | record

Le BAS DU CORPS EN BOIS de la bande est collé à CEILING (settings.py) : c'est la
limite haute du joueur, il se cogne donc la tête contre la bande. Les petits
trèfles qui dépassent sous la bande passent par-dessus le décor.
"""
import pygame
from settings import WINDOWWIDTH, CEILING, ASSETS

# --- game_strip.1 : image et placement -------------------------------------
HUD_FILE = ASSETS / 'game strip' / 'barre_hud.png'     # bande avec fond transparent
HUD_BOTTOM = CEILING        # y du bas du corps en bois de la bande (90 px)
HUD_TOP_MARGIN = 6          # espace (px) entre le haut de l'écran et le chapeau du lutin
BODY_BOTTOM = 215           # ligne du bas du corps en bois, en pixels de la bande recadrée

# --- game_strip.2 : états du trèfle et chaudron ----------------------------
CLOVER_TO_FIND, CLOVER_FOUND, CLOVER_USED = 'a_trouver', 'trouve', 'utilise'
CLOVER_TEXT = {CLOVER_TO_FIND: 'À trouver', CLOVER_FOUND: 'Trouvé !', CLOVER_USED: 'Utilisé'}
CLOVER_COLOR = {CLOVER_TO_FIND: (215, 215, 215),
                CLOVER_FOUND: (150, 255, 150),
                CLOVER_USED: (170, 170, 170)}
POT_MAX = 3                                     # chaudron : 0/3, 1/3, ...

# --- game_strip.3 : cases (x1, y1, x2, y2) en pixels de barre_hud.png ------
# Intérieur sombre de chaque case, mesuré sur la bande recadrée (2145 x 231, sans marge).
# Elles sont converties automatiquement à l'échelle de l'écran.
SLOTS = {'score':    (308, 91, 533, 169),
         'pieces':   (701, 91, 818, 169),
         'trefle':   (1003, 91, 1223, 169),
         'chaudron': (1417, 91, 1567, 169),
         'record':   (1800, 91, 1956, 169)}
CLOVER_ICON = (887, 80, 987, 178)               # icône du trèfle (à griser si pas trouvé)

TEXT_COLOR = (255, 255, 255)
SHADOW_COLOR = (25, 12, 0)


def format_number(n):
    """1961 -> 1'961 (séparateur suisse)."""
    return f"{n:,}".replace(',', "'")


class GameStrip:
    def __init__(self):
        source = pygame.image.load(str(HUD_FILE)).convert_alpha()
        # Recadrage automatique : enlève la marge transparente autour de la bande.
        # Sans ça, une image avec de la marge (2172 x 724 par ex.) serait dessinée
        # trop bas. Fonctionne avec l'image d'origine ou la version déjà recadrée.
        source = source.subsurface(source.get_bounding_rect(min_alpha=128)).copy()
        sw, sh = source.get_size()

        # Échelle uniforme (le pixel art n'est pas déformé) : le corps en bois
        # descend jusqu'à HUD_BOTTOM, le chapeau reste à HUD_TOP_MARGIN du haut.
        self.scale = (HUD_BOTTOM - HUD_TOP_MARGIN) / BODY_BOTTOM
        # Les coordonnées SLOTS sont mesurées sur la référence 2145 x 231.
        # L'image jointe est plus petite : normaliser l'échelle de référence.
        self.scale = min(self.scale, (WINDOWWIDTH - 12) / 2145)
        size = (round(sw * self.scale), round(sh * self.scale))
        self.image = pygame.transform.smoothscale(source, size)

        # Centrée horizontalement ; verticalement, le bas du corps tombe sur HUD_BOTTOM.
        self.pos = ((WINDOWWIDTH - size[0]) // 2,
                    HUD_BOTTOM - round(BODY_BOTTOM * self.scale))

        # Cases converties en rectangles écran.
        self.slots = {name: self._to_screen(box) for name, box in SLOTS.items()}
        self.pause_rect = self._to_screen((2025, 77, 2135, 190))

        # État du trèfle et du chaudron : géré ici pour ne pas toucher au main.
        # Les autres modules font simplement hud.clover = CLOVER_FOUND, hud.pot += 1...
        self.reset()

        # Police proportionnelle à la hauteur d'une case.
        self.font_size = round(self.slots['pieces'].height * 0.8)
        self.font = pygame.font.SysFont(None, self.font_size)
        # Centre vertical d'un chiffre : sert à aligner tous les textes sur la même ligne.
        self.digit_center_y = self.font.render('0', True, TEXT_COLOR).get_bounding_rect().centery

        # Icône du trèfle grisée (calculée une seule fois).
        icon_rect = self._to_screen(CLOVER_ICON)                 # position à l'écran
        local_rect = icon_rect.move(-self.pos[0], -self.pos[1])  # position dans l'image
        self.clover_pos = icon_rect.topleft
        self.clover_dim = self._make_dim(self.image.subsurface(local_rect).copy())

    def reset(self):
        """À appeler au début de chaque partie."""
        self.clover = CLOVER_TO_FIND
        self.pot = 0
        self.pot_max = POT_MAX

    # -- outils ------------------------------------------------------------
    def _to_screen(self, box):
        x1, y1, x2, y2 = box
        s = self.scale
        return pygame.Rect(self.pos[0] + round(x1 * s), self.pos[1] + round(y1 * s),
                           round((x2 - x1) * s), round((y2 - y1) * s))

    @staticmethod
    def _make_dim(icon):
        """Remplace les pixels verts par du gris (le fond bois reste intact)."""
        for x in range(icon.get_width()):
            for y in range(icon.get_height()):
                r, g, b, a = icon.get_at((x, y))
                if a > 0 and g > r + 25 and g > b + 25:
                    v = int((0.3 * r + 0.59 * g + 0.11 * b) * 0.75)
                    icon.set_at((x, y), (v, v, v, a))
        return icon

    def _draw_text(self, screen, text, slot, color=TEXT_COLOR):
        """Dessine le texte centré dans la case (centrage sur les pixels réellement dessinés)."""
        surf = self.font.render(text, True, color)
        shadow = self.font.render(text, True, SHADOW_COLOR)
        ref_y = self.digit_center_y                     # centre vertical d'un chiffre dans la police
        max_w = slot.width - 10
        if surf.get_bounding_rect().width > max_w:      # texte trop long : on le réduit
            k = max_w / surf.get_bounding_rect().width
            new_size = (max(1, round(surf.get_width() * k)), max(1, round(surf.get_height() * k)))
            surf = pygame.transform.smoothscale(surf, new_size)
            shadow = pygame.transform.smoothscale(shadow, new_size)
            ref_y *= k
        ink = surf.get_bounding_rect()                  # zone réellement dessinée (sans marges)
        pos = (slot.centerx - ink.centerx, round(slot.centery - ref_y))
        screen.blit(shadow, (pos[0] + 1, pos[1] + 1))
        screen.blit(surf, pos)

    # -- affichage ---------------------------------------------------------
    def draw(self, screen, score, coins, record):
        """À appeler en dernier dans la boucle de jeu (la bande passe par-dessus tout).

        score  : score de la partie en cours
        coins  : nombre de pièces (coin_count)
        record : meilleur score (topScore)
        Trèfle et chaudron viennent de self.clover (CLOVER_TO_FIND, CLOVER_FOUND,
        CLOVER_USED) et self.pot (0 à self.pot_max).
        """
        screen.blit(self.image, self.pos)

        if self.clover != CLOVER_FOUND:                 # grisé tant qu'il n'est pas trouvé
            screen.blit(self.clover_dim, self.clover_pos)

        self._draw_text(screen, format_number(score), self.slots['score'])
        self._draw_text(screen, format_number(coins), self.slots['pieces'])
        self._draw_text(screen, CLOVER_TEXT[self.clover], self.slots['trefle'], CLOVER_COLOR[self.clover])
        self._draw_text(screen, f'{self.pot}/{self.pot_max}', self.slots['chaudron'])
        self._draw_text(screen, format_number(record), self.slots['record'])