import pygame
from pathlib import Path
from collections import deque
from functools import lru_cache

MENU_ASSETS_DIR = Path(__file__).resolve().parent / "assets" / "menu"

@lru_cache(maxsize=32)
def load_image(name, size, remove_black=False):
    """Load an image and resize it without stretching it."""

    path = next(
        (MENU_ASSETS_DIR / (name + extension)
         for extension in (".png", ".jpg", ".jpeg")
         if (MENU_ASSETS_DIR / (name + extension)).exists()),
        None
    )

    if path is None:
        raise FileNotFoundError(
            f"Missing image in {MENU_ASSETS_DIR}: {name}"
        )

    image = pygame.image.load(str(path)).convert_alpha()

    # Crop transparent margins before resizing the image.
    bounds = image.get_bounding_rect()
    if bounds.width and bounds.height:
        image = image.subsurface(bounds).copy()

    if remove_black:
        # Reduce large images to speed up background removal.
        scale_factor = min(1, 800 / max(image.get_size()))
        image = pygame.transform.scale(image, (
            max(1, round(image.get_width() * scale_factor)),
            max(1, round(image.get_height() * scale_factor))
        ))

        # Remove the outer black background without erasing inner details.
        width, height = image.get_size()
        pixels = deque(
            [(x, y) for x in range(width) for y in (0, height - 1)]
            + [(x, y) for y in range(height) for x in (0, width - 1)]
        )
        visited = set()

        while pixels:
            x, y = pixels.popleft()
            if not (0 <= x < width and 0 <= y < height):
                continue
            if (x, y) in visited:
                continue
            visited.add((x, y))

            red, green, blue, alpha = image.get_at((x, y))
            if alpha == 0 or max(red, green, blue) <= 18:
                image.set_at((x, y), (0, 0, 0, 0))
                pixels.extend(((x - 1, y), (x + 1, y),
                               (x, y - 1), (x, y + 1)))

        bounds = image.get_bounding_rect()
        if bounds.width and bounds.height:
            image = image.subsurface(bounds).copy()

    # Use the same scale factor for both dimensions to avoid distortion.
    scale_factor = min(size[0] / image.get_width(),
                       size[1] / image.get_height())
    image = pygame.transform.scale(image, (
        max(1, round(image.get_width() * scale_factor)),
        max(1, round(image.get_height() * scale_factor))
    ))

    # Center the image within the requested area.
    result = pygame.Surface(size, pygame.SRCALPHA)
    result.blit(image, image.get_rect(
        center=(size[0] // 2, size[1] // 2)))
    return result


def show_menu(window, high_score=0, last_score=None,
              sound_enabled=True, coins=0):
    """Display the menu in a 960 × 540 window."""

    clock = pygame.time.Clock()

    # Locate the folder containing the font files.
    fonts_dir = Path(__file__).resolve().parent / "assets" / "fonts"

    # Use Pixelify Sans for rules, scores, and the coin counter.
    font = pygame.font.Font(
        str(fonts_dir / "pixelify.ttf"), 22
    )

    # Use Press Start 2P for the game title.
    title_font = pygame.font.Font(
        str(fonts_dir / "press_start.ttf"), 20
    )

    # Use Tiny5 Duo for all buttons.
    button_font = pygame.font.Font(
        str(fonts_dir / "tiny5_duo.ttf"), 24
    )
    small_button_font = pygame.font.Font(
        str(fonts_dir / "tiny5_duo.ttf"), 14
    )

    background = load_image("background", (960, 540), False)
    title = load_image("title", (540, 170))
    green_button = load_image("green_button", (350, 54))
    wooden_button = load_image("wooden_button", (350, 54))
    small_button = load_image("wooden_button", (180, 38))
    chest = load_image("chest", (55, 55))
    coin_panel = load_image("wooden_button", (240, 54))

    # Darken the background to make the text easier to read.
    overlay = pygame.Surface((960, 540), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 110))

    buttons = [
        ("PLAY", pygame.Rect(305, 235, 350, 54)),
        ("HIGH SCORE", pygame.Rect(305, 298, 350, 54)),
        ("RULES AND CONTROLS", pygame.Rect(305, 361, 350, 54)),
        ("SHOP", pygame.Rect(305, 424, 350, 54))
    ]
    back_button_rect = pygame.Rect(305, 424, 350, 54)
    sound_button_rect = pygame.Rect(20, 490, 180, 38)
    page = "home"

    def draw_text(message, center, text_font=font):
        rendered_text = text_font.render(
            str(message), True, (255, 245, 220)
        )
        window.blit(rendered_text, rendered_text.get_rect(center=center))

    def draw_button(message, rectangle, image):
        window.blit(image, rectangle)

        # Use smaller text for the rules and sound buttons.
        selected_font = (
            small_button_font
            if message == "RULES AND CONTROLS"
            or message.startswith("SOUND:")
            else button_font
        )

        draw_text(message, rectangle.center, selected_font)

    previous_cursor_visibility = pygame.mouse.get_visible()
    pygame.mouse.set_visible(True)

    try:
        while True:
            # Handle mouse clicks and key presses.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if page == "home":
                            pygame.quit()
                            raise SystemExit
                        page = "home"

                    if event.key == pygame.K_RETURN and page == "home":
                        return sound_enabled

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if sound_button_rect.collidepoint(event.pos):
                        sound_enabled = not sound_enabled
                        if pygame.mixer.get_init():
                            pygame.mixer.music.set_volume(
                                1.0 if sound_enabled else 0.0
                            )

                    elif page == "home":
                        for label, rectangle in buttons:
                            if rectangle.collidepoint(event.pos):
                                if label == "PLAY":
                                    return sound_enabled
                                page = label
                                break

                    elif back_button_rect.collidepoint(event.pos):
                        page = "home"

            # Draw the background and title.
            window.fill((0, 0, 0))
            window.blit(background, (0, 0))
            window.blit(overlay, (0, 0))
            window.blit(title, (210, 40))
            draw_text("LEPRECHAUN", (480, 125), title_font)
            draw_text("ESCAPE", (480, 155), title_font)
            # Draw the wooden panel behind the coin counter.
            window.blit(coin_panel, (15, 10))

            # Draw the chest icon and coin count over the panel.
            window.blit(chest, (20, 10))
            draw_text(f"CHEST: {coins}", (160, 37), button_font)

            if page == "home":
                for label, rectangle in buttons:
                    draw_button(
                        label,
                        rectangle,
                        green_button if label == "PLAY" else wooden_button
                    )

                if last_score is not None:
                    draw_text(
                        f"LAST SCORE: {last_score}",
                        (window.get_width() // 2, 510),
                        button_font
                    )

            else:
                pygame.draw.rect(
                    window, (45, 25, 15), (220, 225, 520, 185)
                )

                if page == "HIGH SCORE":
                    lines = [
                        "HIGH SCORE",
                        f"{high_score} points",
                        "Best score this session."
                    ]
                elif page == "RULES AND CONTROLS":
                    lines = [
                        "Avoid the obstacles.",
                        "Hold SPACE to move up.",
                        "Release SPACE to move down.",
                        "Press ESC during the game to quit."
                    ]
                else:
                    lines = [
                        "SHOP",
                        "Coming soon: no purchases available yet."
                    ]

                for index, line in enumerate(lines):
                    draw_text(line, (480, 255 + index * 36))

                draw_button("BACK", back_button_rect, wooden_button)

            draw_button(
                "SOUND: " + ("ON" if sound_enabled else "OFF"),
                sound_button_rect,
                small_button
            )
            pygame.display.flip()
            clock.tick(60)

    finally:
        if pygame.display.get_init():
            pygame.mouse.set_visible(previous_cursor_visibility)