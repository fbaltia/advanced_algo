import socketio
import uvicorn
import datetime

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio)

clients = {}
tokens = {}
token_def = ["⬤","✖"]



@sio.event
async def connect(sid, environ, auth):
    tokens[sid] = token_def[0] if not clients else token_def[1]
    clients[sid] = auth.get('username')
    print(f'{datetime.datetime.now()} - {auth.get('username')} s\'est connecté, jeton : {tokens[sid]}')
    await sio.emit('ON_CONNECT', {
            'username': clients.get(sid),
            'token': tokens.get(sid),
            'tokens': token_def
        })

@sio.event
def disconnect(sid):
    print(f'{clients.get(sid)} s\'est déco')
    clients.pop(sid)

@sio.on('NEW_MESSAGE')
async def new_message(sid, message: str):
    print(clients[sid], message)
    await sio.emit('ON_MESSAGE', {
        'username': clients.get(sid),
        'message': message
    })

if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)