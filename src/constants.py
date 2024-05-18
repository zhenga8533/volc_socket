import os
import socket


API_KEY = os.getenv('API_KEY')

# Server Variables
SERVER = socket.gethostbyname(socket.gethostname())
PORT = int(os.getenv('PORT'))
FORMAT = 'utf-8'
BUFFER = 256

# Discord Variables
CH_PING = '<@&1240705901908852826>'
DM_PING = '<@&1240705811580194878>'
POWDER_WEBHOOK = os.getenv('POWDER_WEBHOOK')
