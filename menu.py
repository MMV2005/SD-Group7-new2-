import pygame
from pathlib import Path
from collections import deque
from functools import lru_cache
from sprite_assets import resolve_image_path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
MENU_ASSETS_DIR = ASSETS_DIR / "menu"
FONTS_DIR = ASSETS_DIR / "fonts"

def crop_transparent_margins(image):
    bounds = image.get_bounding_rect()
    if bounds.width and bounds.height:
        return image.subsurface(bounds).copy()
    return image


def scale_image(image, factor):
    width = max(1, round(image.get_width() * factor))
    height = max(1, round(image.get_height() * factor))
    return pygame.transform.scale(image, (width, height))


def remove_outer_black_background(image):
    # Limit the number of pixels to examine.
    factor = min(1, 800 / max(image.get_size()))
    image = scale_image(image, factor)
    width, height = image.get_size()

    # Start from all four edges of the image.
    pixels = deque()
    for x in range(width):
        pixels.append((x, 0))
        pixels.append((x, height - 1))
    for y in range(height):
        pixels.append((0, y))
        pixels.append((width - 1, y))

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
            pixels.extend((
                (x - 1, y),
                (x + 1, y),
                (x, y - 1),
                (x, y + 1),
            ))

    return crop_transparent_margins(image)


@lru_cache(maxsize=32)
def load_image(name, size, remove_black=False):
    """Load an image and fit it inside the requested area."""
    path = resolve_image_path(MENU_ASSETS_DIR / f"{name}.png")
    image = pygame.image.load(str(path)).convert_alpha()
    image = crop_transparent_margins(image)

    if remove_black:
        image = remove_outer_black_background(image)

    target_width, target_height = size
    factor = min(
        target_width / image.get_width(),
        target_height / image.get_height(),
    )
    image = scale_image(image, factor)

    result = pygame.Surface(size, pygame.SRCALPHA)
    result.blit(image, image.get_rect(center=result.get_rect().center))
    return result


def draw_text(window, message, center, font):
    rendered_text = font.render(str(message), True, (255, 245, 220))
    window.blit(rendered_text, rendered_text.get_rect(center=center))


def show_menu(window, high_score=0, last_score=None,
              sound_enabled=True, coins=0):
    """Display the menu in a 960 × 540 window."""

    clock = pygame.time.Clock()

    font = pygame.font.Font(str(FONTS_DIR / "pixelify.ttf"), 22)
    title_font = pygame.font.Font(str(FONTS_DIR / "press_start.ttf"), 20)
    button_font = pygame.font.Font(str(FONTS_DIR / "tiny5_duo.ttf"), 24)
    small_button_font = pygame.font.Font(str(FONTS_DIR / "tiny5_duo.ttf"), 14)

    background = load_image("background", (960, 540))
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


    def draw_button(message, rectangle, image):
        window.blit(image, rectangle)

        # Use smaller text for the rules and sound buttons.
        selected_font = (
            small_button_font
            if message == "RULES AND CONTROLS"
            or message.startswith("SOUND:")
            else button_font
        )

        draw_text(window, message, rectangle.center, selected_font)
        
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
            draw_text(window, "LEPRECHAUN", (480, 125), title_font)
            draw_text(window, "ESCAPE", (480, 155), title_font)
            # Draw the wooden panel behind the coin counter.
            window.blit(coin_panel, (15, 10))

            # Draw the chest icon and coin count over the panel.
            window.blit(chest, (20, 10))
            draw_text(window, f"CHEST: {coins}", (160, 37), button_font)

            if page == "home":
                for label, rectangle in buttons:
                    draw_button(
                        label,
                        rectangle,
                        green_button if label == "PLAY" else wooden_button
                    )

                if last_score is not None:
                    draw_text(
                        window,
                        f"LAST SCORE: {last_score}",
                        (window.get_width() // 2, 510),
                        button_font,
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
                    draw_text(window, line, (480, 255 + index * 36), font)

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