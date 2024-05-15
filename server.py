import socket
import threading
import json
import datetime

# Server configuration
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 3389
FORMAT = 'utf-8'
BUFFER = 64

# Data functions
def load_data(file) -> dict:
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(file: str, data: dict):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

# Data variables
core = load_data('data.json')
users = load_data('users.json')
lock = threading.Lock()

# Command handlers
def handle_command(data: dict, conn: socket.socket, addr: tuple) -> bool:
    command = data.get('command', None)

    if command == 'disconnect':  # Disconnect command
        print(f'[DISCONNECT] {addr} disconnected.')
        return False
    elif command == 'test':  # Test command
        conn.send(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}'.encode(FORMAT))
    elif command == 'user':  # Track unique users
        username = data.get('username', None)
        version = data.get('version', None)

        if username:
            with lock:
                if version not in users:
                    users[version] = {"total": 0, "username": {}}
                if username not in users[version]:
                    users[version]["total"] += 1

                users[version]["username"][username] = datetime.datetime.now().isoformat()
                save_data('users.json', users)
    elif command == 'ch':  # Crystal Hollows
        pass
    elif command == 'dm':  # Dwarven Mines
        pass
        
    return True

# Client handler
def handle_client(conn, addr):
    print(f'[NEW CONNECTION] {addr} connected.')

    connected = True
    while connected:
        msg = conn.recv(BUFFER).decode(FORMAT)
        
        if msg:
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                data = {}

            if not handle_command(data, conn, addr):
                connected = False

    conn.close()

# Start server
def start():
    server.listen()
    print(f'[LISTENING] Server is listening on {SERVER}')
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER, PORT))

    print('[STARTING] Attemping to start server...')
    start()
