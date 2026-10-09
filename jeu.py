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

# Animation d'apparition (échelle)
echelle_rouge = 0.0
echelle_dore = 0.0

# Stats et Gameplay
score = 0
meilleur_score = 100  # Record fixé de Jack
temps_limite = 30.0
temps_debut = 0
effets_tir = []
particules = []

tirs_totaux = 0
tirs_touches = 0
combo = 0
multiplicateur = 1

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
                    tirs_totaux = 0
                    tirs_touches = 0
                    combo = 0
                    multiplicateur = 1
                    temps_limite = 30.0
                    temps_debut = pygame.time.get_ticks()
                    dernier_pop_doree = pygame.time.get_ticks()
                    doree_active = False

                    rect_rouge.width = taille_cube
                    rect_rouge.height = taille_cube
                    rect_rouge.x = random.randint(0, 1280 - taille_cube)
                    rect_rouge.y = random.randint(0, 720 - taille_cube)
                    rect_dore.width = taille_doree
                    rect_dore.height = taille_doree

                    echelle_rouge = 0.0
                    particules.clear()
                    effets_tir.clear()

                    etat_jeu = "JEU"
                    pygame.mouse.set_visible(False)

            # JEU
            elif etat_jeu == "JEU":
                son_tir.play()
                effets_tir.append({"pos": pos_souris, "rayon": 5})
                tirs_totaux += 1
                touche = False

                # Test clic cube doré (+3 pts x multiplicateur, +1s bonus)
                if doree_active and rect_dore.collidepoint(pos_souris):
                    tirs_touches += 1
                    combo += 1
                    multiplicateur = 1 + (combo // 5)
                    score += 3 * multiplicateur
                    temps_limite += 1.0
                    doree_active = False
                    touche = True
                    son_impact_verre.play()

                    # Particules dorées
                    for _ in range(15):
                        particules.append(
                            {
                                "x": pos_souris[0],
                                "y": pos_souris[1],
                                "vx": random.uniform(-4, 4),
                                "vy": random.uniform(-4, 4),
                                "vie": 255,
                                "couleur": (255, 215, 0),
                            }
                        )

                # Test clic cube rouge (+1 pt x multiplicateur, +0.5s bonus)
                if not touche and rect_rouge.collidepoint(pos_souris):
                    tirs_touches += 1
                    combo += 1
                    multiplicateur = 1 + (combo // 5)
                    score += 1 * multiplicateur
                    temps_limite += 0.5
                    touche = True
                    son_impact_verre.play()

                    # Particules rouges
                    for _ in range(15):
                        particules.append(
                            {
                                "x": pos_souris[0],
                                "y": pos_souris[1],
                                "vx": random.uniform(-4, 4),
                                "vy": random.uniform(-4, 4),
                                "vie": 255,
                                "couleur": (255, 50, 50),
                            }
                        )

                    rect_rouge.x = random.randint(0, 1280 - taille_cube)
                    rect_rouge.y = random.randint(0, 720 - taille_cube)
                    echelle_rouge = 0.0

                # Pénalité en cas de raté
                if not touche:
                    combo = 0
                    multiplicateur = 1
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
        temps_ecoule = (temps_actuel - temps_debut) / 1000.0
        temps_restant = max(0.0, temps_limite - temps_ecoule)

        if temps_restant <= 0:
            etat_jeu = "GAME_OVER"

        # Apparition Cube doré (toutes les 3s)
        if not doree_active and temps_actuel - dernier_pop_doree >= 3000:
            rect_dore.x = random.randint(0, 1280 - taille_doree)
            rect_dore.y = random.randint(0, 720 - taille_doree)
            doree_active = True
            echelle_dore = 0.0
            dernier_pop_doree = temps_actuel

        if doree_active and temps_actuel - dernier_pop_doree >= duree_doree:
            doree_active = False

        # Animations de grossissement (grossissent jusqu'à 100%)
        echelle_rouge = min(1.0, echelle_rouge + 0.15)
        if doree_active:
            echelle_dore = min(1.0, echelle_dore + 0.15)

        # Dessin cube rouge
        w_r, h_r = int(taille_cube * echelle_rouge), int(
            taille_cube * echelle_rouge
        )
        off_x_r, off_y_r = (taille_cube - w_r) // 2, (taille_cube - h_r) // 2
        r_dessin = pygame.Rect(
            rect_rouge.x + off_x_r, rect_rouge.y + off_y_r, w_r, h_r
        )
        pygame.draw.rect(screen, "red", r_dessin, border_radius=6)
        pygame.draw.rect(screen, "white", r_dessin, width=2, border_radius=6)

        # Dessin cube doré
        if doree_active:
            w_d, h_d = int(taille_doree * echelle_dore), int(
                taille_doree * echelle_dore
            )
            off_x_d, off_y_d = (taille_doree - w_d) // 2, (
                taille_doree - h_d
            ) // 2
            d_dessin = pygame.Rect(
                rect_dore.x + off_x_d, rect_dore.y + off_y_d, w_d, h_d
            )
            pygame.draw.rect(screen, "gold", d_dessin, border_radius=6)
            pygame.draw.rect(
                screen, "white", d_dessin, width=2, border_radius=6
            )

        # Animation des particules d'impact
        for p in particules[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vie"] -= 12
            if p["vie"] <= 0:
                particules.remove(p)
            else:
                s = pygame.Surface((4, 4))
                s.set_alpha(p["vie"])
                s.fill(p["couleur"])
                screen.blit(s, (p["x"], p["y"]))

        # Effets de cercle du tir
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
        if multiplicateur > 1:
            screen.blit(
                font.render(
                    f"Combo x{multiplicateur} 🔥", True, "orange"
                ),
                (20, 100),
            )

        screen.blit(
            font.render(f"Record Jack : {meilleur_score}", True, "gold"),
            (500, 20),
        )
        screen.blit(
            font.render(f"Temps : {temps_restant:.1f}s", True, "yellow"),
            (1080, 20),
        )

    elif etat_jeu == "GAME_OVER":
        pygame.mouse.set_visible(True)
        precision = (
            (tirs_touches / tirs_totaux * 100) if tirs_totaux > 0 else 0.0
        )

        t_over = font_grand.render("TEMPS ÉCOULÉ !", True, "red")
        t_final = font.render(f"Score final : {score}", True, "white")
        t_prec = font.render(
            f"Précision : {precision:.1f}% ({tirs_touches}/{tirs_totaux})",
            True,
            "cyan",
        )
        t_rec = font.render(f"Record de Jack : {meilleur_score}", True, "gold")
        t_restart = font.render(
            "Appuie sur ESPACE pour revenir au menu", True, "gray"
        )

        screen.blit(t_over, (420, 180))
        screen.blit(t_final, (520, 270))
        screen.blit(t_prec, (440, 330))
        screen.blit(t_rec, (490, 390))
        screen.blit(t_restart, (380, 480))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()