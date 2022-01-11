import socket
import errno
import time
import threading
import pandas as pd
import io
import struct
import helpers as h
import pickle

HEADER = 64  # potential concern
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECT"


class Server:

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.PORT = h.PORT
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)
        self.server.bind(self.ADDR)

        print("[STARTING] server is starting...")
        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.SERVER}")

        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")

        connected = True
        while connected:
            data = self.receiveDataHelper(conn)
            if not data:
                connected = False
                continue

            if data is not None:
                print("Received data!")
                vehicle_id, track_id, modality, modality_precision, df = pd.read_pickle(io.BytesIO(data))
                df.to_pickle("data/my_pickle.pkl")
                print("Saved pickle file!")

        print(f"[CLOSING CONNECTION] {addr} disconnected.")
        conn.close()

    def receiveDataHelper(self, conn):
        recv_test = conn.recv(4)
        if recv_test == b"":
            time.sleep(1)
            return False

        data_size = struct.unpack('>I', recv_test)[0]
        received_payload = b""
        remaining_payload_size = data_size

        while remaining_payload_size != 0:
            print(remaining_payload_size)
            received_payload += conn.recv(remaining_payload_size)
            remaining_payload_size = data_size - len(received_payload)
        return received_payload


new_server = Server()
