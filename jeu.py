import array
import random
import pygame

# Initialisation audio et pygame
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()


# --- GENERATION DES SONS ---
def generer_son_tir():
    frequence = 44100
    duree = 0.05
    nb_echantillons = int(frequence * duree)
    tampon = array.array("h")
    for i in range(nb_echantillons):
        valeur = (
            int(32767 * 0.2 * (1 - i / nb_echantillons)) if i % 15 < 7 else 0
        )
        tampon.append(valeur)
    return pygame.mixer.Sound(buffer=tampon)


def generer_son_verre_casse():
    frequence = 44100
    duree = 0.25
    nb_echantillons = int(frequence * duree)
    tampon = array.array("h")
    for i in range(nb_echantillons):
        attenuation = 1 - (i / nb_echantillons)
        bruit = random.randint(-32000, 32000)
        valeur = int(bruit * 0.4 * attenuation)
        tampon.append(valeur)
    return pygame.mixer.Sound(buffer=tampon)


son_tir = generer_son_tir()
son_impact_verre = generer_son_verre_casse()

# Polices
font = pygame.font.SysFont(None, 40)
font_grand = pygame.font.SysFont(None, 70)

# Etats du jeu
etat_jeu = "MENU"
difficulte = "Moyen"
vitesse_de_base = 2.5

# Cible rouge
rayon = 35
x = random.randint(rayon, 1280 - rayon)
y = random.randint(rayon, 720 - rayon)
dir_x = random.choice([-1, 1])
dir_y = random.choice([-1, 1])

# Cible dorée mouvante
doree_x = 0
doree_y = 0
doree_dir_x = 0
doree_dir_y = 0
doree_active = False
doree_rayon = 30  # Légèrement plus grande (30 au lieu de 25)
dernier_pop_doree = pygame.time.get_ticks()
duree_doree = 2500  # Dure 2.5 secondes au lieu de 1.5s

# Variables de session
score = 0
meilleur_score = 100  # Record fixé de Jack
temps_limite = 30
temps_debut = 0
effets_tir = []

running = True
while running:
    temps_actuel = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos_souris = event.pos

            # MENU
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
                    doree_active = False
                    etat_jeu = "JEU"
                    pygame.mouse.set_visible(False)

            # JEU
            elif etat_jeu == "JEU":
                son_tir.play()
                effets_tir.append({"pos": pos_souris, "rayon": 5})

                touche = False

                # Cible dorée (+3 pts)
                if doree_active:
                    dist_doree = (
                        (pos_souris[0] - doree_x) ** 2
                        + (pos_souris[1] - doree_y) ** 2
                    ) ** 0.5
                    if dist_doree <= doree_rayon:
                        score += 3
                        doree_active = False
                        touche = True
                        son_impact_verre.play()

                # Cible rouge (+1 pt)
                if not touche:
                    dist_rouge = (
                        (pos_souris[0] - x) ** 2 + (pos_souris[1] - y) ** 2
                    ) ** 0.5
                    if dist_rouge <= rayon:
                        score += 1
                        touche = True
                        son_impact_verre.play()
                        x = random.randint(rayon, 1280 - rayon)
                        y = random.randint(rayon, 720 - rayon)
                        dir_x = random.choice([-1, 1])
                        dir_y = random.choice([-1, 1])

                # Pénalité clic raté (-1 pt)
                if not touche:
                    score = max(0, score - 1)

                if score > meilleur_score:
                    meilleur_score = score

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and etat_jeu == "GAME_OVER":
                etat_jeu = "MENU"

    # --- RENDU ---
    screen.fill((20, 24, 33))

    if etat_jeu == "MENU":
        pygame.mouse.set_visible(True)
        t_titre = font_grand.render("AIM TRAINER 2D", True, "white")
        t_record = font.render(f"Record Jack : {meilleur_score}", True, "gold")

        screen.blit(t_titre, (440, 150))
        screen.blit(t_record, (510, 240))

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

        # Cible rouge
        x += dir_x * vitesse_actuelle
        y += dir_y * vitesse_actuelle
        if x - rayon <= 0 or x + rayon >= 1280:
            dir_x *= -1
        if y - rayon <= 0 or y + rayon >= 720:
            dir_y *= -1

        # Apparition cible dorée (toutes les 3s)
        if not doree_active and temps_actuel - dernier_pop_doree >= 3000:
            doree_x = random.randint(doree_rayon, 1280 - doree_rayon)
            doree_y = random.randint(doree_rayon, 720 - doree_rayon)
            doree_dir_x = random.choice([-1, 1])
            doree_dir_y = random.choice([-1, 1])
            doree_active = True
            dernier_pop_doree = temps_actuel

        # Déplacement & disparition de la cible dorée
        if doree_active:
            vitesse_doree = vitesse_actuelle * 1.2
            doree_x += doree_dir_x * vitesse_doree
            doree_y += doree_dir_y * vitesse_doree
            if doree_x - doree_rayon <= 0 or doree_x + doree_rayon >= 1280:
                doree_dir_x *= -1
            if doree_y - doree_rayon <= 0 or doree_y + doree_rayon >= 720:
                doree_dir_y *= -1

            if temps_actuel - dernier_pop_doree >= duree_doree:
                doree_active = False

        # Dessin cible rouge
        pygame.draw.circle(screen, "red", (int(x), int(y)), rayon)
        pygame.draw.circle(screen, "white", (int(x), int(y)), int(rayon * 0.6))
        pygame.draw.circle(screen, "red", (int(x), int(y)), int(rayon * 0.3))

        # Dessin cible dorée
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

        # Viseur
        sx, sy = pygame.mouse.get_pos()
        pygame.draw.circle(screen, "cyan", (sx, sy), 12, 2)
        pygame.draw.line(screen, "cyan", (sx - 18, sy), (sx + 18, sy), 2)
        pygame.draw.line(screen, "cyan", (sx, sy - 18), (sx, sy + 18), 2)

        # Interface
        screen.blit(font.render(f"Score : {score}", True, "white"), (20, 20))
        screen.blit(
            font.render(f"Record Jack : {meilleur_score}", True, "gold"),
            (500, 20),
        )
        screen.blit(
            font.render(f"Temps : {temps_restant}s", True, "yellow"), (1100, 20)
        )

    elif etat_jeu == "GAME_OVER":
        pygame.mouse.set_visible(True)
        t_over = font_grand.render("TEMPS ÉCOULÉ !", True, "red")
        t_final = font.render(f"Score final : {score}", True, "white")
        t_rec = font.render(f"Record de Jack : {meilleur_score}", True, "gold")
        t_restart = font.render(
            "Appuie sur ESPACE pour revenir au menu", True, "gray"
        )

        screen.blit(t_over, (420, 220))
        screen.blit(t_final, (540, 320))
        screen.blit(t_rec, (510, 370))
        screen.blit(t_restart, (380, 450))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()