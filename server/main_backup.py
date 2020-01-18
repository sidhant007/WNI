#import eventlet
from aiohttp import web
import socketio
import os
import pickle
import base64
import socketio

#sio = socketio.Server()
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
#app = socketio.WSGIApp(sio, static_files={
#    '/': {'content_type': 'text/html', 'filename': 'index.html'}
#})

requests = dict()
all_roots = dict()
all_helpers = dict()

class RoomRequest:
    def __init__(self, root_sid, code, n):
        self.running = False
        self.root_sid = root_sid
        self.code = code
        self.n = n
        self.mapping = []
        self.helpers = set()

    def add_helper(self, sid):
        if self.running is True:
            return {'error_message': "WNI: Room is already running"}
        if len(self.helpers) == self.n:
            return {'error_message': "WNI: Room is already full"}

        self.helpers.add(sid)
        return {}

    def helper_disconnected(self, sid):
        self.helpers.remove(sid)
        if self.running is True:
            print(sid + " dropped out in between running")
            #sio.emit('exit_code', {'error_message': 'WNI: Someone dropped out from the network'}, room=self.root_sid)
            for x in self.helpers:
                pass
                #sio.emit('exit_code', {'error_message': 'WNI: Someone dropped out from the network'}, room=x)
        else:
            sio.emit('print_message', {'message': "WNI: Update: Number of users currently joined = " + str(len(self.helpers))}, room=self.root_sid)

    def run_code(self):
        self.running = True
        file_data = base64.b64decode(self.code)

        sio.emit('run_code', {'id': 0, 'code': self.code}, room=self.root_sid)
        self.mapping.append(self.root_sid)
        for x in self.helpers:
            sio.emit('run_code', {'id': len(self.mapping), 'code': self.code}, room=x)
            self.mapping.append(x)

    def send_data(self, data):
        receive_sid = self.mapping[data['receive_id']]
        #print("SENDING DATA:", data)
        sio.emit('receive_data_from_server', data, room=receive_sid)

@sio.event
def connect(sid, environ):
    print("connected", sid)

@sio.event
async def list_all_requests(sid):
    table = []
    for key in sorted(requests):
        table.append([key, requests[key].n, len(requests[key].helpers), requests[key].running])

    await sio.emit('print_table', {'table': table}, room=sid)
    return 0

@sio.event
def join_request(sid, data):
    print("Join request ", sid)
    if data['room_id'] not in requests:
        sio.emit('join_request_fail', {'error_message': "WNI: Room ID not found"}, room=sid)
        return 0

    is_error = requests[data['room_id']].add_helper(sid)

    if 'error_message' in is_error:
        sio.emit('join_request_fail', is_error, room=sid)
        return 0

    all_helpers[sid] = data['room_id']
    sio.emit('print_message', {'message': "WNI: Update: Number of users currently joined = " + str(len(requests[data['room_id']].helpers))}, room=requests[data['room_id']].root_sid)

    if len(requests[data['room_id']].helpers) == requests[data['room_id']].n:
        open(data['room_id'] + '.py', 'wb').write(requests[data['room_id']].code)
        print("Going to run code", data['room_id'])
        requests[data['room_id']].run_code()

@sio.event
def disconnect(sid):
    print("to disconnect ", sid)
    if sid in all_roots:
        del requests[all_roots[sid]]
        del all_roots[sid]

    if sid in all_helpers:
        if all_helpers[sid] in requests:
            requests[all_helpers[sid]].helper_disconnected(sid)
        del all_helpers[sid]

    print("disconnect ", sid)

@sio.event
def make_request(sid, data):
    print("Making request ", sid)
    if data['room_id'] in requests:
        sio.emit('make_request_fail', {'error_message': "WNI: Room ID collided with another room"}, room=sid)
        return 0
    all_roots[sid] = data['room_id']
    requests[data['room_id']] = RoomRequest(sid, data['code'], data['n'])

@sio.event
def send_data(sid, data):
    if sid in all_roots:
        requests[all_roots[sid]].send_data(data)
    if sid in all_helpers:
        requests[all_helpers[sid]].send_data(data)

if __name__ == '__main__':
    web.run_app(app)
    #eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
