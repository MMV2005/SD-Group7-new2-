# Importe Pygame pour dessiner le menu et lire les clics.
import pygame


# Reçoit la fenêtre existante, le meilleur score et le dernier score.
# Renvoie True pour jouer et False pour quitter.
def afficher_menu(surface, meilleur_score, dernier_score):
    # Rend la souris visible pendant le menu.
    pygame.mouse.set_visible(True)
    # Crée une horloge pour limiter la vitesse de la boucle du menu.
    horloge = pygame.time.Clock()
    # Lit les dimensions de la fenêtre du jeu.
    largeur, hauteur = surface.get_size()
    # Adapte la taille du texte à la fenêtre.
    taille = max(16, min(largeur // 14, hauteur // 12, 48))
    # Crée la police du titre avec la police par défaut de Pygame.
    police_titre = pygame.font.Font(None, taille + 12)
    # Crée la police des scores et du bouton.
    police = pygame.font.Font(None, taille)
    # Crée le rectangle qui sert à dessiner et à détecter le bouton.
    bouton = pygame.Rect(0, 0, min(220, largeur * 3 // 4), taille + 24)
    # Place le bouton au centre horizontal, vers le bas du menu.
    bouton.center = (largeur // 2, hauteur * 3 // 4)

    # Cette fonction locale dessine un texte centré à une hauteur donnée.
    def texte_centre(texte, fonte, couleur, y):
        # Transforme le texte en image ; True lisse les lettres.
        image = fonte.render(texte, True, couleur)
        # Centre le rectangle de l'image dans la fenêtre.
        rectangle = image.get_rect(center=(largeur // 2, y))
        # Colle l'image du texte sur la fenêtre.
        surface.blit(image, rectangle)

    # Garde le menu ouvert jusqu'à une demande de jouer ou de quitter.
    while True:
        # Récupère les événements en attente : clavier, souris, fermeture.
        for evenement in pygame.event.get():
            # La croix de la fenêtre demande de quitter le jeu.
            if evenement.type == pygame.QUIT:
                return False
            # Échap permet aussi de quitter depuis le menu.
            if evenement.type == pygame.KEYDOWN and evenement.key == pygame.K_ESCAPE:
                return False
            # Vérifie que l'utilisateur a appuyé sur le bouton gauche.
            if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
                # Vérifie que le clic se trouve à l'intérieur du bouton Play.
                if bouton.collidepoint(evenement.pos):
                    # Cache à nouveau la souris pendant la partie.
                    pygame.mouse.set_visible(False)
                    # Termine la fonction et autorise le lancement de la partie.
                    return True

        # Efface l'image précédente avec un fond vert foncé.
        surface.fill((18, 48, 36))
        # Affiche le nom du jeu en doré.
        texte_centre('leprechaun', police_titre, (255, 210, 90), hauteur // 5)
        # La f-string insère la valeur du meilleur score dans le texte.
        texte_centre(f'Meilleur score : {meilleur_score}', police, (255, 255, 255), hauteur * 2 // 5)
        # None signifie qu'aucune partie n'a encore été jouée.
        dernier = '-' if dernier_score is None else str(dernier_score)
        # Affiche le dernier score, ou un tiret au premier lancement.
        texte_centre(f'Dernier score : {dernier}', police, (255, 255, 255), hauteur // 2)
        # Détecte si la souris survole le bouton.
        survol = bouton.collidepoint(pygame.mouse.get_pos())
        # Choisit une couleur plus claire lorsque la souris passe dessus.
        couleur = (255, 225, 125) if survol else (225, 180, 65)
        # Dessine le bouton avec des coins arrondis.
        pygame.draw.rect(surface, couleur, bouton, border_radius=12)
        # Dessine le mot Play au centre du bouton.
        texte_centre('Play', police, (18, 48, 36), bouton.centery)
        # Affiche à l'écran tout ce qui vient d'être dessiné.
        pygame.display.update()
        # Limite le menu à 60 images par seconde pour ménager le processeur.
        horloge.tick(60)