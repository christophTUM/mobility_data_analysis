import socket
import struct
import helpers as h
import os


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

    def send(self, serialized_data, filename):
        #if serialized_data == DISCONNECT_MESSAGE:
        #    self.client.sendall(struct.pack('>I', len(DISCONNECT_MESSAGE)))
        #    self.client.sendall(DISCONNECT_MESSAGE.encode(FORMAT))
        #else:
        filename_header = f"{len(filename):<{10}}".encode("utf-8")
        self.client.send(filename_header + filename)
        self.client.sendall(struct.pack('>I', len(serialized_data)))
        self.client.sendall(serialized_data)


if __name__ == "__main__":
    _client = Client()
    path = "model/track_1500000312376.pkl"
    with open(path, 'rb') as f:
        filename = os.path.basename(path).encode("utf-8")
        _client.send(f.read(), filename)
