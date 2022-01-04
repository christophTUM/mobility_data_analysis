import socket

HEADER = 64  # potential concern
PORT = 5050
SERVER = "192.168.178.123"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(ADDR)

    def send(self, msg):
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)
        print(self.client.recv(2048).decode())  # ideal same protocol as server


_client = Client()
_client.send("Hello world!")
input()
_client.send("Hello everyone!")
input()
_client.send("Hello Christoph!")
_client.send(DISCONNECT_MESSAGE)
