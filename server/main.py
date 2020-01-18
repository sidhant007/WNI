import eventlet
#from aiohttp import web
import socketio
import os
import pickle
import base64

sio = socketio.Server()
#sio = socketio.AsyncServer()
#app = web.Application()
#sio.attach(app)
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

requests = dict()
all_roots = dict()
all_helpers = dict()
all_users = dict()
sid_to_user = dict()

class RoomUser:
    def __init__(self, sid):
        self.sid = sid
        self.money = 1000

class RoomRequest:
    def __init__(self, root_sid, code, n, rate, seconds):
        self.running = False
        self.root_sid = root_sid
        self.code = code
        self.n = n
        self.rate = rate
        self.seconds = seconds
        self.mapping = []
        self.helpers = set()
        self.helpers_closed = set()

    def add_helper(self, sid):
        if self.running is True:
            return {'error_message': "WNI: Room is already running"}
        if len(self.helpers) == self.n:
            return {'error_message': "WNI: Room is already full"}

        self.helpers.add(sid)
        return {}

    def remove_all_helpers(self):
        for x in self.helpers:
            print("Tryint to disconnect helper:", x) # debug
            #sio.emit('disconnect', room=x)
            sio.emit('disconnect_this_helper', room=x)

    def add_helper_to_helpers_closed(self, sid):
        #all_users[sid_to_user[sid]].money = all_users[sid_to_user[sid]].money + (self.rate * self.seconds)
        self.helpers_closed.add(sid)

    def helper_disconnected(self, sid):
        self.helpers.remove(sid)
        if sid not in self.helpers_closed:
            all_users[sid_to_user[sid]].money = all_users[sid_to_user[sid]].money - ((self.n + 1) * self.rate * self.seconds)
            all_users[sid_to_user[self.root_sid]].money = all_users[sid_to_user[self.root_sid]].money + ((self.n + 1) * self.rate * self.seconds)
            print(sid + " dropped out in between running")
            sio.emit('exit_code', {'error_message': 'WNI: Some helper dropped out in between. That helper has been penalised.'}, room=self.root_sid)
            for x in self.helpers:
                sio.emit('exit_code', {'error_message': 'WNI: Someone dropped out in between. That helper has been penalised.'}, room=x)
        else:
            sio.emit('print_message', {'message': "WNI: Update: Number of users currently joined = " + str(len(self.helpers))}, room=self.root_sid)

    def run_code(self):
        all_users[sid_to_user[self.root_sid]].money = all_users[sid_to_user[self.root_sid]].money - (self.n * self.rate * self.seconds)
        self.running = True
        file_data = base64.b64decode(self.code)

        sio.emit('run_code', {'id': 0, 'code': self.code}, room=self.root_sid)
        self.mapping.append(self.root_sid)
        for x in self.helpers:
            all_users[sid_to_user[x]].money = all_users[sid_to_user[x]].money + (self.rate * self.seconds)
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
def add_user(sid, data):
    if data['user'] in all_users:
        sio.emit('register_request_fail', {'error_message': "WNI: User id collision"}, room=sid)
        return 0
    all_users[data['user']] = RoomUser(sid)
    sio.emit('register_clean_exit', room=sid)

@sio.event
def cleanup_root(sid):
    #print("BC", sid)
    if sid in all_roots:
        if all_roots[sid] in requests:
            del requests[all_roots[sid]]
        del all_roots[sid]
    sio.emit('exit_maaro', room=sid)

@sio.event
def cleanup_helper(sid):
    if sid in all_helpers:
        del all_helpers[sid]

@sio.event
def list_all_requests(sid, data):
    if data['user'] not in all_users:
        sio.emit('show_failed', {'error_message': "WNI: User not found"}, room=sid)
        return 0
    entry_message = "Hi " + data['user'] + "\nWni-Money you have = " + str(all_users[data['user']].money)
    table = []
    for key in sorted(requests):
        table.append([key, requests[key].n, len(requests[key].helpers), requests[key].running, requests[key].rate, requests[key].seconds])

    sio.emit('print_table', {'entry_message': entry_message, 'table': table}, room=sid)
    return 0

@sio.event
def closing_helper_correctly(sid):
    requests[all_helpers[sid]].add_helper_to_helpers_closed(sid)

@sio.event
def join_request(sid, data):
    print("Join request ", sid)
    if data['room_id'] not in requests:
        sio.emit('join_request_fail', {'error_message': "WNI: Room ID not found"}, room=sid)
        return 0
    if data['user'] not in all_users:
        sio.emit('join_request_fail', {'error_message': "WNI: User not found"}, room=sid)
        return 0

    sid_to_user[sid] = data['user']

    is_error = requests[data['room_id']].add_helper(sid)

    if 'error_message' in is_error:
        sio.emit('join_request_fail', is_error, room=sid)
        return 0

    all_helpers[sid] = data['room_id']
    sio.emit('print_message', {'message': "WNI: Update: Number of users currently joined = " + str(len(requests[data['room_id']].helpers))}, room=requests[data['room_id']].root_sid)

    if len(requests[data['room_id']].helpers) == requests[data['room_id']].n:
        open(data['room_id'] + '.py', 'wb').write(requests[data['room_id']].code)
        #self.rate = rate
        #self.seconds = seconds
        print("Going to run code", data['room_id'])
        requests[data['room_id']].run_code()

@sio.event
def disconnect(sid):
    print("to disconnect ", sid)
    if sid in all_roots:
        #requests[all_roots[sid]].remove_all_helpers()
        if all_roots[sid] in requests:
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
    if data['user'] not in all_users:
        sio.emit('make_request_fail', {'error_message': "WNI: User not found"}, room=sid)
        return 0

    money_needed = data['n'] * data['rate'] * data['seconds']

    if all_users[data['user']].money < money_needed:
        sio.emit('make_request_fail', {'error_message': "WNI: User doesn't have enough wni-money"}, room=sid)
        return 0

    sid_to_user[sid] = data['user']

    all_roots[sid] = data['room_id']
    requests[data['room_id']] = RoomRequest(sid, data['code'], data['n'], data['rate'], data['seconds'])

@sio.event
def send_data(sid, data):
    if sid in all_roots:
        requests[all_roots[sid]].send_data(data)
    if sid in all_helpers:
        requests[all_helpers[sid]].send_data(data)

if __name__ == '__main__':
    #web.run_app(app)
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
