import curses
import socketio
import asyncio
import curses.textpad
from enum import Enum


class GRID_BORDERS(Enum):
    TL = "╔"
    TR = "╗"
    BL = "╚"
    BR = "╝"
    H = "═"
    V = "║"

log = []
game_over = False
NUMBER_OF_ROWS = 6
NUMBER_OF_COLUMNS = 7
NUMBER_OF_ALIGNED_TOKENS_TO_WIN = 4
grid =  [[' ' for _ in range(NUMBER_OF_COLUMNS)] for _ in range(NUMBER_OF_ROWS)]

socket_client = socketio.AsyncClient()
colours = ['R', 'J']
colour = None
messages = []

connected = True
msg_win=None
input_win=None
is_my_turn = None

def message_received(message):
    global colour
    if message['message'] in colours:
        colour = message['message']
        print_grid(colour)
        print_prompt(colour)

    if message['message'] in {"1", "2", "3", "4", "5", "6", "7"} and not game_over:
        play(int(message['message']))


def check_winner(a_colour, a_column, a_row):
    if grid[a_row][a_column] != a_colour:
        return False
    directions = [
        (1, 0),   # Horizontal ->
        (0, 1),   # Vertical v
        (1, 1),   # Diagonal \
        (1, -1)   # Diagonal /
    ]
    for dc, dr in directions:
        count = 1
        c, r = a_column + dc, a_row + dr
        while 0 <= c < NUMBER_OF_COLUMNS and 0 <= r < NUMBER_OF_ROWS and grid[r][c] == a_colour:
            count += 1
            c += dc
            r += dr
        c, r = a_column - dc, a_row - dr
        while 0 <= c < NUMBER_OF_COLUMNS and 0 <= r < NUMBER_OF_ROWS and grid[r][c] == a_colour:
            count += 1
            c -= dc
            r -= dr
        if count >= NUMBER_OF_ALIGNED_TOKENS_TO_WIN:
            return True
    return False

def print_grid(a_colour):
    msg_win.clear()
    msg_win.addstr(f"{GRID_BORDERS.TL.value}{GRID_BORDERS.H.value * (NUMBER_OF_COLUMNS*4 -1)}{GRID_BORDERS.TR.value}" + "\n")
    for row in grid:
        msg_win.addstr(GRID_BORDERS.V.value + " " + " | ".join(row) + " " + GRID_BORDERS.V.value + "\n")
    msg_win.addstr(f"{GRID_BORDERS.BL.value}{GRID_BORDERS.H.value * (NUMBER_OF_COLUMNS*4 -1)}{GRID_BORDERS.BR.value}" + "\n")
            
    msg_win.refresh()
    input_win.clear()

def print_prompt(a_colour):
    if a_colour == colours[0]:
        input_win.addstr("Vous êtes " + a_colour + ". Choisissez une colonne (1-7) pour jouer: ")
    else:
        input_win.addstr("C'est au tour de " + a_colour + ". Attendez votre tour...\n")
    input_win.refresh()

    
def winner(a_colour):
    global game_over
    input_win.addstr(f'{a_colour} a gagné !')
    game_over = True
    input_win.refresh()

def play(column):
    global colours
    global colour
    #écriture dans la grille
    row = -1
    for i in range(5, -1, -1):
        if grid[i][column-1] == " ":
            grid[i][column-1] = colour
            row = i
            break
    print_grid(colour)
    is_winner = check_winner(colour, column-1, row)
    if is_winner: 
        winner(colour)
    else:
    #on change de couleur /tour
        if not all(item == ' ' for row in grid for item in row):
            colour = list(set.difference(set(colours), {colour}))[0]
        print_prompt(colour)

async def listen_input():
    while connected:
        await asyncio.sleep(0.05)
        if is_my_turn:
            input_win.nodelay(True)
            key = input_win.getch()
            box = curses.textpad.Textbox(input_win)

            box.edit()
            message = box.gather()[-2].strip()
            await socket_client.emit('NEW_MESSAGE', message)
            input_win.clear()
            input_win.refresh()

async def get_username():
    input_win.clear()
    input_win.addstr("Nom d'utilisateur: ")
    input_win.refresh()
    box = curses.textpad.Textbox(input_win)
    box.edit()
    username = box.gather()[19:].strip()
    if not username:
        return "anonymous"
    return username

@socket_client.event
def disconnect():
    global connected
    input_win.clear()
    input_win.addstr("Disconnected from server. Appuyez sur une touche pour quitter.")
    connected = False
    input_win.refresh()

async def main(screen: curses.window):
    global msg_win
    global input_win
    screen.clear()
    screen.refresh()
    msg_win = curses.newwin(curses.LINES - 3, curses.COLS, 0, 0)
    input_win = curses.newwin(1, curses.COLS, curses.LINES-2, 0)

    #---
    username = await get_username()
    #---

    socket_client.on('ON_MESSAGE', message_received)

    await socket_client.connect(
        'http://127.0.0.1:8000',
        auth={'username' : username}
    )

    asyncio.create_task(listen_input())
    await socket_client.wait()

if __name__ == '__main__':
    curses.wrapper(lambda screen: asyncio.run(main(screen)))