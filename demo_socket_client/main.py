# python -m venv .venv
# .venv\Scripts\Activate
# pip install python-socketio aiohttp windows-curses
# pip freeze > requirements.txt
import curses
import socketio
import asyncio
import curses.textpad

socket_client = socketio.AsyncClient()
titi = 0
messages = []
msg_win=None
input_win=None
def message_received(message):
    msg_win.clear()
    messages.append(message)
    for m in messages:
        msg_win.addstr(f'{m.get('username')}: {m.get('message')}\n')
    msg_win.refresh()

async def listen_input():
    while True:
        await asyncio.sleep(0.05)
        input_win.nodelay(True)
        key = input_win.getch()
        if key in {10, 13}:
            box = curses.textpad.Textbox(input_win)
            box.edit()
            message = box.gather()
            await socket_client.emit('NEW_MESSAGE', message)
            input_win.clear()
            input_win.refresh()

async def main(screen: curses.window):
    global msg_win
    global input_win

    screen.clear()
    screen.refresh()

    msg_win = curses.newwin(curses.LINES - 3, curses.COLS, 0, 0)
    input_win = curses.newwin(1, curses.COLS, curses.LINES-2, 0)

    await socket_client.connect(
        'https://lawsuit-pays-lookup-researcher.trycloudflare.com',
        auth={'username' : 'Khun'}
    )

    socket_client.on('ON_MESSAGE', message_received)

    asyncio.create_task(listen_input())

    await socket_client.wait()

if __name__ == '__main__':
    curses.wrapper(lambda screen: asyncio.run(main(screen)))