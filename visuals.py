"""Visuals - player 3-frame animation, loaded when Visuals() is created."""
import pygame, math, random
from settings import *
from reglages_personnages import *
from transitions import draw_fog
from sprite_assets import load_frames, load_image

PLAYER_FRAMES_FOLDER = ASSETS / 'Skins' / 'classic'

#--- fonds (un par monde) ---
BACKGROUND_FOLDER = ASSETS / 'world'
# y de la ligne du sol dans chaque image SOURCE (pixels).
BACKGROUND_HORIZONS = {'meadow': 800, 'pub': 830, 'cave': 805, 'gold': 755}
GOOSE_FRAMES_FOLDER = ASSETS / 'goose'
ANIMATION_FPS = 9           # Number of frames per second for the player animation (FPS).

# --- AJOUT : portail ---
PORTAL_FILE = ASSETS / 'transition' / 'portal.png'
PORTAL_SIZE = (210, 425)              # taille du portail à l'écran


class Visuals:
    def __init__(self):
        self.frames = [
            load_image(str(PLAYER_FRAMES_FOLDER / f'vol_{i}.png')).convert_alpha()
            for i in range(3)]
        
        self.masks = [pygame.mask.from_surface(frame) for frame in self.frames]

        #Image and mask of the pose currently displayed. They are refreshed
        # by update_pose(), which must be called once per game loop turn.
        self.image = self.frames[0]
        self.mask = self.masks[0]

        # --- fonds, chargés une seule fois (un par monde) ---
        self.backgrounds = {name: self.load_background(name) for name in BACKGROUND_HORIZONS}

        # --- AJOUT : image du portail, chargée une seule fois ---
        portal = load_image(str(PORTAL_FILE)).convert_alpha()
        portal = portal.subsurface(portal.get_bounding_rect(min_alpha=20))   # enlève les bords transparents
        self.portal_image = pygame.transform.scale(portal, PORTAL_SIZE)


        self.goose_frames = [
            load_image(str(GOOSE_FRAMES_FOLDER / f'goose_{i}.png')).convert_alpha()
            for i in range(2)]
        # Un seul masque fixe (les ailes qui battent ne modifient pas la hitbox)
        self.goose_mask = pygame.mask.from_surface(self.goose_frames[0])

        self.coins = []               # particules actuellement à l'écran
        self.jet_accumulator = 0.0    # reste fractionnaire : JET_RATE / FPS n'est pas entier
        self.load_obstacles()

    def get_rect(self):
        """Return a new rect of the player's size (same for the 3 poses)."""
        return self.frames[0].get_rect()

    def update_pose(self):
        """Choose the current pose from the elapsed time."""
        # get_ticks() = milliseconds since pygame.init(); /1000 -> seconds.
        elapsed_seconds = pygame.time.get_ticks() / 1000
        # elapsed_seconds * ANIMATION_FPS = number of animation steps so far.
        # int() keeps the whole part, so the pose only changes every
        # 1 / ANIMATION_FPS seconds.
        step = int(elapsed_seconds * ANIMATION_FPS)
        # The modulo makes the sequence loop forever and keeps the index
        # inside the list.
        index = FRAME_SEQUENCE[step % len(FRAME_SEQUENCE)]
        self.image = self.frames[index]
        self.mask = self.masks[index]

    @staticmethod
    def load_background(world):
        """Load the image once, then align its ground line on FLOOR."""
        source = load_image(str(BACKGROUND_FOLDER / f'bg_{world}.png')).convert()
        w, h = source.get_size()
        horizon = BACKGROUND_HORIZONS[world]

        # Cut the source in two at the horizon: landscape above, soil below.
        top = source.subsurface((0, 0, w, horizon))
        bottom = source.subsurface((0, horizon, w, h - horizon))

        # Stretch each part so the horizon lands exactly on FLOOR.
        background = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))
        background.blit(pygame.transform.scale(top, (WINDOWWIDTH, FLOOR)), (0, 0))
        background.blit(pygame.transform.scale(bottom, (WINDOWWIDTH, WINDOWHEIGHT - FLOOR)), (0, FLOOR))
        return background

    def draw_background(self, screen, world='meadow'):
        """Draw the background of the given world. Must be called BEFORE anything else each frame."""
        screen.blit(self.backgrounds[world], (0, 0))

    # visuals.5 : Portails des mondes normaux uniquement.
    def draw_portal(self, screen, portal_x):
        draw_fog(screen, portal_x - 20)
        screen.blit(self.portal_image, self.portal_image.get_rect(
            center=(round(portal_x + 26), 282)))


    def reset_jet(self):
        """Vide le jet : à appeler au début de chaque partie."""
        self.coins = []
        self.jet_accumulator = 0.0

    def update_jet(self, player_rect, thrusting):
        """Crée et fait avancer les pièces : à appeler une fois par image."""
        dt = 1 / FPS    # pas de temps fixe (FPS vient de settings)

        # Création : JET_RATE pièces par seconde, plafonnées à JET_MAX
        if thrusting:
            self.jet_accumulator += JET_RATE * dt
            while self.jet_accumulator >= 1 and len(self.coins) < JET_MAX:
                self.jet_accumulator -= 1
                life = random.uniform(*JET_LIFE)
                self.coins.append({
                    'x': player_rect.left + JET_OFFSET_X,
                    'y': player_rect.centery + player_rect.height * JET_OFFSET_Y,
                    'vx': -random.uniform(*JET_SPEED),    # projetée vers l'arrière
                    'vy': random.uniform(*JET_SPREAD),    # dispersion verticale
                    'life': life, 'initial': life,        # 'initial' sert au rétrécissement
                    'angle': random.uniform(0, math.tau), # phase de rotation aléatoire
                })
            if len(self.coins) >= JET_MAX:
                self.jet_accumulator = 0.0                # évite l'accumulation au plafond

        # Mise à jour physique : intégration d'Euler en secondes
        for c in self.coins:
            c['vy'] += JET_GRAVITY * dt
            c['x'] += c['vx'] * dt
            c['y'] += c['vy'] * dt
            c['angle'] += 24 * dt     # environ 0,4 rad par image à 60 FPS
            c['life'] -= dt

        # Suppression des pièces expirées ou arrivées au sol
        self.coins = [c for c in self.coins if c['life'] > 0 and c['y'] <= FLOOR]

    def draw_jet(self, screen):
        """Dessine les pièces du jet."""
        for c in self.coins:
            # Hauteur proportionnelle à la vie restante : la pièce rétrécit
            h = max(3, round(10 * c['life'] / c['initial']))
            # Largeur en |cos(angle)| : effet de pièce qui tourne sur elle-même
            w = max(2, round(h * abs(math.cos(c['angle']))))
            rect = (round(c['x']), round(c['y']), w, h)
            pygame.draw.ellipse(screen, COIN_FILL, rect)
            pygame.draw.ellipse(screen, COIN_EDGE, rect, 1)

    def draw_player(self, screen, player_rect):
        """Dessine le jet, puis la pose actuelle du joueur."""
        self.draw_jet(screen)                  # d'abord les pièces : elles passent derrière le sprite
        screen.blit(self.image, player_rect)
    
     #Visuals.14 
    def get_goose_rect(self, center_x, center_y): #Return a rect for a new goose centered on (center_x, center_y).
        return self.goose_frames[0].get_rect(center=(center_x, center_y))
    def draw_goose(self, screen, baddie): #Draw goose_0 or goose_1 depending on the goose's age (GOOSE_FPS = 6).
        index = int(baddie['age'] * GOOSE_FPS) % 2
        screen.blit(self.goose_frames[index], baddie['rect'])

    # Charger les images et les masques des obstacles.
    def load_obstacles(self):
        folder = ASSETS / 'obstacles'
        shooters_folder = ASSETS / 'shooters'

        self.obstacle_frames = {}
        self.obstacle_masks = {}

        # visuals.15 : Tous les chemins ici ; toutes les dimensions dans settings.15.
        paths = {
            'barrel': [folder / 'wooden_barrel.png'],
            'mug': [ASSETS / 'bonus' / 'beer_mug.png'],
            'rock_floor': [folder / 'rock_spike_up.png'],
            'rock_ceiling': [folder / 'rock_spike_down.png'],
            'rock_horizontal': [folder / 'floating_platform.png'],
            'rock_vertical': [folder / 'stone_wall.png'],
            'rock_diagonal': [folder / 'stone_bridge.png'],
            'cannon': [shooters_folder / 'bear_launcher.png'],
            'flame': [shooters_folder / 'dragon_head.png'],
        }
        paths.update({
            'goose': [GOOSE_FRAMES_FOLDER / f'goose_{i}.png' for i in range(2)],
            'red_goose': [GOOSE_FRAMES_FOLDER / f'red_goose_{i}.png' for i in range(2)],
            'bat': [ASSETS / 'bats' / f'bat_{i}.png' for i in (1, 2)],})
        
        paths.update({f'fence_{i}': [folder / f'fence_{i}.png']
                      for i in range(len(FENCE_SIZES))})
        for key, filenames in paths.items():
            self.obstacle_frames[key] = load_frames(
                filenames, OBSTACLE_SIZES[key], trim=key not in LAUNCHERS
            )
        # Les lanceurs gardent leur cadre source pour conserver la bouche calibrée.
        self.goose_frames = self.obstacle_frames['goose']
        self.goose_mask = pygame.mask.from_surface(self.goose_frames[0])

        # Créer un masque par image, après les redimensionnements.
        for key, frames in self.obstacle_frames.items():
            self.obstacle_masks[key] = [
                pygame.mask.from_surface(image)
                for image in frames
            ]

        # Entities répète ces motifs à hauteur fixe et anime leur défilement.
        self.jet_images = {}

        for kind, filename in (
            ('cannon', 'bear_laser.png'),
            ('flame', 'fire_ball.png'),
        ):
            self.jet_images[kind] = load_image(
                str(shooters_folder / filename)
            ).convert_alpha()
        
    # Dessiner un obstacle, son avertissement et son jet.
    def draw_obstacle(self, screen, obstacle):
        if obstacle.kind in ('cannon', 'flame'):
            mouth_x, mouth_y = obstacle.muzzle

            # Clignotement de la ligne avant le tir.
            if obstacle.age < JET_WARNING:
                if int(obstacle.age * 8) % 2 == 0:
                    color = (
                        (255, 205, 70)
                        if obstacle.kind == 'cannon'
                        else (255, 100, 45)
                    )

                    pygame.draw.line(
                        screen,
                        color,
                        (0, mouth_y),
                        (mouth_x, mouth_y),
                        2
                    )

            # Afficher exactement la surface utilisée pour le masque.
            if obstacle.firing and obstacle.jet_surface is not None:
                screen.blit(
                    obstacle.jet_surface,
                    obstacle.jet_rect
                )

        # Dessiner le lanceur par-dessus l’extrémité de son jet.
        # visuals.16 : Fondu après le tir, sans modifier la ressource partagée.
        if obstacle.kind in LAUNCHERS and obstacle.age >= JET_END:
            image = obstacle.image.copy()
            image.set_alpha(obstacle.opacity)
            screen.blit(image, obstacle.rect)
        else:
            screen.blit(obstacle.image, obstacle.rect)

    