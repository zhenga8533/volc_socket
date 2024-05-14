import socket
import threading
import json

SERVER = socket.gethostbyname(socket.gethostname())
PORT = 3389
FORMAT = 'utf-8'
BUFFER = 64

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER, PORT))

def handle_command(data: dict, conn: socket.socket, addr: tuple) -> bool:
    if data['command'] == 'disconnect':
        print(f'[DISCONNECT] {addr} disconnected.')
        return False
    elif data['command'] == 'test':
        conn.send('Test command received.'.encode(FORMAT))
        
    return True

def handle_client(conn, addr):
    print(f'[NEW CONNECTION] {addr} connected.')

    connected = True
    while connected:
        msg = conn.recv(BUFFER).decode(FORMAT)
        if msg:
            data = json.loads(msg)

            if not handle_command(data, conn, addr):
                connected = False

    conn.close()

def start():
    server.listen()
    print(f'[LISTENING] Server is listening on {SERVER}')
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')

if __name__ == '__main__':
    print('[STARTING] Attemping to start server...')
    start()
