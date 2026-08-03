# python -m venv .venv
# .venv\Scripts\Activate
# pip install python-socketio aiohttp windows-curses
# pip freeze > requirements.txt
import curses
import curses.textpad

import socketio
import asyncio

socket_client = socketio.AsyncClient()
messages = []

#fenêtres curses:
msg_win = None
input_win = None


def message_received(message):
    #global msg_win          #en 'global' quand on réaffecte une nouvelle valeur
    # mais pas besoin ici
    msg_win.clear()         #pas de 'global' car on ne réaffecte pas (rappel = l' "append" ne réaffecte pas)
    messages.append(message)
    for m in messages:
        msg_win.addnstr(f'{m.get('username')}: {m.get('message')}')
    msg_win.refresh()

async def listen_input():
    while True:
        await asyncio.sleep(0.05) #pr permettre de ne pas bloquer le 'main'
        input_win.nodelay(True) # pour que le getch ne soit pas bloquant
        key = input_win.getch()
        if key in {10, 13, curses.KEY_ENTER}:
            box = curses.textpad.Textbox(input_win)
            box.edit()
            message = box.gather()
            await socket_client.emit('NEW_MESSAGE', message)
            input_win.clear()
            input_win.refresh()

async def main(screen : curses.window):
    global msg_win
    global input_win

    screen.clear()
    screen.refresh()

    msg_win = curses.newwin(curses.LINES-1, curses.COLS, 0,0)
    input_win = curses.newwin(1, curses.COLS, curses.LINES-2,0)


    await socket_client.connect(
        'https://lawsuit-pays-lookup-researcher.trycloudflare.com',
        auth={'username' : 'François'}
    )

    socket_client.on('ON_MESSAGE', message_received)#ce qu'on fait quand on reçoit un msg
    asyncio.create_task(listen_input())

    await socket_client.emit('NEW_MESSAGE', 'Coucou !!!')

    await socket_client.wait()

if __name__ == '__main__':
    curses.wrapper(lambda screen: asyncio.run(main()))    #lancer la méthode main de façon asynch)) #on wrap le truc dans un curses, avec une lambda
                   