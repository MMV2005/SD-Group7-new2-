"""BonusSpawner : gestion des bonus et de leurs effets."""
import random
import pygame
from settings import BONUS_DEFINITIONS, WINDOWWIDTH, CEILING, FLOOR, POT_REQUIRED
from sprite_assets import load_frames

class BonusSpawner:
    # bonus.1 : Charger uniquement les définitions actives avec le chargeur commun.
    def __init__(self):
        self.definitions = {k: d for k, d in BONUS_DEFINITIONS.items() if d['enabled']}
        self.images = {}
        self.masks = {}
        for kind, definition in self.definitions.items():
            if definition['effect'] not in ('count', 'coin_multiplier', 'shield'):
                raise ValueError(f"Effet de bonus inconnu : {definition['effect']}")
            self.images[kind] = load_frames([definition['file']], definition['size'])[0]
            self.masks[kind] = pygame.mask.from_surface(self.images[kind])
        self.reset()

    # bonus.2 : Nouvelle partie : objets, compteurs et effets remis à zéro.
    def reset(self):
        self.counts = {kind: 0 for kind in self.definitions}
        self.active = {}
        self.clear()

    # bonus.3 : Transition : enlever les objets, conserver les acquisitions/effets.
    def clear(self):
        self.items = []
        self.timers = {k: random.uniform(*d['interval']) for k, d in self.definitions.items()}

    @property
    def pots(self):
        return self.counts.get('pot', 0)

    @property
    def ready(self):
        return self.pots >= POT_REQUIRED

    def consume_pots(self):
        self.counts['pot'] = 0

    # bonus.4 : Effets génériques. Nouvelle collecte = durée renouvelée.
    def collect(self, kind):
        definition = self.definitions[kind]
        limit = definition.get('limit')
        count = self.counts[kind] + 1
        self.counts[kind] = min(count, limit) if limit is not None else count
        if definition['effect'] != 'count':
            self.active[kind] = definition['duration']

    @property
    def coin_multiplier(self):
        return max([1] + [self.definitions[k].get('value', 1)
                          for k in self.active
                          if self.definitions[k]['effect'] == 'coin_multiplier'])

    @property
    def invincible(self):
        return any(self.definitions[k]['effect'] == 'shield' for k in self.active)

    @property
    def clover_state(self):
        if 'clover' in self.active:
            return 'trouve'
        return 'utilise' if self.counts.get('clover', 0) else 'a_trouver'

    # bonus.5 : Apparitions indépendantes des obstacles ; éviter les recouvrements initiaux.
    def spawn(self, kind, hazards):
        image = self.images[kind]
        margin = image.get_height() // 2 + 12
        for _ in range(8):
            rect = image.get_rect(center=(WINDOWWIDTH + 50,
                random.randint(CEILING + margin, FLOOR - margin)))
            occupied = [h.rect for h in hazards] + [i['rect'] for i in self.items]
            if not any(rect.colliderect(r.inflate(16, 16)) for r in occupied):
                self.items.append({'kind': kind, 'rect': rect, 'x': float(rect.centerx)})
                return True
        return False

    # bonus.6 : Mise à jour en secondes ; ne pas appeler pendant pause/transition.
    def update(self, player_rect, player_mask, speed, hazards, dt, world, blocked=False):
        self.active = {k: remaining - dt for k, remaining in self.active.items()
                       if remaining > dt}
        if not blocked:
            for kind, definition in self.definitions.items():
                if world not in definition['worlds']:
                    continue
                limit = definition.get('limit')
                if limit is not None and self.counts[kind] >= limit:
                    continue
                self.timers[kind] = max(0.0, self.timers[kind] - dt)
                if self.timers[kind] <= 0 and not any(i['kind'] == kind for i in self.items):
                    self.timers[kind] = (random.uniform(*definition['interval'])
                                        if self.spawn(kind, hazards) else 0.5)
        collected = []
        for item in self.items[:]:
            item['x'] -= speed * dt
            rect = item['rect']
            rect.centerx = round(item['x'])
            offset = (rect.x - player_rect.x, rect.y - player_rect.y)
            if (rect.colliderect(player_rect)
                    and player_mask.overlap(self.masks[item['kind']], offset) is not None):
                self.collect(item['kind'])
                collected.append(item['kind'])
                self.items.remove(item)
            elif rect.right < 0:
                self.items.remove(item)
        return collected

    # bonus.7 : Dessin de tous les objets avec la même méthode.
    def draw(self, screen):
        for item in self.items:
            screen.blit(self.images[item['kind']], item['rect'])