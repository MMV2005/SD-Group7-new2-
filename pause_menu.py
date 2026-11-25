import pygame

from menu import FONTS_DIR, draw_text, load_image


# --- Réglages de la mise en page -------------------------------------------
# Positions et largeurs en FRACTIONS du panneau visible
# (0.0 = bord haut/gauche, 1.0 = bord bas/droit).
TITLE_Y = 0.287           # centre du titre (inclut une compensation de la police)
RESUME_Y = 0.50           # centre du bouton RESUME
BOTTOM_Y = 0.754          # centre de la rangée RESTART / MAIN MENU
RESUME_WIDTH = 0.5       # largeur visible du bouton RESUME
BOTTOM_WIDTH = 0.32       # largeur visible de chacun des deux boutons du bas
BOTTOM_GAP = 0.03         # écart horizontal entre les deux boutons du bas

# Tailles de police
TITLE_SIZE = 28
RESUME_FONT_SIZE = 30
BOTTOM_FONT_SIZE = 22


def crop_visible(image):
    """Retire les marges transparentes d'une image.

    get_bounding_rect() donne le plus petit rectangle qui contient les pixels
    non transparents (alpha >= 100). On découpe l'image à cette taille, ce qui
    permet de positionner et dimensionner ce qui est réellement visible.
    """
    return image.subsurface(image.get_bounding_rect(min_alpha=100)).copy()


def fit_width(image, width):
    """Redimensionne une image à une largeur donnée en gardant ses proportions."""
    ratio = image.get_height() / image.get_width()
    return pygame.transform.scale(image, (int(width), int(width * ratio)))


def show_pause(window):
    """Affiche le menu pause par-dessus le jeu figé.

    Retourne "resume", "restart" ou "menu".
    """

    clock = pygame.time.Clock()
    center_x, center_y = window.get_rect().center

    # La fenêtre contient encore la dernière image du jeu : on la garde en fond.
    frozen_game = window.copy()

    # Voile sombre par-dessus le jeu.
    overlay = pygame.Surface(window.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))

    # Panneau rogné à sa partie visible, puis centré à l'écran.
    panel = crop_visible(load_image("wooden_frame", (600, 310)))
    panel_rect = panel.get_rect(center=(center_x, center_y))
    pw, ph = panel_rect.size

    # Boutons rognés à leur partie visible, puis mis à la largeur voulue.
    green_base = crop_visible(load_image("green_button", (260, 48)))
    wooden_base = crop_visible(load_image("wooden_button", (260, 48)))

    resume_image = fit_width(green_base, RESUME_WIDTH * pw)
    restart_image = fit_width(wooden_base, BOTTOM_WIDTH * pw)
    menu_image = fit_width(wooden_base, BOTTOM_WIDTH * pw)

    # Polices (créées avant les entrées, car chaque entrée garde la sienne).
    title_font = pygame.font.Font(str(FONTS_DIR / "press_start.ttf"), TITLE_SIZE)
    resume_font = pygame.font.Font(str(FONTS_DIR / "tiny5_duo.ttf"), RESUME_FONT_SIZE)
    bottom_font = pygame.font.Font(str(FONTS_DIR / "tiny5_duo.ttf"), BOTTOM_FONT_SIZE)

    # Décalage horizontal du centre de chaque bouton du bas par rapport
    # au centre du panneau : la moitié de (largeur d'un bouton + écart).
    side_offset = (BOTTOM_WIDTH + BOTTOM_GAP) / 2 * pw

    resume_y = panel_rect.top + RESUME_Y * ph
    bottom_y = panel_rect.top + BOTTOM_Y * ph

    # Chaque entrée : (texte, valeur retournée, image, rectangle, police).
    entries = [
        ("RESUME", "resume", resume_image,
         resume_image.get_rect(center=(panel_rect.centerx, resume_y)),
         resume_font),
        ("RESTART", "restart", restart_image,
         restart_image.get_rect(center=(panel_rect.centerx - side_offset, bottom_y)),
         bottom_font),
        ("MENU", "menu", menu_image,
         menu_image.get_rect(center=(panel_rect.centerx + side_offset, bottom_y)),
         bottom_font),
    ]

    previous_cursor_visibility = pygame.mouse.get_visible()
    pygame.mouse.set_visible(True)

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                # Raccourcis clavier : P, ECHAP ou ENTREE reprennent la partie.
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_p, pygame.K_ESCAPE, pygame.K_RETURN):
                        return "resume"

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for _, action, _, rect, _ in entries:
                        if rect.collidepoint(event.pos):
                            return action

            # Redessiner le jeu figé, puis le voile et le panneau.
            window.blit(frozen_game, (0, 0))
            window.blit(overlay, (0, 0))
            window.blit(panel, panel_rect)

            # Titre dans le cadre, positionné par rapport au panneau.
            draw_text(
                window,
                "PAUSE",
                (panel_rect.centerx, panel_rect.top + TITLE_Y * ph),
                title_font,
            )

            for label, _, image, rect, font in entries:
                window.blit(image, rect)
                draw_text(window, label, rect.center, font)

            pygame.display.flip()
            clock.tick(60)

    finally:
        if pygame.display.get_init():
            pygame.mouse.set_visible(previous_cursor_visibility)