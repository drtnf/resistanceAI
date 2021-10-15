import socketio

socket_ = socketio.AsyncServer(async_mode = 'asgi')
app = socketio.ASGIApp(socket_, static_files={
    '/': './public/'
})

@socket_.event
async def connect(sid, environ):
    print(sid, 'connected.')

@socket_.event
async def disconnect(sid):
    print(sid, 'disconnected.')