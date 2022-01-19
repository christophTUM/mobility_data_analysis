import socket
import struct
from pathlib import Path


class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER = "10.183.119.142"
        self.PORT = 5050
        self.ADDR = (self.SERVER, self.PORT)
        self.client.connect(self.ADDR)

    def send(self, serialized_data, filename):
        filename_header = f"{len(filename):<{10}}".encode("utf-8")
        self.client.send(filename_header + filename)
        self.client.sendall(struct.pack('>I', len(serialized_data)))
        self.client.sendall(serialized_data)


if __name__ == "__main__":
    _client = Client()
    dir_with_tracks = Path("data/test/")
    for file in dir_with_tracks.glob('*.*'):
        if not file.name == ".DS_Store":
            with open(file, 'rb') as f:
                f_name = file.name.encode("utf-8")
                _client.send(f.read(), f_name)
