import socket
import threading
import json
import time
import os
from commands import *

# Server configuration
SERVER = socket.gethostbyname(socket.gethostname())
PORT = os.getenv('PORT')
FORMAT = 'utf-8'
BUFFER = 64

# Environment variables
API_KEY = os.getenv
POWDER_WEBHOOK = os.getenv('POWDER_WEBHOOK')


# Data functions and variables
def load_data(file) -> dict:
    try:
        with open('./db/' + file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(file: str, data: dict):
    with open('./db/' + file, 'w') as f:
        json.dump(data, f, indent=4)

core = load_data('data.json') or {
    'ch': [],
    'dm': []
}
users = load_data('users.json')
lock = threading.Lock()
running = True

def save_all():
    print('[DB] Saving data...')
    save_data('data.json', core)
    save_data('users.json', users)

def send_data(conn: socket.socket, data: dict):
    conn.send((json.dumps(data) + '\n').encode(FORMAT))

# Command handlers
def handle_command(data: dict, conn: socket.socket, addr: tuple) -> bool:
    command = data.get('command', None)

    if command == 'disconnect':  # Disconnect command
        print(f'[DISCONNECT] {addr} disconnected.')
        return False
    elif command == 'test':  # Test command
        conn.send(f'[TEST] Command Received\n'.encode(FORMAT))
    elif command == 'user':  # Track unique users
        username = data.get('username', None)
        version = data.get('version', None)
        
        if username and version:
            with lock:
                if version not in users:
                    users[version] = {"total": 0, "usernames": {}}
                if username not in users[version]["usernames"]:
                    users[version]["total"] += 1

                users[version]["usernames"][username] = time.time()
    elif command == 'ch':  # Crystal Hollows
        request = data.get('request', None)
        event = data.get('event', None)

        if event:
            with lock:
                if request == 'post':
                    core['ch'].append([event, time.time()])
                    if event == '2x Powder':
                        send_webhook(core, 'https://discord.com/api/webhooks/1234567890')
                elif request == 'get':
                    send_data(conn, process_event(core, 'ch'))
    elif command == 'dm':  # Dwarven Mines
        request = data.get('request', None)
        event = data.get('event', None)

        if event:
            with lock:
                if request == 'post':
                    core['dm'].append([event, time.time()])
                elif request == 'get':
                    send_data(conn, process_event(core, 'dm'))
    elif command == 'alloy':  # Divan's Alloy
        player = data.get('player', None)

        if player:
            pass  # TBD
        
    return True

# Client handler
def handle_client(conn, addr):
    print(f'[NEW CONNECTION] {addr} connected.')
    conn.settimeout(60)

    global running
    connected = True
    last_command_time = time.time()
    while connected and running:
        try:
            msg = conn.recv(BUFFER).decode(FORMAT)
        except socket.timeout:
            if time.time() - last_command_time > 24 * 60 * 60:
                print(f'[DISCONNECT] {addr} disconnected due to inactivity.')
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

def handle_commands():
    global running
    while running:
        command = input()
        if command == 'shutdown':
            print('[COMMAND] Initiating server shutdown...')
            running = False
        elif command == 'save':
            save_all()

    save_all()

# Start server
def start():
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
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER, PORT))

    print('[STARTING] Attemping to start server...')
    start()
