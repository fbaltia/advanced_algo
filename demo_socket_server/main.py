import uvicorn
import socketio

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio)


if __name__ == '__main':
    uvicorn.run('main:app', '127.0.0.1', port=8000, reload = True)

    


