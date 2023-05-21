import socket
import pickle
import enum


class Event:
    class EventType(enum.Enum):
        INVITE = 'INVITATION'
        ACCEPT = 'ACCEPT'
        DECLINE = 'DECLINE'
        PLAYER = 'PLAYER'
        PLAY = "PLAY"

    def __init__(self, type: EventType, message: str = ""):
        self.type = type
        self.message = message


class Communication:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 3333
        self.addr = (self.server, self.port)
        self.player = self.connect()

    def get_player(self):
        return self.player

    def connect(self):
        try:
            self.client.connect(self.addr)
            data = self.client.recv(2048).decode()
            if data:
                return data
        except Exception as e:
            print(e)

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            data = self.client.recv(2048)
            if len(data) > 0:
                return pickle.loads(data)
        except socket.error as e:
            raise e

    def recieve(self, buffer: int = 2048):
        try:
            data = self.client.recv(buffer)
            if len(data) > 0:
                return pickle.loads(data)
        except socket.error as e:
            print("RECIEVE ERROR: ", e)

    def close(self):
        self.client.close()
