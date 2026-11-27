"""Main intégré : pièces, HUD, pause, obstacles et transitions.
Remplacer ce fichier avec les modules de la même archive.
Le profil du joueur est conservé dans sauvegarde.json.
"""
import pygame, random, sys
from game_strip import GameStrip
from pygame.locals import *
from coins import CoinSpawner
from bonus import BonusSpawner
from menu import show_menu
from sauvegarde import Profil
from uuid import uuid4
from game_over import show_game_over
from settings import *
from gravity import JetpackPhysics
from visuals import Visuals
from entities import *
from worlds import next_hazard, next_gate, other_world
from transitions import Transition
from audio import Audio
from pause_menu import show_pause


def terminate():
    pygame.quit()
    sys.exit()

def main():
    # Set up pygame, the window, and the mouse cursor.
    pygame.init()
    mainClock = pygame.time.Clock()
    windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption("Leprechaun Escape")
    pygame.mouse.set_visible(True)

    # Set up the fonts.
    font = pygame.font.SysFont(None, 48)

    # Toute la gestion musicale se trouve dans audio.py.
    audio = Audio()

    # Set up images.
    boutique = Profil()
    visuals = Visuals(boutique.equipe)               # loads the 3 frames and their masks
    hud = GameStrip()
    playerRect = visuals.get_rect()

    # Provide the shared resources to all hazards.
    Hazard.configure(
        visuals.obstacle_frames,
        visuals.obstacle_masks,
        visuals.jet_images)


    topScore = boutique.record
    last_score = boutique.dernier_score
    sound_enabled = boutique.son
    open_main_menu = True
    gravity = JetpackPhysics()
    coins = CoinSpawner()
    bonuses = BonusSpawner()
    coin_count = 0


    while True:
        # Musique du menu principal (également au retour après Game Over).
        if open_main_menu:
            audio.stop_game_over()
            audio.set_enabled(sound_enabled)
            audio.play("menu")
            sound_enabled = show_menu(
                windowSurface,
                high_score=topScore,
                last_score=last_score,
                sound_enabled=sound_enabled,
                boutique=boutique
            )

        visuals.set_skin(boutique.equipe)

        # Appliquer le choix SOUND ON/OFF fait dans le menu.
        audio.set_enabled(sound_enabled)
        audio.stop_game_over()
        
        # main.1 : Réinitialiser la partie et le monde.
        run_id = uuid4().hex
        hazards = []
        world = 'meadow'
        distance = 0.0
        score = 0
        speed = START_SPEED

        # Délais avant les obstacles.
        danger_timer = 1.0
        safe_timer = 0.0

        # Position et mouvement : une nouvelle partie commence en vol.
        visuals.set_player_mode('fly')
        playerRect = visuals.get_rect()
        playerRect.center = (WINDOWWIDTH / 3 - 100, WINDOWHEIGHT / 2)
        gravity.reset(playerRect.centery)
        thrusting = False

        # Effets visuels, pièces et bandeau.
        visuals.reset_jet()
        coins.reset()
        coin_count = 0
        hud.reset()
        hud.pot_max = POT_REQUIRED

        bonuses.reset()

        gold_remaining = 0.0
        gold_return_world = 'meadow'

        # Préparation des portails.
        next_portal = next_gate(distance)
        portal_x = None
        portal_destination = None
        transition = None

        audio.play(world)
        leave_action = None # None = partie normale ; sinon "restart" ou "menu" (choisi dans la pause).

        # main.2 : Boucle de la partie.
        while True:
            mainClock.tick(FPS)

            # Pas de temps fixe, compatible avec notre physique actuelle.
            dt = 1 / FPS

            collision = False
            pause_requested = False

            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()

                # Clic sur le bouton pause du bandeau.
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if hud.pause_rect.collidepoint(event.pos):
                        pause_requested = True

                if event.type == KEYDOWN:
                    if event.key == K_p:
                        pause_requested = True
                    if event.key == K_SPACE:
                        thrusting = True

                if event.type == KEYUP:
                    if event.key == K_ESCAPE:
                        terminate()

                    if event.key == K_SPACE:
                        thrusting = False

            # Ouvrir le menu pause (bloquant : le jeu est figé tant qu'il est ouvert).
            if pause_requested:
                thrusting = False
                audio.pause()
                choice = show_pause(windowSurface)
                audio.unpause()

                if choice != "resume":
                    leave_action = choice
                    break

            # main.3 : Faire avancer une transition en cours.
            if transition is not None:

                # Changer le monde lorsque le nuage couvre l'écran.
                if transition.update(dt):
                    world = transition.destination
                    audio.play(world)

                # Terminer la transition et préparer la suite.
                if transition.done:
                    transition = None
                    portal_destination = None

                    safe_timer = SAFE_SECONDS
                    danger_timer = 0.0

                    bonuses.clear()
                    if world == 'gold':
                        bonuses.consume_pots()
                        hud.pot = 0
                        gold_remaining = GOLD_SECONDS
                        coins.timer = 0
                        next_portal = float('inf')
                    else:
                        next_portal = next_gate(distance)
            
            # main.4 : Faire avancer le jeu seulement hors transition.
            else:
                safe_timer = max(0.0, safe_timer - dt)

                if world == 'gold':
                    speed = GOLD_SPEED

                else:
                    speed = min(
                        MAX_SPEED,
                        START_SPEED + distance * SPEED_PER_METER
                    )

                    distance += speed * dt * METERS_PER_PIXEL
                    score = int(distance)

                # Animation et mouvement du personnage.
                # Depuis le sol : ESPACE déclenche le décollage.
                # On conserve la position des pieds en changeant de hitbox.
                if thrusting and visuals.mode == 'walk':
                    playerRect = visuals.set_player_mode('fly', playerRect)
                    gravity.reset(playerRect.centery)

                playerRect.centery = gravity.update(
                    thrusting,
                    playerRect.height,
                    WINDOWHEIGHT
                )

                # À l'atterrissage, la pose debout apparaît seulement quand
                # les pieds atteignent FLOOR, pas selon un Y arbitraire.
                if (not thrusting and playerRect.bottom >= FLOOR
                        and gravity.velocity >= 0):
                    if visuals.mode != 'walk':
                        playerRect = visuals.set_player_mode('walk', playerRect)
                        playerRect.bottom = FLOOR
                        gravity.reset(playerRect.centery)

                # Le masque change avec la frame avant les collisions.
                visuals.update_pose()
                visuals.update_jet(playerRect, thrusting)

                # main.5 : Déplacer les obstacles déjà présents.
                for obstacle in hazards:
                    obstacle.update(dt, speed, playerRect)

                # Retirer les obstacles sortis ou ayant terminé leur tir.
                hazards = [
                    obstacle
                    for obstacle in hazards
                    if not obstacle.offscreen()
                ]

                # main.6 : Bonus génériques et transition arc-en-ciel immédiate.
                bonuses.update(
                    playerRect, visuals.mask, speed, hazards, dt, world,
                    blocked=(portal_x is not None
                             or (world != 'gold' and distance >= next_portal))
                )
                hud.pot = bonuses.pots
                hud.clover = bonuses.clover_state

                if world == 'gold':
                    gold_remaining = max(0.0, gold_remaining - dt)
                    gate_pending = gold_remaining <= 0
                    if gate_pending:
                        transition = Transition.rainbow(gold_return_world)
                        hazards.clear()
                        coins.reset()
                        bonuses.clear()
                elif bonuses.ready:
                    gold_return_world = world
                    transition = Transition.rainbow('gold')
                    portal_x = None
                    portal_destination = None
                    hazards.clear()
                    coins.reset()
                    bonuses.clear()
                    gate_pending = True
                else:
                    gate_pending = distance >= next_portal
                    if gate_pending and portal_x is None and not hazards:
                        portal_x = WINDOWWIDTH + 140
                        portal_destination = other_world(world)

                # main.7 : Déplacer le portail vers la gauche.
                if portal_x is not None:
                    portal_x -= speed * dt

                    # Déclencher la transition quand il atteint le joueur.
                    if portal_x <= playerRect.centerx:
                        transition = Transition(
                            portal_destination,
                            start_x=portal_x - 20,
                            portal_x=portal_x
                        )

                        # La transition dessine désormais le portail.
                        portal_x = None
                        coins.reset()
                        bonuses.clear()

                # main.8 : Autoriser ou bloquer les nouveaux obstacles.
                can_spawn = (
                    world != 'gold'
                    and not gate_pending
                    and portal_x is None
                    and transition is None
                    and safe_timer <= 0
                )

                if can_spawn:
                    danger_timer -= dt

                    if danger_timer <= 0:
                        obstacle = next_hazard(
                            world,
                            distance,
                            hazards,
                            speed,
                        )

                        if obstacle is not None:
                            hazards.append(obstacle)

                            # Réduire progressivement le délai d'apparition.
                            progress = min(
                                1.0,
                                distance / DENSITY_MAX_DISTANCE
                            )

                            interval = (
                                OBSTACLE_INTERVAL_START
                                + (
                                    OBSTACLE_INTERVAL_MIN
                                    - OBSTACLE_INTERVAL_START
                                ) * progress
                            )

                            danger_timer = max(
                                OBSTACLE_INTERVAL_MIN,
                                interval * random.uniform(0.9, 1.1)
                            )

                        else:
                            # Réessayer si aucun obstacle n'était autorisé.
                            danger_timer = 0.10

                # main.9 : Vérifier les collisions hors transition et sécurité.
                if transition is None and safe_timer <= 0 and not bonuses.invincible:
                    for obstacle in hazards:
                        if obstacle.collides_with(playerRect, visuals.mask):
                            collision = True
                            break
                # main.9b : Fréquence dorée ; multiplication uniquement par un bonus actif.
                if transition is None:
                    in_gold = world == 'gold'
                    gained = coins.update(
                        playerRect, speed, hazards, blocked=gate_pending, dt=dt,
                        interval=GOLD_COIN_INTERVAL if in_gold else COIN_INTERVAL
                    )
                    coin_count += gained * bonuses.coin_multiplier

                    # Son lors de la récupération des pièces.
                    if gained > 0:
                        audio.play_pickup()

            # main.10 : Dessiner le fond du monde actuel.
            visuals.draw_background(windowSurface, world)

            coins.draw(windowSurface)
            bonuses.draw(windowSurface)

            # Dessiner les obstacles et le personnage.
            for obstacle in hazards:
                visuals.draw_obstacle(windowSurface, obstacle)

            visuals.draw_player(windowSurface, playerRect)

            # main.11 : Dessiner le portail pendant son approche.
            if portal_x is not None:
                visuals.draw_portal(windowSurface, portal_x)

            # main.12 : Dessiner la transition par-dessus le décor.
            if transition is not None:
                transition.draw(
                    windowSurface,
                    visuals.portal_image
                )

            # main.13 : Dessiner la barre en bois en dernier.
            hud.draw(windowSurface, score, coin_count, max(topScore, score))

            # main.13b : Jauge dorée ; le timer est déjà figé pendant la pause.
            if world == 'gold' and transition is None:
                hud.draw_gold_timer(windowSurface, gold_remaining, GOLD_SECONDS)


            pygame.display.update()

            # 8. End the game if the player has collided with an obstacle. Actualize the top score if necessary.
            if collision:
                topScore = max(topScore, score)
                break

        # Quitter depuis la pause : on saute l'écran Game Over.
        if leave_action is not None:
            open_main_menu = leave_action == "menu"
            continue
        
        # La musique s’arrête et le son Game Over est joué par audio.py.
        audio.play_game_over()

        # Save the latest score and update the session record.
        last_score = score
        boutique.fin_partie(run_id, coin_count, score)
        topScore = max(topScore, score)

        # Show the game-over panel over the frozen game.
        action = show_game_over(windowSurface, score, topScore)

        # Choose whether to open the main menu before the next game.
        open_main_menu = action == "menu"   


if __name__ == "__main__":
    main()

