Organisation du programme:
Le programme est divisé en deux composantes essentielles;
un fichier logique.py et affichageessai4.py

ATTENTION! Afin de lancer le jeu, il faut lancer affichageessai4.py


le fichier complémentaire logique.py contient des fonctions utiles au bon fonctionnement de la boucle logique du jeu, plus précisément, il contient des fonctions de génération de position 
aléatoires et toutes les fonctions d'opérations sur les tuiles du jeu comme la vérification de si l'aventurier peut accédez à une salle où non, et
une fonction de rotation pour les tuiles qui changera les valeurs internes correspondants à l'orientation d'une tuile donnée sans changer son nombre d'ouverture ou fermeture


le fichier affichageessai4.py contient une fonction de génération de donjon aléatoires, des fonctions d'affichage, des fonctions pour gérer le scénario de fin de jeu, une fonction
boucle_clic qui constituent le gros de la boucle logique du jeu et fait appel à certaines des fonctions dans logique.py, des fonctions d'affichages de menus et main(), qui est appelé
au démarrage du programme et permet le bon fonctionnement des menus et copie l'état de départ du donjon pour le retour en arrière en appuyant sur R. 



Déroulement du jeu:
Au lancement du programme, on remarque deux boutons à l'écran;
-Jouer
-Labyrinthe

Le bouton Jouer est un générateur de niveau 
aléatoire qui prompte le joueur dans le
terminal à y inscrire le nombre de lignes, 
colonnes, et la taille des images du labyrinthe généré. 

Le bouton Labyrinthe amènes le joueur à un deuxième menu, qui lui montre 5 boutons
-Labyrinthe (1-4)
-Retour Menu
Le bouton Retour Menu est assez intuitif, il renvoie le joueur
vers le premier menu de choix entre les boutons 'Jouer' et 'Labyrinthe'
Les boutons Labyrinthes numérotés de 1 a 4. Ils amènent le joueur
à des donjons conçus au préalables. La position de départ de l'aventurier
et des dragons ne change pas entre chaque régénération. Cependant,
la position du trésor est susceptible de changer entre chaque régénération.

Le jeu, une fois lancé, démarre sur une phase de rotation, où le joueur peut cliquer sur n'importe quelle tuile dans l'écran;
Après avoir cliqué sur une tuile, cette tuile effectue une rotation de 90° en sens horaire, et la phase de rotation se termine.
La phase qui suit est une phase de déplacement. Lors d'une phase de déplacement, le joueur peut déplacer l'aventurier vers 
une autre tuile en utilisant les touches fléchés sur son clavier, si il n'existe aucun mur entre la tuile où l'aventurier se trouve 
et celle où le joueur souhaite le faire se déplacer. 
Après un déplacement réussi de l'aventurier, le jeu revient à une phase de rotation. Cette boucle basique peut continuer
jusqu'à ce que l'aventurier entre en contact avec un dragon de niveau supérieur au sien, ou tue tous les dragons dans le donjon. 
Si l'aventurier est incapable de bouger, car il est entouré par des murs, il est possible de sauter la phase de déplacement en appuyant
sur la barre d'espace; cela n'est pas vrai de la phase de rotation. 
De plus, si le joueur décide qu'il ne veut pas arrêter de jouer, mais veut recommencer le donjon au point de départ, il peut appuyer sur R 
sur son clavier pour revenir au point de départ du donjon. A cette occasion, l'aventurier reviendra au point des départ, les salles tournées reviendrons à
leur orientation de départ, et les dragons morts seront régénérés.





Mentions de sources:

Dragon sprite:
Aucun copyright (license CC0)
Lien vers le bien digital d'origine;
https://opengameart.org/content/shmup-dragon 

Knight sprite:
Aucun copyright (license CC0)
Lien vers le bien digital d'origine;
https://opengameart.org/content/pixel-knight-32x32

Sprite du tresor réalisé par Alexis Gaudiere

Floor sprite:
Protégé sous une license CC 3.0 et plus récent; actuelle license plus récente:
https://creativecommons.org/licenses/by/4.0/
Auteur d'origine; Jordan Irwin (AntumDeluge)
Sprite modifié par Alexis Gaudiere, les modifications étant l'ajout de murs dans le sprite
Lien canonique:
https://opengameart.org/node/108812