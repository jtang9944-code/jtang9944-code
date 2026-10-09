import array
import math
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
font_petite = pygame.font.SysFont("Consolas", 24)
font = pygame.font.SysFont("Consolas", 36, bold=True)
font_grand = pygame.font.SysFont("Consolas", 70, bold=True)

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

# Animation d'apparition
echelle_rouge = 0.0
echelle_dore = 0.0

# Stats et Gameplay
score = 0
meilleur_score = 100
temps_limite = 30.0
temps_debut = 0

effets_tir = []
particules = []
impacts_rates = []
duree_shake = 0

tirs_totaux = 0
tirs_touches = 0
combo = 0
multiplicateur = 1

# Variables d'animation du fond et thèmes de couleur
grille_offset_y = 0
couleurs_fond = [
    ((10, 12, 28), (30, 45, 80)),  # Thème de base
    ((28, 10, 20), (80, 30, 60)),  # Violet
    ((10, 28, 15), (30, 80, 45)),  # Vert Cyber
    ((28, 20, 10), (80, 50, 30)),  # Ambre
    ((25, 10, 28), (70, 30, 80)),  # Électrique
]
index_couleur = 0

# --- CRÉATION DE LA SURFACE DU DRAPEAU DU CAMEROUN ---
largeur_drapeau, hauteur_drapeau = 24, 16
surface_drapeau = pygame.Surface(
    (largeur_drapeau, hauteur_drapeau), pygame.SRCALPHA
)

# Bandes verticales : Vert, Rouge, Jaune
l_bande = largeur_drapeau // 3
pygame.draw.rect(
    surface_drapeau, (0, 122, 61), (0, 0, l_bande, hauteur_drapeau)
)  # Vert
pygame.draw.rect(
    surface_drapeau,
    (206, 17, 38),
    (l_bande, 0, l_bande, hauteur_drapeau),
)  # Rouge
pygame.draw.rect(
    surface_drapeau,
    (252, 209, 22),
    (l_bande * 2, 0, l_bande, hauteur_drapeau),
)  # Jaune


# Étoile dorée au centre
def dessiner_etoile(surface, cx, cy, rayons_ex, rayon_in, couleur):
    points = []
    for i in range(10):
        r = rayons_ex if i % 2 == 0 else rayon_in
        angle = i * math.pi / 5 - math.pi / 2
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    pygame.draw.polygon(surface, couleur, points)


dessiner_etoile(
    surface_drapeau,
    largeur_drapeau / 2,
    hauteur_drapeau / 2,
    3.5,
    1.5,
    (252, 209, 22),
)

# Génération de la pluie de drapeaux
drapeaux = [
    {
        "x": random.randint(0, 1280),
        "y": random.randint(-720, 720),
        "vitesse": random.uniform(1.2, 3.0),
        "alpha": random.randint(100, 220),
    }
    for _ in range(40)
]


# --- FONCTION DE RENDU DU FOND AVEC PLUIE DE DRAPEAUX ---
def dessiner_fond(surface, offset_y, idx_couleur):
    c_base, c_grille = couleurs_fond[idx_couleur]

    # Dégradé dynamique
    for y in range(720):
        ratio = y / 720
        r = int(c_base[0] + ratio * 15)
        g = int(c_base[1] + ratio * 15)
        b = int(c_base[2] + ratio * 20)
        pygame.draw.line(surface, (r, g, b), (0, y), (1280, y))

    # Grille néon
    taille_case = 40
    for x in range(0, 1280, taille_case):
        pygame.draw.line(surface, c_grille, (x, 0), (x, 720), 1)

    offset_actuel = int(offset_y) % taille_case
    for y in range(offset_actuel, 720, taille_case):
        pygame.draw.line(surface, c_grille, (0, y), (1280, y), 1)

    # Rendu et déplacement de la pluie de drapeaux du Cameroun
    for d in drapeaux:
        d["y"] += d["vitesse"]
        if d["y"] > 720:
            d["y"] = random.randint(-40, -10)
            d["x"] = random.randint(0, 1280)

        temp_surface = surface_drapeau.copy()
        temp_surface.set_alpha(d["alpha"])
        surface.blit(temp_surface, (d["x"], d["y"]))


running = True
while running:
    temps_actuel = pygame.time.get_ticks()
    pos_souris = pygame.mouse.get_pos()

    grille_offset_y += 0.5

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # MENU
            if etat_jeu == "MENU":
                if 250 <= pos_souris[0] <= 470 and 360 <= pos_souris[1] <= 450:
                    difficulte = "Facile"
                    taille_cube = 100
                    taille_doree = 80
                elif 530 <= pos_souris[0] <= 750 and 360 <= pos_souris[1] <= 450:
                    difficulte = "Moyen"
                    taille_cube = 55
                    taille_doree = 45
                elif 810 <= pos_souris[0] <= 1030 and 360 <= pos_souris[1] <= 450:
                    difficulte = "Difficile"
                    taille_cube = 25
                    taille_doree = 20

                if 490 <= pos_souris[0] <= 790 and 510 <= pos_souris[1] <= 590:
                    score = 0
                    tirs_totaux = 0
                    tirs_touches = 0
                    combo = 0
                    multiplicateur = 1
                    index_couleur = 0
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
                    impacts_rates.clear()

                    etat_jeu = "JEU"
                    pygame.mouse.set_visible(False)

            # JEU
            elif etat_jeu == "JEU":
                son_tir.play()
                effets_tir.append({"pos": pos_souris, "rayon": 5})
                tirs_totaux += 1
                touche = False

                ancien_mult = multiplicateur

                # Clic cube doré
                if doree_active and rect_dore.collidepoint(pos_souris):
                    tirs_touches += 1
                    combo += 1
                    multiplicateur = 1 + (combo // 5)
                    score += 3 * multiplicateur
                    temps_limite += 1.0
                    doree_active = False
                    touche = True
                    duree_shake = 8
                    son_impact_verre.play()

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

                # Clic cube rouge
                if not touche and rect_rouge.collidepoint(pos_souris):
                    tirs_touches += 1
                    combo += 1
                    multiplicateur = 1 + (combo // 5)
                    score += 1 * multiplicateur
                    temps_limite += 0.5
                    touche = True
                    duree_shake = 5
                    son_impact_verre.play()

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

                # Changement de couleur + Shake au changement de combo
                if multiplicateur > ancien_mult:
                    index_couleur = (index_couleur + 1) % len(couleurs_fond)
                    duree_shake = 12

                # Tir raté
                if not touche:
                    combo = 0
                    multiplicateur = 1
                    index_couleur = 0
                    score = max(0, score - 1)
                    impacts_rates.append({"pos": pos_souris, "vie": 255})

                if score > meilleur_score:
                    meilleur_score = score

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and etat_jeu == "GAME_OVER":
                etat_jeu = "MENU"

    # --- RENDU ---
    surface_jeu = pygame.Surface((1280, 720))
    dessiner_fond(surface_jeu, grille_offset_y, index_couleur)

    shake_offset = (0, 0)
    if duree_shake > 0:
        shake_offset = (random.randint(-6, 6), random.randint(-6, 6))
        duree_shake -= 1

    if etat_jeu == "MENU":
        pygame.mouse.set_visible(True)

        t_titre_s = font_grand.render("AIM TRAINER 2D", True, (0, 0, 0))
        t_titre = font_grand.render("AIM TRAINER 2D", True, (0, 255, 200))
        surface_jeu.blit(t_titre_s, (373, 113))
        surface_jeu.blit(t_titre, (370, 110))

        panel_rec = pygame.Rect(440, 210, 400, 50)
        pygame.draw.rect(
            surface_jeu, (15, 20, 35), panel_rec, border_radius=12
        )
        pygame.draw.rect(
            surface_jeu, (255, 215, 0), panel_rec, width=2, border_radius=12
        )
        t_record = font.render(
            f"RECORD : {meilleur_score} PTS", True, (255, 215, 0)
        )
        surface_jeu.blit(t_record, (480, 220))

        boutons_diff = [
            ((250, 360), "Facile", (46, 204, 113), "Cubes XXL"),
            ((530, 360), "Moyen", (241, 196, 15), "Cubes Normal"),
            ((810, 360), "Difficile", (231, 76, 60), "Cubes Mini"),
        ]

        for pos, nom, couleur, desc in boutons_diff:
            rect_b = pygame.Rect(*pos, 220, 90)
            survol = rect_b.collidepoint(pos_souris)
            selectionne = difficulte == nom

            couleur_fond = (30, 40, 60) if survol else (20, 25, 40)
            pygame.draw.rect(surface_jeu, couleur_fond, rect_b, border_radius=15)

            epaisseur = 4 if (selectionne or survol) else 1
            c_bordure = couleur if (selectionne or survol) else (60, 75, 100)
            pygame.draw.rect(
                surface_jeu, c_bordure, rect_b, width=epaisseur, border_radius=15
            )

            txt = font.render(nom, True, couleur)
            txt_desc = font_petite.render(desc, True, (150, 160, 180))
            surface_jeu.blit(txt, (pos[0] + 30, pos[1] + 15))
            surface_jeu.blit(txt_desc, (pos[0] + 25, pos[1] + 55))

        rect_jouer = pygame.Rect(490, 510, 300, 80)
        survol_jouer = rect_jouer.collidepoint(pos_souris)
        c_jouer = (0, 255, 255) if survol_jouer else (0, 180, 220)

        pygame.draw.rect(
            surface_jeu,
            (10, 30, 50) if survol_jouer else (10, 20, 35),
            rect_jouer,
            border_radius=20,
        )
        pygame.draw.rect(
            surface_jeu, c_jouer, rect_jouer, width=3, border_radius=20
        )

        txt_jouer = font_grand.render("JOUER", True, c_jouer)
        surface_jeu.blit(txt_jouer, (545, 520))

    elif etat_jeu == "JEU":
        temps_ecoule = (temps_actuel - temps_debut) / 1000.0
        temps_restant = max(0.0, temps_limite - temps_ecoule)

        if temps_restant <= 0:
            etat_jeu = "GAME_OVER"

        if not doree_active and temps_actuel - dernier_pop_doree >= 3000:
            rect_dore.x = random.randint(0, 1280 - taille_doree)
            rect_dore.y = random.randint(0, 720 - taille_doree)
            doree_active = True
            echelle_dore = 0.0
            dernier_pop_doree = temps_actuel

        if doree_active and temps_actuel - dernier_pop_doree >= duree_doree:
            doree_active = False

        for imp in impacts_rates[:]:
            pygame.draw.circle(surface_jeu, (80, 90, 110), imp["pos"], 4)
            imp["vie"] -= 1
            if imp["vie"] <= 0:
                impacts_rates.remove(imp)

        echelle_rouge = min(1.0, echelle_rouge + 0.15)
        if doree_active:
            echelle_dore = min(1.0, echelle_dore + 0.15)

        w_r, h_r = int(taille_cube * echelle_rouge), int(
            taille_cube * echelle_rouge
        )
        off_x_r, off_y_r = (taille_cube - w_r) // 2, (taille_cube - h_r) // 2
        r_dessin = pygame.Rect(
            rect_rouge.x + off_x_r, rect_rouge.y + off_y_r, w_r, h_r
        )
        pygame.draw.rect(
            surface_jeu, (235, 47, 6), r_dessin, border_radius=8
        )
        pygame.draw.rect(
            surface_jeu, (255, 255, 255), r_dessin, width=2, border_radius=8
        )

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
            pygame.draw.rect(
                surface_jeu, (255, 215, 0), d_dessin, border_radius=8
            )
            pygame.draw.rect(
                surface_jeu, (255, 255, 255), d_dessin, width=2, border_radius=8
            )

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
                surface_jeu.blit(s, (p["x"], p["y"]))

        for effet in effets_tir[:]:
            pygame.draw.circle(
                surface_jeu, (255, 230, 0), effet["pos"], int(effet["rayon"]), 2
            )
            effet["rayon"] += 2
            if effet["rayon"] > 25:
                effets_tir.remove(effet)

        sx, sy = pos_souris
        pygame.draw.circle(surface_jeu, (0, 255, 255), (sx, sy), 12, 2)
        pygame.draw.line(
            surface_jeu, (0, 255, 255), (sx - 18, sy), (sx + 18, sy), 2
        )
        pygame.draw.line(
            surface_jeu, (0, 255, 255), (sx, sy - 18), (sx, sy + 18), 2
        )

        surface_jeu.blit(
            font.render(f"SCORE : {score}", True, (255, 255, 255)), (20, 20)
        )
        surface_jeu.blit(
            font_petite.render(f"MODE : {difficulte}", True, (150, 160, 180)),
            (20, 65),
        )
        if multiplicateur > 1:
            surface_jeu.blit(
                font.render(
                    f"COMBO x{multiplicateur} 🔥", True, (255, 120, 0)
                ),
                (20, 100),
            )

        surface_jeu.blit(
            font.render(f"RECORD : {meilleur_score}", True, (255, 215, 0)),
            (500, 20),
        )
        surface_jeu.blit(
            font.render(f"TEMPS : {temps_restant:.1f}s", True, (255, 220, 0)),
            (1000, 20),
        )

    elif etat_jeu == "GAME_OVER":
        pygame.mouse.set_visible(True)
        precision = (
            (tirs_touches / tirs_totaux * 100) if tirs_totaux > 0 else 0.0
        )

        panel_go = pygame.Rect(340, 140, 600, 420)
        pygame.draw.rect(surface_jeu, (15, 20, 35), panel_go, border_radius=20)
        pygame.draw.rect(
            surface_jeu, (231, 76, 60), panel_go, width=2, border_radius=20
        )

        t_over = font_grand.render("FIN DE PARTIE", True, (231, 76, 60))
        t_final = font.render(f"Score Final : {score}", True, (255, 255, 255))
        t_prec = font.render(
            f"Précision   : {precision:.1f}%", True, (0, 255, 200)
        )
        t_rec = font.render(
            f"Record Jack : {meilleur_score}", True, (255, 215, 0)
        )
        t_restart = font_petite.render(
            "Appuie sur ESPACE pour continuer", True, (150, 160, 180)
        )

        surface_jeu.blit(t_over, (430, 180))
        surface_jeu.blit(t_final, (450, 280))
        surface_jeu.blit(t_prec, (450, 330))
        surface_jeu.blit(t_rec, (450, 380))
        surface_jeu.blit(t_restart, (420, 470))

    screen.blit(surface_jeu, shake_offset)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()