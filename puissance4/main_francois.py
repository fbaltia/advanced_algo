import curses
import socketio
import asyncio
import curses.textpad

socket_client = socketio.AsyncClient()


import numpy as np

messages = []
grid = [[" ", " ", " ", " ", " ", " ", " "] for _ in range(6)]
token = "X"
tokens = ["O","X"]
msg_win=None
input_win=None

def data_received(data):
    global token
    global tokens
    
    token = data["token"]
    tokens = data["tokens"]

    if token == '⬤':
        curses.init_pair(1,curses.COLOR_BLUE, -1)
    else:
        curses.init_pair(2,curses.COLOR_RED, -1)

def message_received(message):
    if message['message'] in ["1", "2", "3", "4", "5", "6", "7"]:

        play(int(message['message']))
    print_grid()

def print_grid():
    global color
    msg_win.clear()

    for row_index, row in enumerate(grid):
        msg_win.move(row_index, 0)
        msg_win.addstr("|", curses.color_pair(2))
        
        for col_index, element in enumerate(row):
            if element in tokens:
                msg_win.addstr(element, curses.color_pair(1))
            else:
                msg_win.addstr(element, curses.color_pair(2))           
            msg_win.addstr("|", curses.color_pair(2))
    msg_win.refresh()
    
def play(column):
    for c in grid:
        for i in range(len(c)):
            if c[i] == " ":
                c[i] = "⬤"
        return
            
async def listen_input():
    while True:
        await asyncio.sleep(0.02)
        input_win.nodelay(True)
        key = input_win.getch()
        box = curses.textpad.Textbox(input_win)
        box.edit()
        message = box.gather()[-2]
        lala = grid
        await socket_client.emit('NEW_MESSAGE', message )
        input_win.clear()
        input_win.refresh()

async def main(screen: curses.window):
    global msg_win
    global input_win
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1,curses.COLOR_WHITE, -1)
    curses.init_pair(2,curses.COLOR_WHITE, -1)
    screen.clear()
    screen.refresh()

    msg_win = curses.newwin(curses.LINES - 3, curses.COLS, 0, 0)
    input_win = curses.newwin(1, curses.COLS, curses.LINES-2, 0)

    socket_client.on('ON_CONNECT', data_received)
    socket_client.on('ON_MESSAGE', message_received)

    await socket_client.connect(
        'http://127.0.0.1:8000',
        auth={'username' : 'Francois'}
    )

    asyncio.create_task(listen_input())
    await socket_client.wait()

if __name__ == '__main__':
    curses.wrapper(lambda screen: asyncio.run(main(screen)))
