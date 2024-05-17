import socket
import threading
import json
import time
import os
from datetime import datetime
from commands import *


# Server configuration
SERVER = socket.gethostbyname(socket.gethostname())
PORT = int(os.getenv('PORT'))
FORMAT = 'utf-8'
BUFFER = 256

# Environment variables
API_KEY = os.getenv('API_KEY')
POWDER_WEBHOOK = os.getenv('POWDER_WEBHOOK')


# Data functions
def load_data(file: str) -> dict:
    """
    Load data from a JSON file.
    
    :param file: The file to load data from.
    """

    try:
        with open('./db/' + file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(file: str, data: dict) -> None:
    """
    Save data to a JSON file.

    :param file: The file to save data to.
    :param data: The data to save.
    """

    with open('./db/' + file, 'w') as f:
        json.dump(data, f, indent=4)

# Data variables
core = load_data('data.json') or {
    'ch': [],
    'dm': [],
    'alloy': 0
}
users = load_data('users.json') or {}

# Control variables
running = True
lock = threading.Lock()
last_ch_powder = 0
last_dm_powder = 0

def save_all() -> None:
    """
    Save all data to JSON files.
    """

    print('[DB] Saving data...')
    save_data('data.json', core)
    save_data('users.json', users)

def send_data(conn: socket.socket, data: dict) -> None:
    """
    Send data to a client.
    """

    conn.send((json.dumps(data) + '\n').encode(FORMAT))


# Client handlers
def handle_command(data: dict, conn: socket.socket, addr: tuple) -> bool:
    """
    Handle a command from a client.
    
    :param data: The data to handle.
    :param conn: The client connection.
    :param addr: The client address.
    """

    command = data.get('command', None)
    player = data.get('player', None)
    if command is None or player is None:
        return True

    if command == 'disconnect':  # Disconnect command
        print(f'[DISCONNECT] {addr} disconnected.')
        return False
    elif command == 'test':  # Test command
        conn.send(f'[TEST] Command Received\n'.encode(FORMAT))
    elif command == 'user':  # Track unique users
        version = data.get('version', None)
        
        if player and version:
            with lock:
                if version not in users:
                    users[version] = {"total": 0, "usernames": {}}
                if player not in users[version]["usernames"]:
                    users[version]["total"] += 1

                users[version]["usernames"][player] = time.time()
    elif command == 'ch':  # Crystal Hollows
        request = data.get('request', None)
        event = data.get('event', None)

        if event:
            with lock:
                if request == 'post':
                    core['ch'].append([event, time.time()])
                    global last_ch_powder

                    if time.time() - last_ch_powder > 1_200 and event == '2x Powder':
                        last_ch_powder = time.time()
                        ping = '<@&1240705901908852826>'
                        msg = ' ⚑ The 2x Powder event starts in 20 seconds! This is a passive event! It\'s happening everywhere in the Crystal Hollows!'
                        send_webhook(player, ping + msg, POWDER_WEBHOOK)
                elif request == 'get':
                    send_data(conn, process_event(core, 'ch'))
    elif command == 'dm':  # Dwarven Mines
        request = data.get('request', None)
        event = data.get('event', None)

        if event:
            with lock:
                if request == 'post':
                    core['dm'].append([event, time.time()])
                    global last_dm_powder

                    if time.time() - last_dm_powder > 1_200 and event == '2x Powder':
                        last_dm_powder = time.time()
                        ping = '<@&1240705811580194878>'
                        msg = ' ⚑ The 2x Powder event starts in 20 seconds! This is a passive event! It\'s happening everywhere in the Dwarven Mines!'
                        send_webhook(player, ping + msg, POWDER_WEBHOOK)
                elif request == 'get':
                    send_data(conn, process_event(core, 'dm'))
    elif command == 'alloy':  # Divan's Alloy
        player = data.get('player', None)
        last_alloy = time.time() - core['alloy']

        if last_alloy > 60:
            with lock:
                if request == 'post':
                    core['alloy'] = time.time()
                    with open('./db/alloy.txt', 'a') as f:
                        f.write(f'{player}: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}\n')
                elif request == 'get':
                    send_data(conn, {
                        'command': 'alloy',
                        'last_alloy': last_alloy
                    })
        
    return True

def handle_client(conn: socket.socket, addr: tuple) -> None:
    """
    Handle a client connection.
    
    :param conn: The client connection.
    :param addr: The client address.
    """

    global running
    connected = True
    last_command_time = time.time()
    conn.settimeout(60)
    print(f'[CONNECT] {addr} connected.')

    while connected and running:
        try:
            msg = conn.recv(BUFFER).decode(FORMAT)
        except socket.timeout:
            if time.time() - last_command_time > 24 * 60 * 60:
                connected = False

        if msg:
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                data = {}

            if not handle_command(data, conn, addr):
                connected = False
            last_command_time = time.time()
        
    conn.close()
    print(f'[DISCONNECT] {addr} disconnected.')

def handle_commands() -> None:
    """
    Handle server commands.
    """

    global running
    while running:
        command = input()
        if command == 'shutdown':
            print('[COMMAND] Initiating server shutdown...')
            running = False
        elif command == 'save':
            save_all()
        elif command == 'connections':
            print(f'[CONNECTIONS] {threading.active_count() - 1} active connections.')

    save_all()


# Start server
def start():
    """
    Start the server.
    """

    print('[STARTING] Attemping to start server...')
    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER, PORT))

    server.listen()
    server.settimeout(10)
    threading.Thread(target=handle_commands).start()
    print(f'[LISTENING] Server is listening on {SERVER}')

    global running
    while running:
        try:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
        except socket.timeout:
            continue

    print('[SHUTDOWN] Shutting down server...')
    server.close()

if __name__ == '__main__':
    start()
