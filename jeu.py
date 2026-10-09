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

# Tailles selon la difficulté
taille_cube = 55
taille_doree = 45

rect_rouge = pygame.Rect(
    random.randint(0, 1280 - taille_cube),
    random.randint(0, 720 - taille_cube),
    taille_cube,
    taille_cube,
)

rect_dore = pygame.Rect(0, 0, taille_doree, taille_doree)
doree_active = False
dernier_pop_doree = pygame.time.get_ticks()
duree_doree = 2500

# Variables de session
score = 0
meilleur_score = 70  # Record fixé de Jack
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
                # Adaptation progressive de la taille des cubes
                if 290 <= pos_souris[0] <= 490 and 380 <= pos_souris[1] <= 440:
                    difficulte = "Facile"
                    taille_cube = 100
                    taille_doree = 80
                elif 540 <= pos_souris[0] <= 740 and 380 <= pos_souris[1] <= 440:
                    difficulte = "Moyen"
                    taille_cube = 55
                    taille_doree = 45
                elif 790 <= pos_souris[0] <= 990 and 380 <= pos_souris[1] <= 440:
                    difficulte = "Difficile"
                    taille_cube = 25
                    taille_doree = 20

                if 510 <= pos_souris[0] <= 770 and 480 <= pos_souris[1] <= 550:
                    score = 0
                    temps_debut = pygame.time.get_ticks()
                    dernier_pop_doree = pygame.time.get_ticks()
                    doree_active = False

                    # Mettre à jour la dimension des rectangles selon la difficulté choisie
                    rect_rouge.width = taille_cube
                    rect_rouge.height = taille_cube
                    rect_rouge.x = random.randint(0, 1280 - taille_cube)
                    rect_rouge.y = random.randint(0, 720 - taille_cube)

                    rect_dore.width = taille_doree
                    rect_dore.height = taille_doree

                    etat_jeu = "JEU"
                    pygame.mouse.set_visible(False)

            # JEU
            elif etat_jeu == "JEU":
                son_tir.play()
                effets_tir.append({"pos": pos_souris, "rayon": 5})

                touche = False

                # Test clic sur cube doré (+3 pts)
                if doree_active and rect_dore.collidepoint(pos_souris):
                    score += 3
                    doree_active = False
                    touche = True
                    son_impact_verre.play()

                # Test clic sur cube rouge (+1 pt)
                if not touche and rect_rouge.collidepoint(pos_souris):
                    score += 1
                    touche = True
                    son_impact_verre.play()
                    rect_rouge.x = random.randint(0, 1280 - taille_cube)
                    rect_rouge.y = random.randint(0, 720 - taille_cube)

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
            epaisse = 5 if difficulte == nom else 1
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

        # Apparition Cube doré (toutes les 3s)
        if not doree_active and temps_actuel - dernier_pop_doree >= 3000:
            rect_dore.x = random.randint(0, 1280 - taille_doree)
            rect_dore.y = random.randint(0, 720 - taille_doree)
            doree_active = True
            dernier_pop_doree = temps_actuel

        if doree_active and temps_actuel - dernier_pop_doree >= duree_doree:
            doree_active = False

        # Dessin du cube rouge
        pygame.draw.rect(screen, "red", rect_rouge, border_radius=6)
        pygame.draw.rect(
            screen, "white", rect_rouge, width=2, border_radius=6
        )

        # Dessin du cube doré
        if doree_active:
            pygame.draw.rect(screen, "gold", rect_dore, border_radius=6)
            pygame.draw.rect(
                screen, "white", rect_dore, width=2, border_radius=6
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
            font.render(f"Mode : {difficulte}", True, "gray"), (20, 60)
        )
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