"""
Exercice : Snake asynchrone dans le terminal
Contexte
Tu vas développer un Snake jouable dans le terminal, sans aucune bibliothèque graphique, uniquement avec curses (l'affichage) et asyncio (la boucle de jeu + la lecture du clavier en simultané).

Le principe : un serpent se déplace en continu sur une grille carrée. Le joueur change sa direction avec les flèches du clavier. S'il mange la nourriture (0), il grandit et une nouvelle nourriture apparaît. S'il se mord la queue, c'est game over.

Prérequis
Sous Windows : pip install windows-curses
Connaître les bases de asyncio (coroutines, await, event loop)
Un terminal suffisamment grand (au moins 20 colonnes x 20 lignes)
Cahier des charges
Le jeu doit respecter les règles suivantes :

La grille : un plateau carré de taille SIZE (configurable), 
    délimité par une bordure (par exemple avec les caractères ╔ ╗ ╚ ╝ ═ ║).
Le serpent : représenté comme une suite de coordonnées (x, y), affiché avec le caractère X. 
    Il démarre avec une longueur de 5.
La nourriture : une position (x, y) tirée aléatoirement sur une case libre (pas déjà occupée par le serpent), 
    affichée avec le caractère 0.
Le déplacement : le serpent avance automatiquement toutes les 200 ms dans sa direction courante. 
    Quand il sort d'un bord, il réapparaît de l'autre côté (effet "Pac-Man").
Les contrôles : les flèches du clavier (haut/bas/gauche/droite) changent la direction du serpent, 
    pendant que le serpent continue de bouger tout seul 
    — la lecture clavier ne doit jamais bloquer l'affichage.
Manger : quand la tête du serpent atteint la nourriture, 
    le serpent grandit d'une case et une nouvelle nourriture apparaît ailleurs.
Game over : quand la tête du serpent touche une autre partie de son propre corps, 
    le jeu s'arrête et affiche GAME OVER.
Quitter : la touche Echap doit permettre d'arrêter le programme proprement.

Étapes 
Tu peux avancer progressivement plutôt que tout écrire d'un coup :

Étape 1 — Affichage statique : dessine la bordure de la grille avec curses, sans logique de jeu.
Étape 2 — Le serpent immobile : affiche un serpent de 5 cases et une nourriture placée aléatoirement.
Étape 3 — Le mouvement automatique : fais avancer le serpent tout seul dans une direction fixe, 
    en boucle, avec asyncio.sleep(0.2).
Étape 4 — Les contrôles clavier : ajoute une deuxième coroutine (ou tâche via run_in_executor) 
    qui lit les touches et met à jour la direction, sans bloquer le mouvement automatique.
Étape 5 — Manger et grandir : détecte la collision avec la nourriture, 
    fais grandir le serpent et régénère la nourriture.
Étape 6 — Game over : détecte la collision avec soi-même et arrête proprement le jeu.
Points d'attention
curses peut lever une erreur (_curses.error: addwstr() returned ERR) si on écrit dans la toute dernière cellule de la fenêtre (bas-droite) 
    — c'est un comportement normal de la bibliothèque, à anticiper.
Deux coroutines qui modifient la même variable (direction, snake, food) doivent se coordonner correctement 
    pour éviter les incohérences d'affichage.
Réfléchis à comment combiner une tâche asynchrone (le mouvement) et une fonction bloquante (screen.getch()) 
    sans que l'une empêche l'autre de s'exécuter.


Bonus (pour aller plus loin)
Empêcher le serpent de faire un demi-tour direct sur lui-même 
    (ex : aller à droite puis immédiatement à gauche).
Ajouter un score affiché à l'écran, incrémenté à chaque nourriture mangée.
Augmenter progressivement la vitesse du serpent au fil de la partie.
Ajouter des obstacles fixes sur la grille.
Gérer proprement le redimensionnement du terminal en cours de partie.
Proposer un écran de fin avec le score final et une option "rejouer".
"""
import asyncio
import curses
from enum import Enum
from random import randint


class GRID_BORDERS(Enum):
    TL = "╔"
    TR = "╗"
    BL = "╚"
    BR = "╝"
    H = "═"
    V = "║"

SNAKE = "X"
FOOD = "0"
WIDTH = 20
HEIGHT = 20


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

async def game_loop(screen: curses.window, width, height):
    # Initialisation de curses pour l'affichage numérique
    curses.curs_set(False)

    def get_random_food_coordinate(snake_body):
            food_coordinate = (1, randint(1, width - 2))
            while food_coordinate in snake_body:
                food_coordinate = (1, randint(1, width - 2))
            return food_coordinate
    
    
    # État initial du jeu
    snake_body = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5)]
    current_direction = Direction.RIGHT  # Direction initiale 
    
    food_coordinate = get_random_food_coordinate(snake_body)
    
    # Boucle de jeu asynchrone
    while True:
        head_y, head_x = snake_body[-1]
        move_y, move_x = current_direction.value
        
        # nouvelle position de la tête avec gestion des bords
        new_head_y = head_y + move_y    if head_y < height-2   else 1
        new_head_x = head_x + move_x    if head_x < width-2    else 1
        new_head = (new_head_y, new_head_x)

        snake_body.append(new_head)
        if new_head != food_coordinate:
            snake_body.pop(0)
        else:
            food_coordinate = get_random_food_coordinate(snake_body)

        #RENDU GRAPHIQUE
        screen.clear()
        #bordures
        screen.addstr(0, 0, f"{GRID_BORDERS.TL.value}{GRID_BORDERS.H.value * (width - 2)}{GRID_BORDERS.TR.value}")
        for i in range(2, height):
            screen.addstr(i - 1, 0, f"{GRID_BORDERS.V.value}{'.' * (width - 2)}{GRID_BORDERS.V.value}")
        screen.addstr(height - 1, 0, f"{GRID_BORDERS.BL.value}{GRID_BORDERS.H.value * (width - 2)}{GRID_BORDERS.BR.value}")
        
        #serpent
        for coordinate in snake_body:
            screen.addstr(coordinate[0], coordinate[1], SNAKE)
            
        #bouffe
        screen.addstr(food_coordinate[0], food_coordinate[1], FOOD)
        screen.refresh()

        # 3. Pause asynchrone de 200 ms (ne bloque pas le thread)
        await asyncio.sleep(0.2)

def main(screen):
    # Lance la boucle d'événements asyncio à l'intérieur du wrapper curses
    asyncio.run(game_loop(screen, WIDTH, HEIGHT))

# Initialisation propre du terminal via le wrapper
curses.wrapper(main)