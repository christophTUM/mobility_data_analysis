import socket
import threading
import pandas as pd
import io
import struct
import helpers as h
from pathlib import Path
import pickle as p


class Server:

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.PORT = h.PORT
        self.SERVER = h.SERVER
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
            data, filename = self.receive_data_helper(conn)
            if not data:
                connected = False
                continue

            if data is not None:
                print("Received data!")
                pkl_list = pd.read_pickle(io.BytesIO(data))
                # vehicle_id, track_id, modality, modality_precision, df = pd.read_pickle(io.BytesIO(data))
                # df.to_pickle(Path.cwd().parent.joinpath(Path(f"data/tracks/{filename}")))
                p.dump(pkl_list, open(Path.cwd().parent.joinpath(Path(f"data/tracks/{filename}")), 'wb'))
                print(f"Saved {filename}!")

        print(f"[CLOSING CONNECTION] {addr} disconnected.")
        conn.close()

    @staticmethod
    def receive_data_helper(conn):
        filename_header = conn.recv(10)
        if not len(filename_header):
            return False, ""
        filename_length = int(filename_header.decode("utf-8").strip())
        filename = conn.recv(filename_length).decode("utf-8")

        recv_len = conn.recv(4)
        data_size = struct.unpack('>I', recv_len)[0]
        received_payload = b""
        remaining_payload_size = data_size

        while remaining_payload_size != 0:
            received_payload += conn.recv(remaining_payload_size)
            remaining_payload_size = data_size - len(received_payload)
        return received_payload, filename


if __name__ == "__main__":
    new_server = Server()
