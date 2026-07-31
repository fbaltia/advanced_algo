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
import random
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
OBSTACLE = "⬤"
SNAKE_INITIAL_SPEED = 0.2

WIDTH = 20
HEIGHT = 10


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

async def read_keyboard(screen, game_state):
    while game_state["running"]:
        input_key = screen.getch()  # Non-bloquant : screen.nodelay(True)

        if input_key == 27:  # Touche Échap (ESC) pour quitter proprement
            game_state["running"] = False
            break
        elif input_key == curses.KEY_UP and game_state["direction"] != Direction.DOWN:
            game_state["direction"] = Direction.UP
        elif input_key == curses.KEY_DOWN and game_state["direction"] != Direction.UP:
            game_state["direction"] = Direction.DOWN
        elif input_key == curses.KEY_LEFT and game_state["direction"] != Direction.RIGHT:
            game_state["direction"] = Direction.LEFT
        elif input_key == curses.KEY_RIGHT and game_state["direction"] != Direction.LEFT:
            game_state["direction"] = Direction.RIGHT
        await asyncio.sleep(0.02)

async def game_loop(screen: curses.window, width, height):
    curses.curs_set(False)
    screen.nodelay(True)

    def game_over():
        screen.clear()
        screen.addstr( width // 2, height // 2, "GAME OVER")
        screen.refresh()

    def get_random_food_coordinate(snake_body, obstacle_locations):
        all_cells = {
            (y, x) for x in range(1,width-1) for y in range(1,height-1)
        }
        snake_body_set = set(snake_body)
        
        free_cells = list(all_cells - snake_body_set)
        free_cells = list(all_cells - obstacle_locations)
        if free_cells:
            return random.choice(free_cells)
        return None

    def get_obstacle_locations(width, height)->set[tuple]:
        max_number_obstacles = randint(width * height // 30, width * height // 20)
        obstacles = set()
        while len(obstacles) < max_number_obstacles:
            x = random.randint(1, height - 2)
            y = random.randint(1, width - 2)
            if (x,y) not in snake_body:
                obstacles.add((x, y))
            
        return obstacles


    def draw():    #RENDU GRAPHIQUE
        GRID_SHIFT_DOWN = 1
        screen.clear()
        #bordures
        screen.addstr(GRID_SHIFT_DOWN, 0, f"{GRID_BORDERS.TL.value}{GRID_BORDERS.H.value * (width - 2)}{GRID_BORDERS.TR.value}")
        for i in range(2, height):
            screen.addstr(GRID_SHIFT_DOWN + i - 1, 0, f"{GRID_BORDERS.V.value}{'.' * (width - 2)}{GRID_BORDERS.V.value}")
        screen.addstr(GRID_SHIFT_DOWN + height - 1, 0, f"{GRID_BORDERS.BL.value}{GRID_BORDERS.H.value * (width - 2)}{GRID_BORDERS.BR.value}")
        
        #serpent
        for coordinate in snake_body:
            screen.addstr(GRID_SHIFT_DOWN + coordinate[0], coordinate[1], SNAKE)
        #bouffe
        if food_coordinate != None:
            screen.addstr(GRID_SHIFT_DOWN+ food_coordinate[0], food_coordinate[1], FOOD)
        #obstacles
        for coordinate in obstacle_locations:
            screen.addstr(GRID_SHIFT_DOWN + coordinate[0], coordinate[1], OBSTACLE)
        #score
        screen.addstr(0, 0, "SCORE:" + str(score))

        screen.refresh()
    
    # État initial du jeu
    score = 0
    snake_body = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5)]
    obstacle_locations = get_obstacle_locations(width, height)
    food_coordinate = get_random_food_coordinate(snake_body, obstacle_locations)
    game_state = {
        "direction": Direction.RIGHT,
        "running": True
    }
    keyboard_task = asyncio.create_task(read_keyboard(screen, game_state))
    

    while game_state["running"]:
        head_y, head_x = snake_body[-1]
        move_y, move_x = game_state["direction"].value
        new_head_y = head_y + move_y
        if new_head_y >= height - 1: 
            new_head_y = 1
        elif new_head_y <= 0: 
            new_head_y = height - 2

        new_head_x = head_x + move_x
        if new_head_x >= width - 1: 
            new_head_x = 1
        elif new_head_x <= 0: 
            new_head_x = width - 2

        new_head = (new_head_y, new_head_x)

        if new_head != food_coordinate:
            snake_body.pop(0)
        else:
            score +=1
            food_coordinate = get_random_food_coordinate(snake_body, obstacle_locations)
            if not food_coordinate:
                game_over()
                await asyncio.sleep(2.0) 
                game_state["running"] = False
        if new_head in snake_body or new_head in obstacle_locations:
            game_over()
            await asyncio.sleep(2.0) 
            game_state["running"] = False
        snake_body.append(new_head)

        draw()
        await asyncio.sleep(SNAKE_INITIAL_SPEED)
    keyboard_task.cancel()

def main(screen):
    asyncio.run(game_loop(screen, WIDTH, HEIGHT))

# Initialisation propre du terminal via le wrapper
#curses.wrapper(main)
if __name__ == "__main__":
    curses.wrapper(main)