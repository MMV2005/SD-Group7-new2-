from functools import lru_cache

import pygame
from reglages_boutique import SKINS, dossier_skin
from settings import ASSETS
from sprite_assets import load_frames, load_image


@lru_cache(maxsize=5)
def portrait(skin):
    return load_frames([dossier_skin(skin) / "portrait.png"], (198, 172))[0]


class Arrow:
    """Flèche en bois cerclée de laiton ; les coins transparents ignorent le clic."""
    def __init__(self, center, left=False):
        image = pygame.Surface((68, 50), pygame.SRCALPHA)
        for color, points in (
            ("#382212", [(2,13),(35,13),(35,1),(66,24),(66,28),(35,49),(35,38),(2,38)]),
            ("#d59a40", [(4,15),(38,15),(38,6),(62,25),(38,43),(38,35),(4,35)]),
            ("#784016", [(7,18),(41,18),(41,12),(56,25),(41,37),(41,32),(7,32)]),
        ):
            pygame.draw.polygon(image, color, points)
        pygame.draw.line(image, "#f4cf87", (7,16), (38,16), 2)
        pygame.draw.line(image, "#9e6029", (14,24), (44,24), 2)
        pygame.draw.circle(image, "#eac477", (10,25), 2)
        self.image = pygame.transform.flip(image, left, False)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=center)
        self.highlight = self.image.copy()
        self.highlight.fill((30, 24, 12), special_flags=pygame.BLEND_RGB_ADD)

    def hit(self, pos):
        return self.rect.collidepoint(pos) and self.mask.get_at(
            (pos[0] - self.rect.x, pos[1] - self.rect.y)
        )

    def draw(self, window):
        image = self.highlight if self.hit(pygame.mouse.get_pos()) else self.image
        window.blit(image, self.rect)


def show_shop(window, boutique, image_menu):
    fonts = ASSETS / "fonts"
    font = pygame.font.Font(str(fonts / "pixelify.ttf"), 22)
    title_font = pygame.font.Font(str(fonts / "press_start.ttf"), 20)
    question_font = pygame.font.Font(str(fonts / "press_start.ttf"), 72)
    small = pygame.font.Font(str(fonts / "tiny5_duo.ttf"), 18)

    background = load_image(ASSETS / "menu" / "shop_background.png").convert()
    background = pygame.transform.scale(background, window.get_size())
    veil = pygame.Surface(window.get_size(), pygame.SRCALPHA)
    veil.fill((15, 9, 3, 40))
    background.blit(veil, (0, 0))

    chest = image_menu("chest", (44, 44))
    sign = image_menu("title", (292, 92))
    frame = pygame.Rect(361, 94, 238, 244)
    display = pygame.Rect(371, 103, 218, 182)
    left = Arrow((308, 209), left=True)
    right = Arrow((652, 209))
    buy = pygame.Rect(355, 350, 250, 49)
    equip = pygame.Rect(355, 403, 250, 49)
    back = pygame.Rect(386, 462, 188, 46)
    balance = pygame.Rect(10, 10, 202, 49)
    field = pygame.Rect(704, 476, 168, 42)
    field.midright = (940, 497)
    coin_font = pygame.font.Font(str(fonts / "tiny5_duo.ttf"), 24)
    clock = pygame.time.Clock()
    skins = list(SKINS)
    index = skins.index(boutique.equipe)
    code = message = ""
    editing = False

    def label(value, center, face=font, color=(255, 245, 217)):
        image = face.render(value, True, color)
        window.blit(image, image.get_rect(center=center))

    @lru_cache(maxsize=32)
    def plate(name, size, enabled=True):
        image = image_menu(name, size).copy()
        if not enabled:
            image.fill((145, 145, 145, 255), special_flags=pygame.BLEND_RGBA_MULT)
        return image

    def button(rect, value, enabled=True, green=False, face=font):
        name = "green_button" if green else "wooden_button"
        window.blit(plate(name, rect.size, enabled), rect)
        label(value, rect.center, face, (255, 245, 217) if enabled else (196, 187, 165))

    while True:
        skin = skins[index]
        info = SKINS[skin]
        owned = boutique.disponible(skin)
        equipped = skin == boutique.equipe
        hidden = info.get("mystere", False) and not owned
        window.blit(background, (0, 0))
        window.blit(sign, sign.get_rect(midtop=(480, 0)))
        # Centre optique de la planche sous le chapeau.
        heading = title_font.render("SKINS", True, (255, 245, 217))
        ink = heading.get_bounding_rect()
        window.blit(heading, (480 - ink.centerx, 54 - ink.centery))
        window.blit(plate("wooden_button", balance.size), balance)
        window.blit(chest, chest.get_rect(center=(40, balance.centery)))
        label(f"{boutique.pieces:,}", (128, balance.centery), coin_font)

        pygame.draw.rect(window, (48, 26, 18), frame.inflate(8, 8))
        pygame.draw.rect(window, (235, 176, 65), frame)
        pygame.draw.rect(window, (63, 40, 27), frame.inflate(-6, -6))
        pygame.draw.rect(window, (153, 155, 151) if hidden else (28, 64, 49), display)
        if hidden:
            label("?", display.center, question_font, (72, 76, 73))
        else:
            image = portrait(skin)
            window.blit(image, image.get_rect(center=display.center))
        label("Mystery skin" if hidden else info["nom"], (480, 307))
        label(f"{index + 1} / {len(skins)}", (480, 327), small, (229, 193, 123))
        left.draw(window)
        right.draw(window)
        button(buy, "OWNED" if owned else f"BUY  {info['prix']:,}", not owned, not owned)
        button(equip, "EQUIPPED" if equipped else "EQUIP", owned and not equipped, owned and not equipped)
        button(back, "MENU")
        admin_label = "Exit admin" if boutique.admin else "Admin code"
        if editing:
            admin_label = "*" * len(code) or "Code + Enter"
        button(field, admin_label, green=editing or boutique.admin, face=small)
        if message:
            image = font.render(message, True, (255, 244, 212))
            rect = image.get_rect(midbottom=(480, 538))
            pygame.draw.rect(window, (40, 30, 20), rect.inflate(18, 3))
            window.blit(image, rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            direction = 0
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                editing = field.collidepoint(event.pos) and not boutique.admin
                if field.collidepoint(event.pos) and boutique.admin:
                    boutique.sortir_admin()
                    index = skins.index(boutique.equipe)
                    message = "Player mode"
                    continue
                if back.collidepoint(event.pos):
                    return
                if left.hit(event.pos):
                    direction = -1
                elif right.hit(event.pos):
                    direction = 1
                elif equip.collidepoint(event.pos):
                    boutique.equiper(skins[index])
                    message = ""
                elif buy.collidepoint(event.pos):
                    message = boutique.acheter(skins[index])
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if editing:
                        code = ""
                        editing = False
                        continue
                    return
                if editing:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        message = boutique.debloquer(code)
                        editing = False
                        code = ""
                    elif event.key == pygame.K_BACKSPACE:
                        code = code[:-1]
                    elif event.unicode.isprintable() and len(code) < 16:
                        code += event.unicode
                elif event.key == pygame.K_a and not boutique.admin:
                    editing = True
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    direction = -1 if event.key == pygame.K_LEFT else 1
            if direction:
                index = (index + direction) % len(skins)
                message = ""
        clock.tick(60)
