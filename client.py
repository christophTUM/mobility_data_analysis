import socket
import errno
import time
import pickle
import threading
import pandas as pd
import os
import io
import struct
import helpers as h


FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECT"
HEADER = 64


class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER = h.SERVER
        self.PORT = h.PORT
        self.ADDR = (self.SERVER, self.PORT)
        self.client.connect(self.ADDR)

    def send(self, serialized_data):
        #if serialized_data == DISCONNECT_MESSAGE:
        #    self.client.sendall(struct.pack('>I', len(DISCONNECT_MESSAGE)))
        #    self.client.sendall(DISCONNECT_MESSAGE.encode(FORMAT))
        #else:
        self.client.sendall(struct.pack('>I', len(serialized_data)))
        self.client.sendall(serialized_data)


_client = Client()
path = "data/track_1500000312376.pkl"
with open(os.path.join(path), 'rb') as f:
    _client.send(f.read())
