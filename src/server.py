import socket
import threading
import json
import time
from commands import *
from constants import *
from handler import handle_command, save_all


# Server configuration
running = True

# Handlers
def handle_client(conn: socket.socket, addr: tuple) -> None:
    """
    Handle a client connection.
    
    :param conn: The client connection.
    :param addr: The client address.
    """

    global running
    connected = True
    received = False
    last_command_time = time.time()
    conn.settimeout(60)

    while connected and running:
        msg = None

        try:
            msg = conn.recv(BUFFER).decode(FORMAT)
        except socket.timeout:
            if time.time() - last_command_time > 3_600 or not received:
                connected = False
                break
            continue
        except Exception as e:
            print(f'Error receiving data from {addr}: {e}')
            msg = None
            connected = False
            break

        if msg:
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                data = {}

            if data.get('command', None) == 'disconnect':
                connected = False
                break
            elif handle_command(data, conn):
                received = True
                last_command_time = time.time()
        elif time.time() - last_command_time > 3_600 or not received:
            connected = False
            break
        
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
