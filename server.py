import asyncio
import socket
import pickle
from game import Game
from communication import Event


class Server:
    def __init__(self, host, port):
        self.addr = (host, port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.addr)
        self.server.listen(3)
        self.server.setblocking(False)
        self.id_count = 0
        self.games = {}  # games dictionary {game_id: Game} to keep track of games
        self.waiting = {}  # waiting dictionary {player_id: client} to keep track of players waiting for game
        self.connected = {}  # connected dictionary {player_id: client} to keep track of connected players all over the server
        self.playing = {}  # playing dictionary {host_player_id: other_player_id} to keep track of players playing in a game

    async def start(self):
        """
        Start server and listen for connections to handle them
        """

        print("Waiting for a connection, Server Started")
        loop = asyncio.get_event_loop()

        while True:
            client, _ = await loop.sock_accept(self.server)
            print("Connected to:", _)
            self.id_count += 1
            p = 0
            try:
                loop.create_task(self.handle_client(client, self.id_count))
            except Exception as e:
                print(e)

    def add_to_waiting(self, client, player_id):
        """
        Add client to waiting list
        :param client:
        :param player_id:
        :return:
        """
        if len(self.waiting) == 6:
            client.close()
            return
        self.connected[player_id] = client
        self.waiting[player_id] = client

    def lobby(self, player_id) -> list:
        """
        Return list of players in lobby
        :param player_id: player requesting lobby
        :return: list of players in lobby
        """
        lobby = self.waiting.copy()
        try:
            del lobby[player_id]
        except KeyError:
            pass
        return list(lobby.keys())

    def invite(self, player_id, player_chosen) -> Event | None:
        """
        Invite player to game
        :param player_id:
        :param player_chosen:
        :return: event object or None
        """
        if player_chosen in self.waiting:
            self.games[player_id] = Game(player_id)
            event = self.__process_event(Event.EventType.INVITE, str(player_id))
            return event
        return None

    def accept_invitation(self, game_id: int, player_id: int) -> Game | None:
        """
        Accept invitation to game
        :param game_id: id of game to join
        :param player_id: id of player accepting invitation
        :return: event object or None
        """
        try:
            self.games[game_id].ready = True
            self.playing[game_id] = player_id
            del self.waiting[game_id]
            del self.waiting[player_id]
        except KeyError:
            return None
        return self.games[game_id]

    def decline_invitation(self, game_id: int, player_id: int) -> Event:
        """
        Decline invitation to game
        :param game_id: id of game to decline
        :param player_id: id of player declining invitation
        :return: decline event
        """
        try:
            del self.games[game_id]
            self.waiting[game_id] = self.connected[game_id]
            self.waiting[player_id] = self.connected[player_id]
        except KeyError:
            raise KeyError("Game not found")
        return self.__process_event(Event.EventType.DECLINE, str(game_id))

    def play(self, game_id, player, move) -> Game | None:
        """
        Play move in game
        :param game_id: id of game to make play
        :param player: player making play
        :param move: move to make
        :return:
        """
        try:
            game = self.games[game_id]
        except KeyError:
            pass
        if game.connected():
            game.play(player, move)
            return game
        return None

    def __process_event(self, event_type: Event.EventType, message):
        """
        Process events from client
        :param event_type: specified event type
        :param message: message to be sent
        :return:
        """
        return Event(type=event_type, message=message)

    async def handle_client(self, client, player_id: int):
        """
        Handle client connection
        :param client: clientTestHandleClient socket
        :param player_id: player id
        """
        self.add_to_waiting(client, player_id)
        game_id = None
        player = 0
        print(f"Player {player_id} connected to lobby")
        loop = asyncio.get_event_loop()
        client.send(str.encode(str(player_id)))
        while True:
            try:
                data = pickle.loads(await loop.sock_recv(client, 4096))
                if not data:
                    break
                elif data == "get":
                    response = pickle.dumps(self.lobby(player_id))
                    await loop.sock_sendall(client, response)
                elif isinstance(data, Event):
                    event = data
                    print(event, player_id)
                    if event.type == Event.EventType.ACCEPT:
                        game_id = int(event.message)
                        game = self.accept_invitation(game_id, player_id)
                        player = 1
                        await loop.sock_sendall(client,
                                                pickle.dumps(game))
                        await loop.sock_sendall(self.connected[game_id], pickle.dumps(game))
                    elif event.type == Event.EventType.DECLINE:
                        game_id = int(event.message)
                        response = self.decline_invitation(game_id, player_id)
                        await loop.sock_sendall(client, pickle.dumps(response))
                        await loop.sock_sendall(self.connected[game_id],
                                                pickle.dumps(response))
                    elif event.type == Event.EventType.PLAY:
                        if self.games[game_id].connected():
                            if event.message != "":
                                game = self.play(game_id, player, event.message)
                                if game:
                                    print("Sending game to player", player, "and", event.message)
                                    print(self.games[game_id].moves)
                                    await loop.sock_sendall(client, pickle.dumps(game))
                                    await loop.sock_sendall(self.connected[game_id], pickle.dumps(game))
                                    if game.both_moved():
                                        self.waiting[game_id] = self.connected[game_id]
                                        del self.playing[game_id]
                                        self.waiting[player_id] = client
                            await loop.sock_sendall(client, pickle.dumps(self.games[game_id]))
                    await loop.sock_sendall(client,
                                            pickle.dumps(self.__process_event(Event.EventType.PLAYER, player)))

                else:
                    player_chosen = int(data)
                    print(player_id, player_chosen)
                    invite = self.invite(player_id, player_chosen)
                    if invite:
                        game_id = player_id
                        player = 0
                        await loop.sock_sendall(client,
                                                pickle.dumps(self.__process_event(Event.EventType.PLAYER, str(player))))
                        await loop.sock_sendall(self.waiting[player_chosen], pickle.dumps(invite))

                    else:
                        response = pickle.dumps("Player not found")
                        await loop.sock_sendall(client, response)
            except Exception as e:
                print(e)
                break
        print("Lost connection")
        try:
            del self.waiting[player_id]
            del self.connected[player_id]
            del self.playing[game_id]
            del self.games[game_id]
            print("Removing player from lobby...", player_id)
        except Exception as e:
            print(e)
        self.id_count -= 1
        client.close()

    def close(self):
        """
        Close serverKeyError
        """
        self.server.close()


if __name__ == '__main__':
    server = Server('127.0.0.1', 3333)
    asyncio.run(server.start())
