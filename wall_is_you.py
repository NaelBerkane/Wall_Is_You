import fltk
import copy
import os
import tkinter.filedialog as fd
from random import randint, choice
from time import sleep

"""
Jeu Wall Is You
Projet SAE - Gestion de donjon, déplacement tactique et sauvegarde.
"""

# --- CONSTANTES ---
HAUT = 0
DROITE = 1
BAS = 2
GAUCHE = 3

MUR = 1
VIDE = 0

# Correspondance entre la configuration des murs (tuple) et le caractère visuel
MAPPING_SITES = {
    (0, 0, 0, 0): " ", (0, 0, 0, 1): "╸", (0, 0, 1, 0): "╻", (0, 0, 1, 1): "╗",
    (0, 1, 0, 0): "╺", (0, 1, 0, 1): "═", (0, 1, 1, 0): "╔", (0, 1, 1, 1): "╦",
    (1, 0, 0, 0): "╹", (1, 0, 0, 1): "╝", (1, 0, 1, 0): "║", (1, 0, 1, 1): "╣",
    (1, 1, 0, 0): "╚", (1, 1, 0, 1): "╩", (1, 1, 1, 0): "╠", (1, 1, 1, 1): "╬"
}

# Dictionnaire inverse pour retrouver le tuple à partir du caractère
CHAR_TO_TUILE = {v: k for k, v in MAPPING_SITES.items()}


#############################################################################
#                            PARTIE LOGIQUE                                 #
#############################################################################

def generer_donjon_aleatoire(cols, lignes):
    """
    Génère une grille de donjon aléatoire.
    :param cols: Nombre de colonnes
    :param lignes: Nombre de lignes
    :return: Matrice (liste de listes) représentant le donjon
    """
    donjon = []
    for x in range(cols):
        colonne = []
        for y in range(lignes):
            tuile = [MUR] * 4
            # On s'assure qu'il y a au moins une ouverture par case
            while VIDE not in tuile:
                tuile = [randint(0, 1) for _ in range(4)]
            colonne.append(tuile)
        donjon.append(colonne)
    return donjon


def position_aleatoire(cols, lignes):
    """Renvoie des coordonnées (x, y) aléatoires dans la grille."""
    return (randint(0, cols - 1), randint(0, lignes - 1))


def generer_positions_entites(donjon):
    """
    Génère les positions de départ uniques pour le héros et les dragons.
    :return: Liste de positions [Heros, Dragon1, Dragon2, Dragon3]
    """
    cols = len(donjon)
    lignes = len(donjon[0])
    
    # Sécurité si le donjon est trop petit
    if cols * lignes < 4: return [(0, 0)] * 4
    
    positions = []
    while len(positions) < 4:
        pos = position_aleatoire(cols, lignes)
        if pos not in positions:
            positions.append(pos)
    return positions


def tourner_tuile_horaire(donjon, x, y):
    """
    Tourne la case (x, y) de 90 degrés dans le sens horaire.
    Modifie le donjon en place.
    """
    tuile = donjon[x][y]
    # Décalage des indices : Gauche->Haut, Haut->Droite, etc.
    nouvelle_tuile = [tuile[GAUCHE], tuile[HAUT], tuile[DROITE], tuile[BAS]]
    donjon[x][y] = nouvelle_tuile


def verifier_deplacement(donjon, x, y, direction):
    """
    Vérifie si un déplacement est possible depuis (x, y) vers une direction.
    :return: (True/False, nouveau_x, nouveau_y)
    """
    dx, dy = 0, 0
    oppose = -1 
    
    # Définition du vecteur de mouvement et du mur opposé (arrivée)
    if direction == HAUT: dy = -1; oppose = BAS
    elif direction == BAS: dy = 1; oppose = HAUT
    elif direction == GAUCHE: dx = -1; oppose = DROITE
    elif direction == DROITE: dx = 1; oppose = GAUCHE

    nx, ny = x + dx, y + dy
    
    # Vérifie si on sort de la grille
    if not (0 <= nx < len(donjon) and 0 <= ny < len(donjon[0])): return False, x, y

    case_actuelle = donjon[x][y]
    case_arrivee = donjon[nx][ny]
    
    # Le passage est ouvert si le mur de départ ET le mur d'arrivée sont vides (0)
    if case_actuelle[direction] == VIDE and case_arrivee[oppose] == VIDE:
        return True, nx, ny
    return False, x, y


def direction_entre_cases(depart, arrivee):
    """
    Renvoie la direction (HAUT, BAS...) pour aller d'une case A à une case B adjacente.
    """
    dx = arrivee[0] - depart[0]
    dy = arrivee[1] - depart[1]
    
    if dx == 1: return DROITE
    if dx == -1: return GAUCHE
    if dy == 1: return BAS
    if dy == -1: return HAUT
    return -1


def deplacer_dragons_ia(donjon, positions):
    """
    Déplace chaque dragon vivant vers une case adjacente valide au hasard.
    Les dragons ne peuvent pas aller sur une case occupée par un autre dragon.
    """
    for i in range(1, 4): # Indices 1, 2, 3 = Dragons
        if positions[i] == (-1, -1): continue # Dragon mort
        
        x, y = positions[i]
        coups_possibles = []
        
        # Test des 4 directions
        for direction in [HAUT, DROITE, BAS, GAUCHE]:
            possible, nx, ny = verifier_deplacement(donjon, x, y, direction)
            
            # Vérification : case libre d'autres dragons
            libre = True
            for k in range(1, 4):
                if i != k and positions[k] == (nx, ny): libre = False
            
            if possible and libre: coups_possibles.append((nx, ny))
        
        # Choix aléatoire parmi les coups possibles
        if coups_possibles: positions[i] = choice(coups_possibles)


# --- GESTION FICHIERS ---

def charger_niveau_fichier(chemin_fichier):
    """
    Lit un fichier texte pour charger un niveau ou une sauvegarde.
    :return: (donjon, positions, niveau_hero, pos_diamant)
    """
    if not os.path.exists(chemin_fichier):
        print("Fichier " + chemin_fichier + " introuvable.")
        return None, None, 1, (-1, -1)

    donjon_transitoire = []
    entites_lignes = []
    
    with open(chemin_fichier, 'r', encoding='utf-8') as f:
        lignes = f.readlines()

    for ligne in lignes:
        ligne = ligne.rstrip('\n')
        if not ligne: continue
        
        # Si la ligne commence par une lettre (A, D, T), c'est une entité
        if ligne[0] in ['A', 'D', 'T']:
            entites_lignes.append(ligne)
        else:
            # Sinon c'est une ligne de la grille
            rangee = []
            for char in ligne:
                tuile = CHAR_TO_TUILE.get(char, (1, 1, 1, 1))
                rangee.append(list(tuile))
            donjon_transitoire.append(rangee)

    # Inversion des axes (Lecture ligne par ligne -> matrice x,y)
    lignes_count = len(donjon_transitoire)
    cols_count = len(donjon_transitoire[0]) if lignes_count > 0 else 0
    donjon = [[donjon_transitoire[y][x] for y in range(lignes_count)] for x in range(cols_count)]

    # Initialisation vide
    positions = [(-1, -1), (-1, -1), (-1, -1), (-1, -1)]
    niveau_hero = 1
    pos_diamant = (-1, -1)
    
    # Traitement des entités
    for entite in entites_lignes:
        parts = entite.split()
        type_entite = parts[0]
        lig = int(parts[1])
        col = int(parts[2])
        
        if type_entite == 'A': # Aventurier
            positions[0] = (col, lig)
            if len(parts) > 3: niveau_hero = int(parts[3])
            
        elif type_entite == 'D': # Dragon
            niveau = int(parts[3])
            if 1 <= niveau <= 3:
                positions[niveau] = (col, lig)
                
        elif type_entite == 'T': # Trésor
            pos_diamant = (col, lig)
            
    return donjon, positions, niveau_hero, pos_diamant


def sauvegarder_niveau_fichier(chemin_fichier, donjon, positions, niveau_hero, pos_diamant):
    """
    Sauvegarde l'état complet du jeu dans un fichier texte.
    """
    with open(chemin_fichier, 'w', encoding='utf-8') as f:
        # Écriture de la grille
        cols = len(donjon)
        lignes = len(donjon[0])
        for y in range(lignes):
            ligne_str = ""
            for x in range(cols):
                tuile = tuple(donjon[x][y])
                ligne_str += MAPPING_SITES.get(tuile, "╬")
            f.write(ligne_str + "\n")
        
        # Écriture du Héros
        hx, hy = positions[0]
        if hx != -1: 
            f.write("A " + str(hy) + " " + str(hx) + " " + str(niveau_hero) + "\n")
        
        # Écriture des Dragons
        for i in range(1, 4):
            dx, dy = positions[i]
            if dx != -1: 
                f.write("D " + str(dy) + " " + str(dx) + " " + str(i) + "\n")
            
        # Écriture du Trésor
        tx, ty = pos_diamant
        if tx != -1: 
            f.write("T " + str(ty) + " " + str(tx) + "\n")

    print("Sauvegarde effectuée !")


#############################################################################
#                          PARTIE AFFICHAGE & JEU                           #
#############################################################################

OFFSET_X = 50
OFFSET_Y = 50

# Dictionnaire des images
IMAGES_TUILES = {
    (0, 0, 0, 0): "╬.gif", (0, 0, 0, 1): "╠.gif", (0, 0, 1, 0): "╩.gif",
    (0, 1, 0, 0): "╣.gif", (1, 0, 0, 0): "╦.gif", (1, 0, 0, 1): "╔.gif",
    (1, 0, 1, 0): "═.gif", (1, 1, 0, 0): "╗.gif", (0, 0, 1, 1): "╚.gif",
    (0, 1, 0, 1): "║.gif", (0, 1, 1, 0): "╝.gif", (0, 1, 1, 1): "╨.gif",
    (1, 0, 1, 1): "╞.gif", (1, 1, 0, 1): "╥.gif", (1, 1, 1, 0): "╡.gif",
    (1, 1, 1, 1): "╬.gif"
}


def recuperer_nom_image(tuile):
    """Retourne le nom du fichier image correspondant à la configuration du mur."""
    return IMAGES_TUILES.get(tuple(tuile), "╬.gif")


def dessiner_donjon(donjon, taille_px):
    """Dessine toutes les cases de la grille."""
    for x in range(len(donjon)):
        for y in range(len(donjon[x])):
            px = OFFSET_X + x * taille_px + taille_px // 2
            py = OFFSET_Y + y * taille_px + taille_px // 2
            fltk.image(px, py, recuperer_nom_image(donjon[x][y]), taille_px, taille_px)


def dessiner_entite(x, y, image, taille_px):
    """Dessine une entité (perso, objet) à une position donnée."""
    if x == -1: return
    px = OFFSET_X + x * taille_px + taille_px // 2
    py = OFFSET_Y + y * taille_px + taille_px // 2
    fltk.image(px, py, image, taille_px - 10, taille_px - 10)


def convertir_grille_vers_pixels(pos, taille_px):
    """
    Fonction utilitaire pour convertir les coordonnées grille (col, lig)
    en coordonnées pixels (x, y) pour l'affichage fltk.
    """
    return (OFFSET_X + pos[0] * taille_px + taille_px // 2,
            OFFSET_Y + pos[1] * taille_px + taille_px // 2)


def dessiner_chemin_planifie(chemin, depart, taille_px):
    """Dessine la ligne violette représentant le chemin futur du héros."""
    if not chemin: return
    
    precedent = depart
    for actuel in chemin:
        p1 = convertir_grille_vers_pixels(precedent, taille_px)
        p2 = convertir_grille_vers_pixels(actuel, taille_px)
        
        fltk.ligne(p1[0], p1[1], p2[0], p2[1], couleur="purple", epaisseur=4)
        fltk.cercle(p2[0], p2[1], 4, couleur="purple", remplissage="purple")
        precedent = actuel


def dessiner_interface(phase, niveau_hero, tresor):
    """Affiche le HUD (texte, état du jeu)."""
    fltk.texte(20, 20, "Niveau: " + str(niveau_hero), couleur="blue", taille=12)
    if tresor: fltk.texte(100, 20, "TRÉSOR OK!", couleur="gold", taille=12)
    
    if phase == "ROTATION":
        fltk.texte(250, 20, "PHASE 1 : ROTATION (Clic Gauche)", couleur="green", taille=12)
    else:
        fltk.texte(250, 20, "PHASE 2 : TRACER (Clic) -> VALIDER (Entrée)", couleur="red", taille=12)
    
    fltk.texte(20, 480, "R:Restart | Esc:Menu | S:Save | Entrée:Valider", couleur="grey", taille=10)


def rafraichir_ecran(donjon, taille_px, positions, phase, niveau, pos_diamant, tresor, chemin_planifie):
    """Fonction principale de dessin : efface tout et redessine la scène."""
    fltk.efface_tout()
    dessiner_donjon(donjon, taille_px)
    
    # Chemin violet uniquement en phase de déplacement
    if phase == "DEPLACEMENT" and chemin_planifie:
        dessiner_chemin_planifie(chemin_planifie, positions[0], taille_px)
        
    dessiner_entite(pos_diamant[0], pos_diamant[1], "tresor.gif", taille_px)
    
    # Dessin des dragons
    dragons_imgs = ["shmupdragonlvone.gif", "shmupdragonlvtwo.gif", "shmupdragonlvthree.gif"]
    for i in range(3):
        idx_pos = i + 1
        if idx_pos < len(positions):
            dessiner_entite(positions[idx_pos][0], positions[idx_pos][1], dragons_imgs[i], taille_px)
            
    dessiner_entite(positions[0][0], positions[0][1], "knight.gif", taille_px)
    dessiner_interface(phase, niveau, tresor)
    fltk.mise_a_jour()


def ecran_fin(message, sous_message, couleur_titre, victoire):
    """Affiche l'écran de victoire ou de défaite."""
    fltk.efface_tout()
    fltk.texte(250, 200, message, couleur=couleur_titre, taille=30, ancrage="center")
    fltk.texte(250, 300, sous_message, couleur="black", taille=14, ancrage="center")
    
    if victoire:
        try: fltk.image(250, 350, "evilmeowl.gif", 50, 50)
        except: fltk.texte(250, 350, "BRAVO !", couleur="gold", taille=20, ancrage="center")
            
    fltk.texte(250, 450, "Cliquez pour retourner au menu", couleur="grey", taille=10, ancrage="center")
    fltk.mise_a_jour()
    fltk.attend_clic_gauche()


# --- LOGIQUE PRINCIPALE DU JEU ---

def spawn_tresor(cols, lignes, positions_interdites):
    """Trouve une position libre aléatoire pour le trésor."""
    while True:
        pos = (randint(0, cols - 1), randint(0, lignes - 1))
        if pos not in positions_interdites: return pos


def gestion_collisions(pos_hero, positions_dragons, niveau_hero, pos_diamant, tresor_recupere):
    """
    Gère les interactions entre le héros, le trésor et les dragons.
    Retourne : (Statut, Info, Tresor_Recup, Pos_Diamant)
    """
    # Ramassage du trésor
    if pos_hero == pos_diamant:
        tresor_recupere = True
        pos_diamant = (-1, -1) 
        
    # Combat contre les dragons
    for i in range(1, 4):
        if pos_hero == positions_dragons[i]:
            # Victoire du héros
            if niveau_hero >= i:
                positions_dragons[i] = (-1, -1)
                # Si c'est le boss (niv 3), on gagne la partie
                if i == 3: return "GAGNE", niveau_hero, tresor_recupere, pos_diamant
                niveau_hero += 1 
            # Défaite du héros
            else:
                return "PERDU", i, tresor_recupere, pos_diamant
                
    return "CONTINUE", niveau_hero, tresor_recupere, pos_diamant


def jouer_niveau(donjon, taille_px, positions, niveau_depart=1, diamant_sauvegarde=None):
    """Boucle principale d'une partie (un niveau)."""
    phase = "ROTATION"
    niveau_hero = niveau_depart
    tresor_recupere = False
    chemin_planifie = [] 
    
    cols = len(donjon); lignes = len(donjon[0])
    
    # Gestion du diamant (chargé ou nouveau)
    if diamant_sauvegarde is not None and diamant_sauvegarde != (-1, -1):
        pos_diamant = diamant_sauvegarde
    else:
        pos_diamant = spawn_tresor(cols, lignes, positions)

    rafraichir_ecran(donjon, taille_px, positions, phase, niveau_hero, pos_diamant, tresor_recupere, chemin_planifie)

    while True:
        ev = fltk.donne_ev()
        if not ev:
            fltk.mise_a_jour()
            continue

        type_event = fltk.type_ev(ev)
        if type_event == "Quitte": return "STOP"

        # --- GESTION CLAVIER ---
        if type_event == "Touche":
            touche = fltk.touche(ev)
            if touche in ['r', 'R']: return "RESTART"
            if touche == "Escape": return "MENU"
            
            # Sauvegarde (Touche S)
            if touche in ['s', 'S']:
                sauvegarder_niveau_fichier("sauvegarde.txt", donjon, positions, niveau_hero, pos_diamant)
                fltk.texte(10, 465, "Sauvegarde effectuée !", couleur="blue", taille=10)
                fltk.mise_a_jour()
                sleep(1)

            # Validation du chemin (Entrée)
            if touche == "Return" and phase == "DEPLACEMENT" and chemin_planifie:
                # 1. Mouvement du héros case par case
                for etape in chemin_planifie:
                    positions[0] = etape 
                    statut, info, tresor_recupere, pos_diamant = gestion_collisions(positions[0], positions, niveau_hero, pos_diamant, tresor_recupere)
                    
                    if isinstance(info, int): niveau_hero = info
                    
                    rafraichir_ecran(donjon, taille_px, positions, phase, niveau_hero, pos_diamant, tresor_recupere, [])
                    fltk.attente(0.15) 
                    
                    if statut == "GAGNE":
                        ecran_fin("VICTOIRE !", "Dragon final vaincu !", "gold", True)
                        return "MENU"
                    elif statut == "PERDU":
                        ecran_fin("GAME OVER", "Tué par un dragon niveau " + str(info), "red", False)
                        return "MENU"
                
                
                deplacer_dragons_ia(donjon, positions)
                
                # Mise à jour visuelle et vérification post-mouvement IA
                rafraichir_ecran(donjon, taille_px, positions, phase, niveau_hero, pos_diamant, tresor_recupere, [])
                fltk.attente(0.2) 
                
                statut, info, tresor_recupere, pos_diamant = gestion_collisions(positions[0], positions, niveau_hero, pos_diamant, tresor_recupere)
                if isinstance(info, int): niveau_hero = info
                
                if statut == "PERDU":
                    ecran_fin("GAME OVER", "Le dragon niv " + str(info) + " vous a eu !", "red", False)
                    return "MENU"
                elif statut == "GAGNE":
                    ecran_fin("VICTOIRE !", "Boss vaincu en défense !", "gold", True)
                    return "MENU"

                # Reset pour le tour suivant
                chemin_planifie = []
                phase = "ROTATION"
                rafraichir_ecran(donjon, taille_px, positions, phase, niveau_hero, pos_diamant, tresor_recupere, chemin_planifie)

            # Passer son tour (Espace)
            if touche == "space" and phase == "DEPLACEMENT" and not chemin_planifie:
                 # Le héros ne bouge pas, les dragons oui
                 deplacer_dragons_ia(donjon, positions)
                 
                 rafraichir_ecran(donjon, taille_px, positions, phase, niveau_hero, pos_diamant, tresor_recupere, [])
                 fltk.attente(0.2)
                 
                 statut, info, tresor_recupere, pos_diamant = gestion_collisions(positions[0], positions, niveau_hero, pos_diamant, tresor_recupere)
                 if isinstance(info, int): niveau_hero = info
                 
                 if statut == "PERDU":
                    ecran_fin("GAME OVER", "Le dragon niv " + str(info) + " vous a eu !", "red", False)
                    return "MENU"
                 elif statut == "GAGNE":
                    ecran_fin("VICTOIRE !", "Boss vaincu en défense !", "gold", True)
                    return "MENU"
                    
                 phase = "ROTATION"
                 rafraichir_ecran(donjon, taille_px, positions, phase, niveau_hero, pos_diamant, tresor_recupere, chemin_planifie)

        #  GESTION SOURIS 
        elif type_event == "ClicGauche":
            cx, cy = fltk.abscisse(ev), fltk.ordonnee(ev)
            ix = (cx - OFFSET_X) // taille_px
            iy = (cy - OFFSET_Y) // taille_px
            
            if 0 <= ix < cols and 0 <= iy < lignes:
                if phase == "ROTATION":
                    tourner_tuile_horaire(donjon, ix, iy)
                    phase = "DEPLACEMENT"
                    rafraichir_ecran(donjon, taille_px, positions, phase, niveau_hero, pos_diamant, tresor_recupere, chemin_planifie)
                
                elif phase == "DEPLACEMENT":
                    case_cliquee = (ix, iy)
                    dernier_point = chemin_planifie[-1] if chemin_planifie else positions[0]
                    
                    # Annulation du dernier point si on clique sur l'avant-dernier
                    avant_dernier = chemin_planifie[-2] if len(chemin_planifie) > 1 else positions[0]
                    if case_cliquee == avant_dernier and chemin_planifie:
                        chemin_planifie.pop()
                    else:
                        # Ajout d'un point si adjacent et accessible
                        dist = abs(case_cliquee[0] - dernier_point[0]) + abs(case_cliquee[1] - dernier_point[1])
                        if dist == 1 and case_cliquee != positions[0]:
                            direction = direction_entre_cases(dernier_point, case_cliquee)
                            possible, _, _ = verifier_deplacement(donjon, dernier_point[0], dernier_point[1], direction)
                            if possible: chemin_planifie.append(case_cliquee)
                            
                    rafraichir_ecran(donjon, taille_px, positions, phase, niveau_hero, pos_diamant, tresor_recupere, chemin_planifie)


def afficher_bouton(x1, y1, x2, y2, couleur, texte):
    """Dessine un bouton coloré avec du texte centré."""
    fltk.rectangle(x1, y1, x2, y2, remplissage=couleur)
    mx = (x1 + x2) // 2
    my = (y1 + y2) // 2
    fltk.texte(mx, my, texte, taille=18, couleur="black", ancrage="center")


def menu_principal():
    """Affiche le menu d'accueil du jeu."""
    fltk.efface_tout()
    fltk.texte(250, 50, "WALL IS YOU", taille=32, couleur="red", ancrage="center")
    
    afficher_bouton(150, 200, 350, 260, "red", "JOUER")
    afficher_bouton(150, 300, 350, 360, "cyan", "CHARGER")
    
    fltk.texte(250, 450, "Fermer la fenêtre pour quitter", taille=10, couleur="grey", ancrage="center")
    fltk.mise_a_jour()
    
    while True:
        ev = fltk.donne_ev()
        if ev:
            if fltk.type_ev(ev) == "Quitte": return 0
            if fltk.type_ev(ev) == "ClicGauche":
                x, y = fltk.abscisse(ev), fltk.ordonnee(ev)
                if 150 <= x <= 350:
                    if 200 <= y <= 260: return 1
                    if 300 <= y <= 360: return 2
        fltk.mise_a_jour()


def menu_choix_labyrinthe():
    """Affiche le menu de sélection de niveau ou de fichier."""
    fltk.efface_tout()
    fltk.texte(250, 40, "CHOIX DU NIVEAU", taille=24, couleur="blue", ancrage="center")
    
    # Colonne Gauche
    afficher_bouton(30, 120, 220, 180, "lightgreen", "Niveau 1")
    afficher_bouton(30, 200, 220, 260, "orange", "Niveau 2")
    afficher_bouton(30, 350, 220, 410, "violet", "Fichier...") 

    # Colonne Droite
    afficher_bouton(280, 120, 470, 180, "chartreuse3", "Niveau 3")
    afficher_bouton(280, 200, 470, 260, "gold3", "Sauvegarde")
    afficher_bouton(280, 350, 470, 410, "red", "Retour")
    
    fltk.mise_a_jour()
    
    while True:
        ev = fltk.donne_ev()
        if ev:
            if fltk.type_ev(ev) == "Quitte": return 0
            if fltk.type_ev(ev) == "ClicGauche":
                x, y = fltk.abscisse(ev), fltk.ordonnee(ev)
                
                # Zone Gauche
                if 30 <= x <= 220:
                    if 120 <= y <= 180: return 1 
                    if 200 <= y <= 260: return 2  
                    if 350 <= y <= 410:           
                        filename = fd.askopenfilename(title="Choisir un niveau", filetypes=[("Fichiers texte", "*.txt"), ("Tous", "*.*")])
                        if filename: return filename

                # Zone Droite
                if 280 <= x <= 470:
                    if 120 <= y <= 180: return 3  
                    if 200 <= y <= 260: return 99 
                    if 350 <= y <= 410: return -1 

        fltk.mise_a_jour()


def main():
    """Fonction principale : lance la fenêtre et gère la boucle des menus."""
    fltk.cree_fenetre(500, 500)
    
    while True:
        choix_menu = menu_principal()
        if choix_menu == 0: break 
        
        donjon_init = []
        positions_init = []
        taille_px = 64
        niveau_depart = 1
        diamant_depart = None

        if choix_menu == 1: # Mode aléatoire
            fltk.efface_tout(); fltk.texte(250, 250, "Regardez le terminal...", taille=20, ancrage="center"); fltk.mise_a_jour()
            print("-" * 30)
            try:
                c = int(input("Colonnes : ")); l = int(input("Lignes : ")); t = input("Taille px (Entrée pour 32) : ")
                taille_px = int(t) if t else 32
                donjon_init = generer_donjon_aleatoire(c, l)
                positions_init = generer_positions_entites(donjon_init)
            except ValueError:
                print("Erreur de saisie."); continue

        elif choix_menu == 2: # Mode Chargement
            choix_lab = menu_choix_labyrinthe()
            if choix_lab == 0: break
            if choix_lab == -1: continue

            nom_fichier = ""
            if choix_lab == 99: nom_fichier = "sauvegarde.txt"
            elif isinstance(choix_lab, str): nom_fichier = choix_lab 
            else: 
                nom_fichier = "niveau" + str(choix_lab) + ".txt"

            donjon_init, positions_init, niveau_depart, diamant_depart = charger_niveau_fichier(nom_fichier)
            
            if donjon_init is None:
                fltk.efface_tout()
                fltk.texte(250, 250, "Fichier introuvable !", couleur="red", ancrage="center")
                fltk.mise_a_jour()
                sleep(2)
                continue

        # Lancement de la partie
        if donjon_init and positions_init:
            while True:
                d_en_cours = copy.deepcopy(donjon_init)
                p_en_cours = copy.deepcopy(positions_init)
                
                resultat = jouer_niveau(d_en_cours, taille_px, p_en_cours, niveau_depart, diamant_depart)
                
                if resultat == "STOP": fltk.ferme_fenetre(); return
                elif resultat == "MENU": break
                elif resultat == "RESTART": continue
                
    fltk.ferme_fenetre()

if __name__ == "__main__":
    main()