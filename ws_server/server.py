import socketio
import eventlet

eventlet.monkey_patch()

mgr = socketio.RedisManager("redis://")
sio = socketio.Server(client_manager=mgr)

@sio.on('connect')
def connect(sid, environ):
    print('connect ', sid)

@sio.on('hello')
def message(sid, data):
    print('message ', data)

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)

app = socketio.Middleware(sio)
# deploy as an eventlet WSGI server
eventlet.wsgi.server(eventlet.listen(('', 5001)), app)