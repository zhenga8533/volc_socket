import time
import socket

SERVER = 'volca.dev'
PORT = 3389

def send(client, msg):
    client.send(msg.encode('utf-8'))
    response = client.recv(1024).decode('utf-8')
    print(response)

if __name__ == '__main__':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))

    send(client, '{"command": "test"}')

    # sleep 5 seconds
    time.sleep(5)

    send(client, '{"command": "disconnect"}')
    client.close()
