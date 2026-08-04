import socketio
import uvicorn

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio)

clients = {}

@sio.event
async def connect(sid, environ, auth):
    if clients == {}: 
        clients[sid] = auth.get('username')
        await sio.emit('ON_MESSAGE', {
                'username': clients.get(sid),
                'message': "R"
            }, to=sid)
        print(f"{clients.get(sid)} s'est connecté et a reçu la couleur R")
    else:
        clients[sid] = auth.get('username')
        await sio.emit('ON_MESSAGE', {
                'username': clients.get(sid),
                'message': "J"
            }, to=sid)
        print(f"{clients.get(sid)} s'est connecté et a reçu la couleur J")
    

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