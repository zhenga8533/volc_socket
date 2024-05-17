import os
import socket


API_KEY = os.getenv('API_KEY')
POWDER_WEBHOOK = os.getenv('POWDER_WEBHOOK')
SERVER = socket.gethostbyname(socket.gethostname())
PORT = int(os.getenv('PORT'))
FORMAT = 'utf-8'
BUFFER = 256
