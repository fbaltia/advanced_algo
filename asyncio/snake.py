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

#region imports
import asyncio
import curses
from enum import Enum
import random
from random import randint
from datetime import datetime
#endregion

#region enums
class GRID_BORDERS(Enum):
    TL = "╔"
    TR = "╗"
    BL = "╚"
    BR = "╝"
    H = "═"
    V = "║"

class DIRECTION(Enum):
    UP = [(-1, 0), "▴"]
    DOWN = [(1, 0), "▾"]
    LEFT = [(0, -1), "◂"]
    RIGHT = [(0, 1), "▸"]

class GAME_STATUS(Enum):
    WAITING_TO_START = "waiting to start"
    RUNNING = "running"
    ABORT = "abort"
#endregion

#region constants
SNAKE = "●"
FOOD = "✫"
OBSTACLE = "■"
OPSIE = "♯"
OPSIE_LIFE_SPAN_IN_SEC = 5.0 # (secs)
SNAKE_INITIAL_SPEED = 0.2 # (secs)
SNAKE_SPEED_INCREMENT = 0.02 #0.02  # (secs)
SNAKE_SPEED_ACCELERATION_INTERVAL = 5.0 # (secs)

WIDTH = 20
HEIGHT = 20
#endregion


#region asyn functions out of the gameloop
async def read_keyboard(screen, game_state):
    while game_state["status"] in (GAME_STATUS.WAITING_TO_START, GAME_STATUS.RUNNING):
        input_key = screen.getch()  # Non-bloquant : screen.nodelay(True)

        if input_key == 27:  # Touche Échap (ESC) pour quitter proprement
            game_state["status"] = GAME_STATUS.ABORT
            break
        elif input_key == curses.KEY_UP and game_state["direction"] != DIRECTION.DOWN:
            game_state["direction"] = DIRECTION.UP
        elif input_key == curses.KEY_DOWN and game_state["direction"] != DIRECTION.UP:
            game_state["direction"] = DIRECTION.DOWN
        elif input_key == curses.KEY_LEFT and game_state["direction"] != DIRECTION.RIGHT:
            game_state["direction"] = DIRECTION.LEFT
        elif input_key == curses.KEY_RIGHT and game_state["direction"] != DIRECTION.LEFT:
            game_state["direction"] = DIRECTION.RIGHT
        if input_key != -1 and game_state["status"] == GAME_STATUS.WAITING_TO_START:
            game_state["status"] = GAME_STATUS.RUNNING
        await asyncio.sleep(0.02)

async def speed_control(game_state):
    while game_state["status"]==GAME_STATUS.RUNNING:
        game_state["speed"] = max(0.05, round(game_state["speed"] - SNAKE_SPEED_INCREMENT, 2))
        await asyncio.sleep(SNAKE_SPEED_ACCELERATION_INTERVAL)

async def opsie_control(game_state, opsies):
    while game_state["status"]==GAME_STATUS.RUNNING:
        opsies[:] = [opsie for opsie in opsies if (datetime.now() - opsie[1]).total_seconds() < OPSIE_LIFE_SPAN_IN_SEC]
        await asyncio.sleep(max(1,OPSIE_LIFE_SPAN_IN_SEC-1))
#endregion

#region gameloop
async def game_loop(screen: curses.window, width, height, with_obstacles = True, with_opsies = False):
    curses.curs_set(False)
    screen.nodelay(True)
    #region internal functions
    def game_over(message):
        game_state["status"] = GAME_STATUS.ABORT
        screen.clear()
        screen.addstr( height // 2, width // 2, message)
        screen.addstr( height // 2 + 1, width // 2, "GAME OVER")
        screen.refresh()

    def get_random_food_coordinate(snake_body, obstacle_locations):
        all_cells = {
            (y, x) for x in range(1,width-1) for y in range(1,height-1)
        }
        snake_body_set = set(snake_body)
        
        free_cells = list(all_cells - snake_body_set)
        if obstacle_locations:
            free_cells = list(all_cells - obstacle_locations)
        if opsies:
            free_cells = list(all_cells - set([x[0] for x in opsies]))
        if free_cells:
            return random.choice(free_cells)
        return None
    
    def get_new_coordinates_according_to_direction(coordinate, direction):
        head_y, head_x = coordinate
        move_y, move_x = direction
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
        return (new_head_y, new_head_x)

    def get_obstacle_locations(width, height)->set[tuple]:
        max_number_obstacles = randint(width * height // 30, width * height // 20)
        obstacles = set()
        while len(obstacles) < max_number_obstacles:
            x = random.randint(1, height - 2)
            y = random.randint(1, width - 2)
            if (x,y) not in snake_body:
                obstacles.add((x, y))
            
        return obstacles
    #endregion

    #region graphical output
    def draw():   
        GRID_SHIFT_DOWN = 2
        screen.clear()
        #bordures
        screen.addstr(GRID_SHIFT_DOWN, 0, f"{GRID_BORDERS.TL.value}{GRID_BORDERS.H.value * (width - 2)}{GRID_BORDERS.TR.value}", curses.color_pair(4))
        for i in range(2, height):
            screen.addstr(GRID_SHIFT_DOWN + i - 1, 0, f"{GRID_BORDERS.V.value}{'.' * (width - 2)}{GRID_BORDERS.V.value}", curses.color_pair(4))
        screen.addstr(GRID_SHIFT_DOWN + height - 1, 0, f"{GRID_BORDERS.BL.value}{GRID_BORDERS.H.value * (width - 2)}{GRID_BORDERS.BR.value}", curses.color_pair(4))
        
        #serpent
        for coordinate in snake_body:
            screen.addstr(GRID_SHIFT_DOWN + coordinate[0], coordinate[1], SNAKE,curses.color_pair(1))
        screen.addstr(GRID_SHIFT_DOWN + snake_body[-1][0], snake_body[-1][1], game_state["direction"].value[1],curses.color_pair(1))
        #bouffe
        if food_coordinate != None:
            screen.addstr(GRID_SHIFT_DOWN+ food_coordinate[0], food_coordinate[1], FOOD,curses.color_pair(2))
        #obstacles
        for coordinate in obstacle_locations:
            screen.addstr(GRID_SHIFT_DOWN + coordinate[0], coordinate[1], OBSTACLE,curses.color_pair(4))
        #score
        screen.addstr(0, 0, "SCORE:" + str(score))
        #opsies
        if opsies:
            for opsie in opsies:
                screen.addstr(GRID_SHIFT_DOWN + opsie[0][0], opsie[0][1], OPSIE,curses.color_pair(3))

        screen.refresh()
    #endregion


    #region initialisation
    curses.start_color()
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(3, 94, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)

    score = 0
    snake_body = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5)]
    obstacle_locations = ()
    opsies = []

    if with_obstacles: 
        obstacle_locations = get_obstacle_locations(width, height)
    food_coordinate = get_random_food_coordinate(snake_body, obstacle_locations)
    game_state = {
        "direction": DIRECTION.RIGHT,
        "status": GAME_STATUS.WAITING_TO_START,
        "speed": SNAKE_INITIAL_SPEED
    }
    keyboard_task = asyncio.create_task(read_keyboard(screen, game_state))
    speed_task = asyncio.create_task(speed_control(game_state))
    opsie_task = asyncio.create_task(opsie_control(game_state, opsies))
    #endregion


    draw()
    while game_state["status"] == GAME_STATUS.WAITING_TO_START:
        await asyncio.sleep(0.2)

    while game_state["status"] == GAME_STATUS.RUNNING:
        new_head = get_new_coordinates_according_to_direction(snake_body[-1],game_state["direction"].value[0])
        if new_head != food_coordinate:
            snake_body.pop(0)
        else:
            score +=1
            if with_opsies:
                x,y = -1 *(snake_body[0][0] - snake_body[1][0]), -1 * (snake_body[0][1] - snake_body[1][1])
                opsies_coord = get_new_coordinates_according_to_direction(snake_body[0], (x,y))
                opsies.append([opsies_coord, datetime.now()])

            food_coordinate = get_random_food_coordinate(snake_body, obstacle_locations)
            if not food_coordinate:
                game_over("GRATZ !!!")
                await asyncio.sleep(2.0) 
                game_state["status"] = GAME_STATUS.ABORT
        if new_head in snake_body or new_head in obstacle_locations:
            game_over("BANG !!!!")
            await asyncio.sleep(2.0) 
            game_state["status"] = GAME_STATUS.ABORT
        if new_head in [opsie[0] for opsie in opsies]:
            game_over("EWWWW !!!")
            await asyncio.sleep(2.0) 
            game_state["status"] = GAME_STATUS.ABORT

        snake_body.append(new_head)

        draw()
        await asyncio.sleep(game_state["speed"])
    keyboard_task.cancel()
    speed_task.cancel()
    if with_opsies:
        opsie_task.cancel()
#endregion    

def main(screen):
    asyncio.run(game_loop(screen, WIDTH, HEIGHT, True, True))

# Initialisation propre du terminal via le wrapper
#curses.wrapper(main)
if __name__ == "__main__":
    curses.wrapper(main)