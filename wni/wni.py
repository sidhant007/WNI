import click
import time
import threading
import os
import pickle
from prettytable import PrettyTable
import base64
import socketio
from collections import deque

sio = socketio.Client()
MY_ID = -1
MSGS = dict()

@click.group()
def cli():
    pass

@click.command()
@click.option("--user", "-u", "user", required=True,
              help="Your new user id",
              type=str)
@click.option("--dev/--prod", default=False)
def register(user, dev):
    """Register a new user with the given name. Acts as pwd too right now."""
    if dev is True:
        sio.connect('http://localhost:8080')
    else:
        sio.connect('http://104.248.156.240:8080')
    sio.emit('add_user', {'user': user})

@click.command()
#@click.option("--id", "-id", "room_id", required=True,
#              help="A string to denote this request uniquely",
#              type=str)
#@click.option("--file", "-f", "code_file", required=True,
#              help="Path to code file to be attached",
#              type=click.Path(exists=True, dir_okay=False, readable=True),
#)
#@click.option("--nodes", "-n", "n", required=True,
#              help="Number of nodes (excluding myself) needed, should be between [1, 20]",
#              type=click.IntRange(1, 20))
@click.argument('room_id', type=str)
@click.argument('code_file', type=click.Path(exists=True, readable=True))
@click.argument('n', type=click.IntRange(1, 20))
@click.option("--user", "-u", "user", required=True,
              help="Your user id",
              type=str)
@click.option("--rate", "-r", "rate", default=5,
              help="Amount of wni-money you will give per second",
              type=click.IntRange(1, 100))
@click.option("--seconds", "-s", "seconds", default=60,
              help="Number of seconds for which your code is run on all PCs",
              type=click.IntRange(30, 100))
@click.option("--dev/--prod", default=False)
def request(room_id, code_file, n, user, rate, seconds, dev):
    """Request computation power of others"""
    if dev is True:
        sio.connect('http://localhost:8080')
    else:
        sio.connect('http://104.248.156.240:8080')
    encoded_file_content = base64.b64encode(open(code_file, 'rb').read())
    sio.emit('make_request', {'user': user, 'room_id': room_id, 'code': encoded_file_content, 'n': n, 'rate': rate, 'seconds': seconds})
    sio.wait() #debug

@click.command()
#@click.option("--id", "-id", "room_id", required=True,
#              help="A string to denote the request to join uniquely",
#              type=str)
@click.argument('room_id', type=str)
@click.option("--user", "-u", "user", required=True,
              help="Your user id",
              type=str)
@click.option("--dev/--prod", default=False)
def join(room_id, user, dev):
    """Join a request to do computation for it"""
    print("Waiting to connect")

    if dev is True:
        sio.connect('http://localhost:8080')
    else:
        sio.connect('http://104.248.156.240:8080')
    sio.emit('join_request', {'user': user, 'room_id': room_id})
    sio.wait() #debug

@click.command()
@click.option("--user", "-u", "user", required=True,
              help="Your user id",
              type=str)
@click.option("--dev/--prod", default=False)
def show(user, dev):
    """Show all requests waiting"""
    print("WNI: Waiting to connect to server")

    if dev is True:
        sio.connect('http://localhost:8080')
    else:
        sio.connect('http://104.248.156.240:8080')
    sio.emit('list_all_requests', {'user': user})

cli.add_command(register)
cli.add_command(request)
cli.add_command(show)
cli.add_command(join)

@sio.event
def connect():
    print("WNI: Connection established to server")

@sio.event
def disconnect(environ):
    print("WNI: Disconnected from server")

@sio.event
def register_clean_exit(environ):
    sio.disconnect()

@sio.event
def print_table(data):
    x = PrettyTable()
    x.field_names = ["ID", "#Nodes Reqd", "#Nodes Joined", "Is Running?", "Rate per second", "#Seconds"]
    for y in data['table']:
        x.add_row(y)
    print(data['entry_message'])
    print(x)
    sio.disconnect()

@sio.event
def show_failed(data):
    print(data['error_message'])
    sio.disconnect()

def force_exit_root():
    print("WNI: Your time is up :)")
    sio.emit('cleanup_root')

@sio.event
def exit_maaro(environ):
    os._exit(0)

def force_exit_helper():
    print("WNI: Time of request is up :)")
    sio.emit('cleanup_helper')
    sio.disconnect()

@sio.event
def run_code(data):
    global MY_ID
    MY_ID = data['id']
    if(MY_ID != 0):
        print("WNI: Running another user's code")
        threading.Timer(12.0, force_exit_helper).start()
    else:
        print("WNI: Running your code")
        threading.Timer(12.0, force_exit_root).start()
    file_data = base64.b64decode(data['code'])
    open('tmp.py', 'wb').write(file_data)
    exec(open("./tmp.py").read())
    if(MY_ID != 0):
        print("WNI: Exited running the other user's code. Still time not up so dont quit")
        time.sleep(MY_ID * 2) #Super ugly hack
        sio.emit('closing_helper_correctly')
    else:
        print("WNI: Exiting from your code. Still time not up so dont quit")
        #sio.disconnect()

@sio.event
def register_request_fail(data):
    print(data['error_message'])
    sio.disconnect()

@sio.event
def make_request_fail(data):
    print(data['error_message'])
    sio.disconnect()

@sio.event
def join_request_fail(data):
    print(data['error_message'])
    sio.disconnect()

@sio.event
def print_message(data):
    print(data['message'])

@sio.event
def receive_data_from_server(data):
    send_id = data['send_id']
    pickled_data = data['pickled_data']
    if send_id not in MSGS:
        MSGS[send_id] = deque()
    MSGS[send_id].append(pickled_data)

@sio.event
def disconnect_this_helper(environ):
    print("WNI: Exited running the other user's code")
    sio.disconnect()

@sio.event
def exit_code(data):
    print(data['error_message'])
    sio.disconnect()
    os._exit(0); #Forced exit

def send_data(receive_id, data):
    global MY_ID
    #print("Receive_id", receive_id)
    pad_data = {'imp_data': data}
    #print("Padded Data", pad_data)
    pickled_data = pickle.dumps(pad_data)
    sio.emit('send_data', {'send_id': MY_ID, 'receive_id': receive_id, 'pickled_data': pickled_data})

def receive_data(send_id):
    while True:
        if send_id in MSGS:
            if len(MSGS[send_id]) != 0:
                pickled_data = MSGS[send_id].popleft()
                data = pickle.loads(pickled_data)
                return data['imp_data']
    return -1
