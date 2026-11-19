import pygame

from menu import FONTS_DIR, draw_text, load_image    

def show_game_over(window, score, high_score):
    """Display a game-over panel over the frozen game."""

    clock = pygame.time.Clock()
    center_x, center_y = window.get_rect().center

    # Keep the last game frame behind the panel.
    frozen_game = window.copy()

    # Darken the game behind the panel.
    overlay = pygame.Surface(window.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))

    # Load the panel and buttons.
    panel = load_image("wooden_frame", (600, 310))
    replay_image = load_image("green_button", (220, 48))
    menu_image = load_image("wooden_button", (220, 48))

    panel_rect = panel.get_rect(center=(center_x, center_y))

    replay_rect = replay_image.get_rect(
        center=(center_x - 120, center_y + 80)
    )
    menu_rect = menu_image.get_rect(
        center=(center_x + 120, center_y + 80)
    )
    title_font = pygame.font.Font(str(FONTS_DIR / "press_start.ttf"), 26)
    score_font = pygame.font.Font(str(FONTS_DIR / "pixelify.ttf"), 24)
    button_font = pygame.font.Font(str(FONTS_DIR / "tiny5_duo.ttf"), 24)

    previous_cursor_visibility = pygame.mouse.get_visible()
    pygame.mouse.set_visible(True)

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return "replay"
                    if event.key == pygame.K_ESCAPE:
                        return "menu"

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if replay_rect.collidepoint(event.pos):
                        return "replay"
                    if menu_rect.collidepoint(event.pos):
                        return "menu"

            # Restore the frozen game before drawing the panel.
            window.blit(frozen_game, (0, 0))
            window.blit(overlay, (0, 0))
            window.blit(panel, panel_rect)

            draw_text(window, "GAME OVER", (center_x, center_y - 80), title_font)
            draw_text(window, f"SCORE: {score}", (center_x, center_y - 20), score_font)
            draw_text(
                window,
                f"HIGH SCORE: {high_score}",
                (center_x, center_y + 15),
                score_font,
            )

            window.blit(replay_image, replay_rect)
            window.blit(menu_image, menu_rect)

            draw_text(window, "REPLAY", replay_rect.center, button_font)
            draw_text(window, "MENU", menu_rect.center, button_font)

            pygame.display.flip()
            clock.tick(60)

    finally:
        if pygame.display.get_init():
            pygame.mouse.set_visible(previous_cursor_visibility)