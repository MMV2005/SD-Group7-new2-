"""audio.py : chargement des musiques, volume, pause et son de game over.

Toutes les options modifiables se trouvent dans reglages_audio.py.
Le jeu appelle seulement les methodes de la classe Audio.
"""
from pathlib import Path
import pygame

from reglages_audio import (
    MUSIC_DIR, MUSIC_TRACKS, MUSIC_VOLUME, GAMEOVER_VOLUME,
    MUSIC_FADE_IN_MS, FALLBACK_MUSIC, GAMEOVER_SOUND,
)


class Audio:
    def __init__(self, enabled=True):
        # Initialiser cette classe apres pygame.init().
        self.enabled = bool(enabled)
        self.current_file = None
        self.paused = False
        self._already_warned = set()
        self.game_over_sound = pygame.mixer.Sound(str(GAMEOVER_SOUND))
        self.set_enabled(enabled)

    def _warn_once(self, message):
        if message not in self._already_warned:
            print("[Audio] " + message)
            self._already_warned.add(message)

    def _music_path(self, place):
        """Selectionne la piste de menu/meadow/pub/cave/gold."""
        if place not in MUSIC_TRACKS:
            raise ValueError(f"Musique non configuree pour {place!r}")

        filename = MUSIC_TRACKS[place]
        if filename:
            path = Path(filename)
            if not path.is_absolute():
                path = MUSIC_DIR / path
            if path.is_file():
                return path

        if FALLBACK_MUSIC is not None:
            fallback = Path(FALLBACK_MUSIC)
            if fallback.is_file():
                self._warn_once(f"Musique {place!r} introuvable ; utilisation de background.mid")
                return fallback

        self._warn_once(f"Aucune musique trouvee pour {place!r} dans assets/music/")
        return None

    def set_enabled(self, enabled):
        """SOUND ON/OFF : conserve la position de la musique."""
        self.enabled = bool(enabled)
        pygame.mixer.music.set_volume(MUSIC_VOLUME if self.enabled else 0.0)
        self.game_over_sound.set_volume(GAMEOVER_VOLUME if self.enabled else 0.0)

    def play(self, place):
        """Change de musique seulement si la piste est differente, puis boucle."""
        path = self._music_path(place)
        self.game_over_sound.stop()

        # Ne pas redemarrer le meme fichier si on est toujours en train de le jouer.
        if path is not None and path == self.current_file:
            if self.paused:
                self.unpause()
                return
            if pygame.mixer.music.get_busy():
                return

        pygame.mixer.music.stop()
        self.current_file = None
        self.paused = False
        if path is None:
            return

        try:
            pygame.mixer.music.load(str(path))
            self.set_enabled(self.enabled)
            pygame.mixer.music.play(loops=-1, fade_ms=MUSIC_FADE_IN_MS)
        except (pygame.error, OSError) as error:
            self._warn_once(f"Impossible de lire {path.name}: {error}")
            return

        self.current_file = path

    def pause(self):
        """Fige la musique sans revenir au debut."""
        if not self.paused:
            pygame.mixer.music.pause()
            self.paused = True

    def unpause(self):
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False

    def stop(self):
        pygame.mixer.music.stop()
        self.current_file = None
        self.paused = False

    def game_over(self):
        """Arrete la musique du monde et joue le son de defaite."""
        self.stop()
        self.game_over_sound.play()
