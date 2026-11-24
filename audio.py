"""Gestion des musiques et effets du jeu via pygame.mixer."""

import pygame

from reglages_audio import (
    MUSIC_DIR,
    MUSIC_FOLDERS,
    MUSIC_FILES,
    MUSIC_EXTENSIONS,
    MUSIC_VOLUME,
    MUSIC_FADE_IN_MS,
    GAMEOVER_SOUND,
    GAMEOVER_VOLUME,
    PICKUP_SOUND,
    PICKUP_VOLUME,
    PICKUP_COOLDOWN_MS,
)


class Audio:
    def __init__(self):
        # À construire après pygame.init().
        self.enabled = True
        self.current_track = None
        self.available = pygame.mixer.get_init() is not None
        self.game_over_sound = None
        self.pickup_sound = None
        self.last_pickup_time = -PICKUP_COOLDOWN_MS

        if not self.available:
            print("[Audio] Mixeur indisponible : jeu sans son.")
            return

        self.game_over_sound = self._load_sound(GAMEOVER_SOUND)
        self.pickup_sound = self._load_sound(PICKUP_SOUND)
        self.set_enabled(True)

    @staticmethod
    def _load_sound(path):
        """Charge un effet sonore sans faire planter le jeu s'il manque."""
        if not path.is_file():
            print(f"[Audio] Son introuvable : {path}")
            return None

        try:
            return pygame.mixer.Sound(str(path))
        except (pygame.error, OSError) as exc:
            print(f"[Audio] Impossible de charger {path.name} : {exc}")
            return None

    @staticmethod
    def _find_music(world):
        """Retourne la musique choisie ou la première du dossier."""
        directory_name = MUSIC_FOLDERS.get(world)
        if directory_name is None:
            raise ValueError(f"Monde audio inconnu : {world!r}")

        folder = MUSIC_DIR / directory_name
        chosen_name = MUSIC_FILES.get(world)

        if chosen_name:
            path = folder / chosen_name
            return path if path.is_file() else None

        if not folder.is_dir():
            return None

        candidates = sorted(
            (
                path for path in folder.iterdir()
                if path.is_file()
                and path.suffix.lower() in MUSIC_EXTENSIONS
            ),
            key=lambda path: path.name.lower(),
        )
        return candidates[0] if candidates else None

    def set_enabled(self, enabled):
        """Applique SOUND ON/OFF à la musique et aux effets."""
        self.enabled = bool(enabled)
        if not self.available:
            return

        pygame.mixer.music.set_volume(
            MUSIC_VOLUME if self.enabled else 0.0
        )
        if self.game_over_sound is not None:
            self.game_over_sound.set_volume(
                GAMEOVER_VOLUME if self.enabled else 0.0
            )
        if self.pickup_sound is not None:
            self.pickup_sound.set_volume(
                PICKUP_VOLUME if self.enabled else 0.0
            )

    def play(self, world):
        """Lance en boucle la musique d'un monde, si elle existe."""
        if not self.available or world == self.current_track:
            return

        path = self._find_music(world)
        if path is None:
            self.stop_music()
            print(f"[Audio] Aucune musique trouvée pour {world!r}.")
            return

        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(
                MUSIC_VOLUME if self.enabled else 0.0
            )
            pygame.mixer.music.play(-1, fade_ms=MUSIC_FADE_IN_MS)
            self.current_track = world
        except (pygame.error, OSError) as exc:
            self.stop_music()
            print(f"[Audio] Impossible de jouer {path.name} : {exc}")

    def pause(self):
        if self.available:
            pygame.mixer.music.pause()

    def unpause(self):
        if self.available:
            pygame.mixer.music.unpause()

    def stop_music(self):
        if self.available:
            pygame.mixer.music.stop()
        self.current_track = None

    def stop_game_over(self):
        if self.game_over_sound is not None:
            self.game_over_sound.stop()

    def play_game_over(self):
        self.stop_music()
        if self.game_over_sound is not None and self.enabled:
            self.game_over_sound.play()

    def play_pickup(self):
        """Joue un son quand au moins une pièce est récupérée."""
        if not self.available or not self.enabled:
            return
        if self.pickup_sound is None:
            return

        now = pygame.time.get_ticks()
        if now - self.last_pickup_time < PICKUP_COOLDOWN_MS:
            return

        self.pickup_sound.play()
        self.last_pickup_time = now

