import random
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

# On cache le curseur classique de la souris
pygame.mouse.set_visible(False)

# Variables de jeu
rayon = 35
x = random.randint(rayon, 1280 - rayon)
y = random.randint(rayon, 720 - rayon)
vitesse_de_base = 2.0  # Départ très doux !
dir_x = random.choice([-1, 1])
dir_y = random.choice([-1, 1])

score = 0
meilleur_score = 20  # Record fixé pour Jack !

# Minuteur (30 secondes)
temps_limite = 30
temps_debut = pygame.time.get_ticks()
game_over = False

# Polices
font = pygame.font.SysFont(None, 40)
font_grand = pygame.font.SysFont(None, 80)

while running:
    # Calcul du temps
    if not game_over:
        temps_ecoule = (pygame.time.get_ticks() - temps_debut) // 1000
        temps_restant = max(0, temps_limite - temps_ecoule)

        # La vitesse augmente au fil du temps (ajoute 0.4 à la vitesse par seconde écoulée)
        vitesse_actuelle = vitesse_de_base + (temps_ecoule * 0.4)

        if temps_restant == 0:
            game_over = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # Recommencer avec la touche ESPACE
            if event.key == pygame.K_SPACE and game_over:
                score = 0
                temps_debut = pygame.time.get_ticks()
                game_over = False
                pygame.mouse.set_visible(False)
                x = random.randint(rayon, 1280 - rayon)
                y = random.randint(rayon, 720 - rayon)
                dir_x = random.choice([-1, 1])
                dir_y = random.choice([-1, 1])

        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            if event.button == 1:
                pos_souris = event.pos
                distance = (
                    (pos_souris[0] - x) ** 2 + (pos_souris[1] - y) ** 2
                ) ** 0.5

                if distance <= rayon:
                    score += 1
                    if score > meilleur_score:
                        meilleur_score = score

                    x = random.randint(rayon, 1280 - rayon)
                    y = random.randint(rayon, 720 - rayon)
                    dir_x = random.choice([-1, 1])
                    dir_y = random.choice([-1, 1])

    # Déplacement progressif si la partie continue
    if not game_over:
        x += dir_x * vitesse_actuelle
        y += dir_y * vitesse_actuelle

        # Rebonds sur les bords
        if x - rayon <= 0:
            x = rayon
            dir_x = 1
        elif x + rayon >= 1280:
            x = 1280 - rayon
            dir_x = -1

        if y - rayon <= 0:
            y = rayon
            dir_y = 1
        elif y + rayon >= 720:
            y = 720 - rayon
            dir_y = -1

    # --- DESSIN ---
    screen.fill((20, 24, 33))  # Fond bleu très foncé

    if not game_over:
        # Cible 2D
        pygame.draw.circle(screen, "red", (int(x), int(y)), rayon)
        pygame.draw.circle(
            screen, "white", (int(x), int(y)), int(rayon * 0.6)
        )
        pygame.draw.circle(screen, "red", (int(x), int(y)), int(rayon * 0.3))

        # Viseur 2D
        souris_x, souris_y = pygame.mouse.get_pos()
        pygame.draw.circle(screen, "cyan", (souris_x, souris_y), 12, 2)
        pygame.draw.line(
            screen,
            "cyan",
            (souris_x - 18, souris_y),
            (souris_x + 18, souris_y),
            2,
        )
        pygame.draw.line(
            screen,
            "cyan",
            (souris_x, souris_y - 18),
            (souris_x, souris_y + 18),
            2,
        )

        # Textes du Score, Record de Jack et Minuteur
        texte_score = font.render(f"Score : {score}", True, "white")
        texte_record = font.render(
            f"Record Jack : {meilleur_score}", True, "gold"
        )
        texte_temps = font.render(f"Temps : {temps_restant}s", True, "yellow")

        screen.blit(texte_score, (20, 20))
        screen.blit(texte_record, (500, 20))
        screen.blit(texte_temps, (1100, 20))
    else:
        # Écran de Game Over
        pygame.mouse.set_visible(True)
        texte_over = font_grand.render("TEMPS ÉCOULÉ !", True, "red")
        texte_final = font.render(f"Score final : {score}", True, "white")
        texte_record = font.render(
            f"Record de Jack : {meilleur_score}", True, "gold"
        )
        texte_restart = font.render(
            "Appuie sur ESPACE pour rejouer", True, "gray"
        )

        screen.blit(texte_over, (420, 220))
        screen.blit(texte_final, (540, 320))
        screen.blit(texte_record, (510, 370))
        screen.blit(texte_restart, (450, 440))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()