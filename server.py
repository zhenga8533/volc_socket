import socket
import threading

PORT = 8533
SERVER = socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'
BUFFER = 64

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER, PORT))

def handle_client(conn, addr):
    print(f'[NEW CONNECTION] {addr} connected.')

    connected = True
    while connected:
        msg_length = conn.recv(BUFFER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == 'disconnect':
                connected = False
            print(f'[{addr}] {msg}')
            conn.send('Message received'.encode(FORMAT))

    conn.close()

def start():
    server.listen()
    print(f'[LISTENING] Server is listening on {SERVER}')
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f'[ACTIVE CONNECTIONS] {threading.activeCount() - 1}')

print('[STARTING] Attemping to start server...')
start()
