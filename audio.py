
"""Gestion des musiques du menu, des mondes, de la pause et du game over."""

import pygame

from reglages_audio import (
    MUSIC_DIR,
    MUSIC_FOLDERS,
    MUSIC_FILES,
    MUSIC_EXTENSIONS,
    MUSIC_VOLUME,
    GAMEOVER_VOLUME,
    MUSIC_FADE_IN_MS,
    GAMEOVER_SOUND,
)


class Audio:
    def __init__(self):
        # pygame.init() doit être appelé avant Audio().
        self.enabled = True
        self.current_track = None
        self.available = pygame.mixer.get_init() is not None
        self.game_over_sound = None

        if not self.available:
            print("[Audio] Mixeur indisponible : le jeu fonctionnera sans son.")
            return

        if GAMEOVER_SOUND.is_file():
            try:
                self.game_over_sound = pygame.mixer.Sound(
                    str(GAMEOVER_SOUND)
                )
            except (pygame.error, OSError) as exc:
                print(f"[Audio] Game over non chargé : {exc}")
        else:
            print(
                f"[Audio] Son de game over introuvable : {GAMEOVER_SOUND}"
            )

        self.set_enabled(True)

    @staticmethod
    def _find_music(world):
        """Trouve le morceau d'un monde dans son dossier."""
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
        """Coupe ou active le son sans arrêter la lecture."""
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

    def play(self, world):
        """Change la musique et la lit en boucle."""
        if not self.available or world == self.current_track:
            return

        path = self._find_music(world)

        if path is None:
            self.stop_music()
            print(
                f"[Audio] Aucune musique trouvée pour {world!r} dans "
                f"{MUSIC_DIR / MUSIC_FOLDERS[world]}"
            )
            return

        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(
                MUSIC_VOLUME if self.enabled else 0.0
            )
            pygame.mixer.music.play(
                -1,
                fade_ms=MUSIC_FADE_IN_MS
            )
            self.current_track = world

        except (pygame.error, OSError) as exc:
            self.stop_music()
            print(
                f"[Audio] Impossible de jouer {path.name} : {exc}"
            )

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

        if self.game_over_sound is not None:
            self.game_over_sound.play()
