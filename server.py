import asyncio
import socket
import pickle
from game import Game
from communication import Event
import traceback

games: dict[int, Game] = {}
id_count = 0
waiting = {}


async def handle_client(client, player_id):
    global id_count
    if len(waiting) < 6:
        waiting[player_id] = client
    game_id = None
    player = 0
    print(f"Player {player_id} connected to lobby")
    loop = asyncio.get_event_loop()
    client.send(str.encode(str(player_id)))
    response = b""
    while True:
        try:
            data = pickle.loads(await loop.sock_recv(client, 4096))
            if not data:
                break
            if data == "get":
                lobby = waiting.copy()
                del lobby[player_id]
                response = pickle.dumps(list(lobby.keys()))
                await loop.sock_sendall(client, response)
            elif isinstance(data, Event):
                event = data
                if event.type == Event.EventType.ACCEPT:
                    game_id = int(event.message)
                    games[game_id].ready = True
                    player = 1
                    # await loop.sock_sendall(client, pickle.dumps(games[game_id]))
                    print(player)
                    await loop.sock_sendall(client,
                                            pickle.dumps(Event(type=Event.EventType.PLAYER, message=str(player))))
                    await loop.sock_sendall(waiting[int(event.message)], pickle.dumps(games[game_id]))
                elif event.type == Event.EventType.PLAY:
                    game = games[game_id]
                    if game.connected():
                        if player == 1:
                            print(event.message != "")
                        if event.message != "":
                            print(player)
                            game.play(player, event.message)
                            print("Sending game to player", player, "and", event.message)
                            print(game.moves)
                        await loop.sock_sendall(client, pickle.dumps(game))
                    await loop.sock_sendall(client,
                                            pickle.dumps(Event(type=Event.EventType.PLAYER, message=str(player))))

            else:
                player_chosen = int(data)
                print(player_id, player_chosen)
                if player_chosen in waiting:
                    response = pickle.dumps(Event(type=Event.EventType.INVITE, message=player_id))
                    await loop.sock_sendall(waiting[player_chosen], response)
                    # response = pickle.dumps('Invitation sent')
                    # await loop.sock_sendall(client, response)
                    game_id = player_id
                    games[game_id] = Game(game_id)
                    # await loop.sock_sendall(client, pickle.dumps(games[game_id]))
                    await loop.sock_sendall(client,
                                            pickle.dumps(Event(type=Event.EventType.PLAYER, message=str(player))))

                else:
                    response = pickle.dumps("Player not found")
                    await loop.sock_sendall(client, response)
        except Exception as e:
            print(str(e))
            break
    print("Lost connection")
    try:
        del waiting[player_id]
        print("Removing player from lobby...", player_id)
    except Exception as e:
        print(e)
    id_count -= 1
    client.close()


async def main():
    global id_count
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 3333))
    server.listen(5)
    server.setblocking(False)
    print("Waiting for a connection, Server Started")
    loop = asyncio.get_event_loop()

    while True:
        client, _ = await loop.sock_accept(server)
        print("Connected to:", _)
        id_count += 1
        p = 0
        try:
            loop.create_task(handle_client(client, id_count))
        except Exception as e:
            print(e)
        # game_id = (id_count - 1) // 2
        # if id_count % 2 == 1:
        #     games[game_id] = Game(game_id)
        #     print("Creating a new game...")
        # else:
        #     games[game_id].ready = True
        #     p = 1
        # loop.create_task(handle_client(client, p, game_id))


if __name__ == '__main__':
    asyncio.run(main())
