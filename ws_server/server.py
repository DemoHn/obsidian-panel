import socketio
import eventlet
import pickle
eventlet.monkey_patch()

mgr = socketio.RedisManager("redis://")
sio = socketio.Server(client_manager=mgr)

@sio.on('connect')
def connect(sid, environ):
    print('connect ', sid)

@sio.on('message', namespace="/")
def emit_message(sid, data):
    mgr.redis.publish("socketio",pickle.dumps(data))

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)

app = socketio.Middleware(sio)
# deploy as an eventlet WSGI server
eventlet.wsgi.server(eventlet.listen(('', 5001)), app)