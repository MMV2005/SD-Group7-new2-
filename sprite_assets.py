"""Chargement commun des obstacles et des bonus."""
import pygame
from pathlib import Path

# sprites.1 : Trouver une image, en privilégiant le PNG.
def resolve_image_path(path):
    path = Path(path)
    extensions = ('.png', '.jpg', '.jpeg')

    if path.parent.is_dir():
        matches = [
            file
            for file in path.parent.iterdir()
            if file.is_file() and file.stem.casefold() == path.stem.casefold() and file.suffix.casefold() in extensions]

        for extension in extensions:
            candidates = [file for file in matches if file.suffix.casefold() == extension]

            if len(candidates) == 1:
                return candidates[0]

            if len(candidates) > 1:
                exact = path.with_suffix(extension)

                if exact in candidates:
                    return exact

                raise ValueError( f"Plusieurs images correspondent à {path}: "f"{candidates}")

    tried = ', '.join(path.stem + extension for extension in extensions)

    raise FileNotFoundError(f"Image introuvable dans {path.parent.resolve()} : "f"{tried}. Vérifie le dossier et le nom avant l'extension.")


# Charger le fichier trouvé par la méthode précédente.
def load_image(path):
    return pygame.image.load(
        str(resolve_image_path(path))
    )

# sprites.2 : Même boîte maximale et même échelle pour toutes les poses.
def load_frames(paths, max_size, trim=True):
    sources = []
    for path in paths:
        image = load_image(path).convert_alpha()
        if trim:
            bounds = image.get_bounding_rect(min_alpha=20)
            if not bounds.width or not bounds.height:
                raise ValueError(f"Image vide : {path}")
            image = image.subsurface(bounds).copy()
        sources.append(image)
    width = max(s.get_width() for s in sources)
    height = max(s.get_height() for s in sources)
    ratio = min(max_size[0] / width, max_size[1] / height)
    canvas_size = (max(1, round(width * ratio)), max(1, round(height * ratio)))
    frames = []
    for source in sources:
        size = (max(1, round(source.get_width() * ratio)),
                max(1, round(source.get_height() * ratio)))
        image = pygame.transform.scale(source, size)
        canvas = pygame.Surface(canvas_size, pygame.SRCALPHA)
        canvas.blit(image, image.get_rect(center=(canvas_size[0] // 2, canvas_size[1] // 2)))
        frames.append(canvas)
    return frames