import os
import random
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Gestion du fichier de sauvegarde du record
FICHIER_RECORD = "record.txt"
if os.path.exists(FICHIER_RECORD):
    with open(FICHIER_RECORD, "r") as f:
        try:
            meilleur_score = int(f.read().strip())
        except ValueError:
            meilleur_score = 100
else:
    meilleur_score = 25

# Polices
font = pygame.font.SysFont(None, 40)
font_grand = pygame.font.SysFont(None, 70)


def sauvegarder_record(score):
    with open(FICHIER_RECORD, "w") as f:
        f.write(str(score))


# Etats du jeu : "MENU", "JEU", "GAME_OVER"
etat_jeu = "MENU"
difficulte = "Moyen"
vitesse_de_base = 2.0

# Variables de la cible rouge
rayon = 35
x = random.randint(rayon, 1280 - rayon)
y = random.randint(rayon, 720 - rayon)
dir_x = random.choice([-1, 1])
dir_y = random.choice([-1, 1])

# Variables de la cible dorée (avec direction pour le mouvement)
doree_x = 0
doree_y = 0
doree_dir_x = 0
doree_dir_y = 0
doree_active = False
doree_rayon = 25
dernier_pop_doree = pygame.time.get_ticks()
duree_doree = 1500  # 1.5 seconde

# Partie et effets
score = 0
temps_limite = 30
temps_debut = 0
effets_tir = []

running = True
while running:
    temps_actuel = pygame.time.get_ticks()

    # --- EVENEMENTS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos_souris = event.pos

            # Clic dans le MENU
            if etat_jeu == "MENU":
                if 290 <= pos_souris[0] <= 490 and 380 <= pos_souris[1] <= 440:
                    difficulte = "Facile"
                    vitesse_de_base = 1.0
                elif 540 <= pos_souris[0] <= 740 and 380 <= pos_souris[1] <= 440:
                    difficulte = "Moyen"
                    vitesse_de_base = 2.5
                elif 790 <= pos_souris[0] <= 990 and 380 <= pos_souris[1] <= 440:
                    difficulte = "Difficile"
                    vitesse_de_base = 4.0

                if 510 <= pos_souris[0] <= 770 and 480 <= pos_souris[1] <= 550:
                    score = 0
                    temps_debut = pygame.time.get_ticks()
                    dernier_pop_doree = pygame.time.get_ticks()
                    etat_jeu = "JEU"
                    pygame.mouse.set_visible(False)

            # Clic pendant le JEU
            elif etat_jeu == "JEU":
                effets_tir.append({"pos": pos_souris, "rayon": 5})

                touche = False

                # Test collision cible dorée
                if doree_active:
                    dist_doree = (
                        (pos_souris[0] - doree_x) ** 2
                        + (pos_souris[1] - doree_y) ** 2
                    ) ** 0.5
                    if dist_doree <= doree_rayon:
                        score += 3
                        doree_active = False
                        touche = True

                # Test collision cible rouge
                if not touche:
                    dist_rouge = (
                        (pos_souris[0] - x) ** 2 + (pos_souris[1] - y) ** 2
                    ) ** 0.5
                    if dist_rouge <= rayon:
                        score += 1
                        touche = True
                        x = random.randint(rayon, 1280 - rayon)
                        y = random.randint(rayon, 720 - rayon)
                        dir_x = random.choice([-1, 1])
                        dir_y = random.choice([-1, 1])

                # Pénalité si tir raté
                if not touche:
                    score = max(0, score - 1)

                if score > meilleur_score:
                    meilleur_score = score
                    sauvegarder_record(meilleur_score)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and etat_jeu == "GAME_OVER":
                etat_jeu = "MENU"

    # --- LOGIQUE ---
    screen.fill((20, 24, 33))

    if etat_jeu == "MENU":
        pygame.mouse.set_visible(True)
        t_titre = font_grand.render("AIM TRAINER 2D", True, "white")
        t_record = font.render(
            f"Record actuel : {meilleur_score}", True, "gold"
        )

        screen.blit(t_titre, (440, 150))
        screen.blit(t_record, (510, 240))

        # Boutons de difficulté
        for pos, nom, c in [
            ((290, 380), "Facile", "green"),
            ((540, 380), "Moyen", "yellow"),
            ((790, 380), "Difficile", "red"),
        ]:
            epaisse = 3 if difficulte == nom else 1
            pygame.draw.rect(
                screen, c, (*pos, 200, 60), width=epaisse, border_radius=10
            )
            txt = font.render(nom, True, c)
            screen.blit(txt, (pos[0] + 50, pos[1] + 15))

        # Bouton Jouer
        pygame.draw.rect(
            screen, "cyan", (510, 480, 260, 70), width=2, border_radius=15
        )
        txt_jouer = font_grand.render("JOUER", True, "cyan")
        screen.blit(txt_jouer, (550, 495))

    elif etat_jeu == "JEU":
        temps_ecoule = (temps_actuel - temps_debut) // 1000
        temps_restant = max(0, temps_limite - temps_ecoule)

        if temps_restant == 0:
            etat_jeu = "GAME_OVER"

        vitesse_actuelle = vitesse_de_base + (temps_ecoule * 0.3)

        # Déplacement cible rouge
        x += dir_x * vitesse_actuelle
        y += dir_y * vitesse_actuelle
        if x - rayon <= 0 or x + rayon >= 1280:
            dir_x *= -1
        if y - rayon <= 0 or y + rayon >= 720:
            dir_y *= -1

        # Déplacement cible dorée
        if doree_active:
            # La cible dorée se déplace légèrement plus vite que la cible normale
            vitesse_doree = vitesse_actuelle * 1.3
            doree_x += doree_dir_x * vitesse_doree
            doree_y += doree_dir_y * vitesse_doree

            # Rebonds de la cible dorée
            if doree_x - doree_rayon <= 0 or doree_x + doree_rayon >= 1280:
                doree_dir_x *= -1
            if doree_y - doree_rayon <= 0 or doree_y + doree_rayon >= 720:
                doree_dir_y *= -1

        # Apparition cible dorée (toutes les 3s)
        if not doree_active and temps_actuel - dernier_pop_doree >= 3000:
            doree_x = random.randint(doree_rayon, 1280 - doree_rayon)
            doree_y = random.randint(doree_rayon, 720 - doree_rayon)
            doree_dir_x = random.choice([-1, 1])
            doree_dir_y = random.choice([-1, 1])
            doree_active = True
            dernier_pop_doree = temps_actuel

        if doree_active and temps_actuel - dernier_pop_doree >= duree_doree:
            doree_active = False

        # Dessin cible rouge
        pygame.draw.circle(screen, "red", (int(x), int(y)), rayon)
        pygame.draw.circle(screen, "white", (int(x), int(y)), int(rayon * 0.6))
        pygame.draw.circle(screen, "red", (int(x), int(y)), int(rayon * 0.3))

        # Dessin cible dorée mouvante
        if doree_active:
            pygame.draw.circle(
                screen, "gold", (int(doree_x), int(doree_y)), doree_rayon
            )
            pygame.draw.circle(
                screen,
                "white",
                (int(doree_x), int(doree_y)),
                int(doree_rayon * 0.5),
            )

        # Effets de tir
        for effet in effets_tir[:]:
            pygame.draw.circle(
                screen, "yellow", effet["pos"], int(effet["rayon"]), 2
            )
            effet["rayon"] += 2
            if effet["rayon"] > 25:
                effets_tir.remove(effet)

        # Viseur 2D
        sx, sy = pygame.mouse.get_pos()
        pygame.draw.circle(screen, "cyan", (sx, sy), 12, 2)
        pygame.draw.line(screen, "cyan", (sx - 18, sy), (sx + 18, sy), 2)
        pygame.draw.line(screen, "cyan", (sx, sy - 18), (sx, sy + 18), 2)

        # Interface
        screen.blit(font.render(f"Score : {score}", True, "white"), (20, 20))
        screen.blit(
            font.render(f"Record : {meilleur_score}", True, "gold"), (520, 20)
        )
        screen.blit(
            font.render(f"Temps : {temps_restant}s", True, "yellow"), (1100, 20)
        )

    elif etat_jeu == "GAME_OVER":
        pygame.mouse.set_visible(True)
        t_over = font_grand.render("TEMPS ÉCOULÉ !", True, "red")
        t_final = font.render(f"Score final : {score}", True, "white")
        t_rec = font.render(f"Meilleur record : {meilleur_score}", True, "gold")
        t_restart = font.render(
            "Appuie sur ESPACE pour revenir au menu", True, "gray"
        )

        screen.blit(t_over, (420, 220))
        screen.blit(t_final, (540, 320))
        screen.blit(t_rec, (500, 370))
        screen.blit(t_restart, (380, 450))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()