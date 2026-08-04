import socketio
import uvicorn

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio)

clients = {}
colours = ['R', 'J']


@sio.event
async def connect(sid, environ, auth):
    your_turn =  False
    if len(clients)<=len(colours):
        if len(clients) == 0:
            colour = colours[0]
            your_turn = True
        else:
            colour = colours[1]

        clients[sid] = auth.get('username')
        await sio.emit('ON_MESSAGE', {
                'username': clients.get(sid),
                'message': colour,
                'your_turn': your_turn
            }, to=sid)
        temp = "premier" if  your_turn else "second"
        print(f"{clients.get(sid)} s'est connecté, a reçu la couleur {colour} et sera le {temp} à jouer")

@sio.event
async def disconnect(sid):
    print(f'{clients.get(sid)} s\'est déco')
    clients.pop(sid)

@sio.on('NEW_MESSAGE')
async def new_message(sid, message: str):
    print(f"Message reçu de {clients.get(sid)}: {message}")
    await sio.emit('ON_MESSAGE', {
        'username': clients.get(sid),
        'message': message
    })

if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)