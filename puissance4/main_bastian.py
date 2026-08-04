import curses
import socketio
import asyncio
import curses.textpad

socket_client = socketio.AsyncClient()

messages = []
grid = [[" ", " ", " ", " ", " ", " ", " "] for _ in range(6)]
color = "X"
your_turn= None
connected = True
msg_win=None
input_win=None

def message_received(message):
    global color, your_turn

    if message['message'] in ["1", "2", "3", "4", "5", "6", "7"]:
        play(int(message['message']))
    elif message['message'] == "R":
        color = "R"
        your_turn = True
    elif message['message'] == "J":
        color = "J"
        your_turn = False

    print_grid()
    

def check_winner():
    msg_win.addstr(f"Checking for winner...\n")
    msg_win.refresh()
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    for row in range(6):
        for col in range(7):
            if grid[row][col] != color:
                continue

            for dr, dc in directions:
                count = 1
                r, c = row + dr, col + dc

                while 0 <= r < 6 and 0 <= c < 7 and grid[r][c] == color:
                    count += 1
                    r += dr
                    c += dc

                if count >= 4:
                    msg_win.addstr(f"Le joueur {color} a gagné!\n")
                    msg_win.refresh()

    other_color = "R" if color == "J" else "J"
    for row in range(6):
            for col in range(7):
                if grid[row][col] != other_color:
                    continue
    
                for dr, dc in directions:
                    count = 1
                    r, c = row + dr, col + dc
    
                    while 0 <= r < 6 and 0 <= c < 7 and grid[r][c] == other_color:
                        count += 1
                        r += dr
                        c += dc
    
                    if count >= 4:
                        msg_win.addstr(f"Le joueur {other_color} a gagné!\n")
                        msg_win.refresh()

def print_grid():
    msg_win.clear()
    for row in grid:
        msg_win.addstr(" | ".join(row) + "\n")
    msg_win.refresh()

    input_win.clear()
    if your_turn:
        input_win.addstr("Vous êtes " + color + ". Choisissez une colonne (1-7) pour jouer: ")
    else:
        other_color = "R" if color == "J" else "J"
        input_win.addstr("C'est au tour de " + other_color + ". Attendez votre tour...\n")
    input_win.refresh()

    check_winner()

def play(column):
    global your_turn
    for i in range(5, -1, -1):
        if grid[i][column-1] == " ":
            if your_turn:            
                grid[i][column-1] = color
                your_turn = False
            else:
                grid[i][column-1] = "R" if color == "J" else "J"
                your_turn = True
            break

    print_grid()
    
            
async def listen_input():
    while connected:
        await asyncio.sleep(0.05)
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

    username = await get_username()

    socket_client.on('ON_MESSAGE', message_received)

    await socket_client.connect(
        'http://127.0.0.1:8000',
        auth={'username' : username}
    )

    asyncio.create_task(listen_input())

    await socket_client.wait()

if __name__ == '__main__':
    curses.wrapper(lambda screen: asyncio.run(main(screen)))