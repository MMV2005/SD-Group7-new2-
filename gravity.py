class JetpackPhysics():

    def __init__(self, gravity=0.7, thrust=1.0, max_fall_speed=10, max_rise_speed=9):
        # Paramètres de réglage (pixels par frame, ou par frame au carré)
        self.gravity = gravity                # accélération vers le bas
        self.thrust = thrust                  # accélération vers le haut (espace maintenue)
        self.max_fall_speed = max_fall_speed  # vitesse de chute maximale
        self.max_rise_speed = max_rise_speed  # vitesse de montée maximale

        # État interne
        self.y = 0.0         # position verticale exacte du centre du personnage
        self.velocity = 0.0  # vitesse verticale (négative = vers le haut)

    def reset(self, center_y):
        """À appeler au début de chaque partie : repart à l'arrêt à la hauteur donnée."""
        self.y = float(center_y)
        self.velocity = 0.0

    def update(self, thrusting, sprite_height, window_height):
        """Avance la physique d'une frame et renvoie la position verticale du centre,
        arrondie en entier (prête à être donnée à un pygame.Rect)."""

        # 1. Accélération selon l'état de la touche espace
        if thrusting:
            self.velocity -= self.thrust
        else:
            self.velocity += self.gravity

        # 2. Plafonnement de la vitesse dans les deux sens
        self.velocity = max(-self.max_rise_speed, min(self.max_fall_speed, self.velocity))

        # 3. Mise à jour de la position exacte (flottante)
        self.y += self.velocity

        # 4. Blocage au plafond et au sol : self.y est la position du centre,
        #    donc on garde une demi-hauteur de marge de chaque côté
        half = sprite_height / 2
        if self.y < half:
            self.y = half
            self.velocity = 0.0
        if self.y > window_height - half:
            self.y = window_height - half
            self.velocity = 0.0

        # 5. Position entière pour l'affichage et les collisions
        return round(self.y)