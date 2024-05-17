import socket
import threading
import json
import time
import os
from commands import *
from handler import handle_command


# Server configuration
SERVER = socket.gethostbyname(socket.gethostname())
PORT = int(os.getenv('PORT'))
FORMAT = 'utf-8'
BUFFER = 256
running = True

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
waifu = load_data('waifu.json') or {}

def save_all() -> None:
    """
    Save all data to JSON files.
    """

    print('[DB] Saving data...')
    save_data('data.json', core)
    save_data('users.json', users)
    save_data('waifu.json', waifu)

def send_data(conn: socket.socket, data: dict) -> None:
    """
    Send data to a client.
    """

    conn.send((json.dumps(data) + '\n').encode(FORMAT))


# Client handlers
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
            print(f'[CONNECTIONS] {threading.active_count() - 2} active connections.')

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
