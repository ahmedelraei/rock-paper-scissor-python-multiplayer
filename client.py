import pickle
from communication import Communication


def main():
    if input("Do you want to play? (y/n): ") == "y":
        comm = Communication()
        player = int(comm.get_player())
        print(f"You are player {player}")
        lobby = None
        while True:
            if lobby:
                print(lobby)
                for player in lobby:
                    print(f"Player {player} is ready to play")
                player_chosen = input("Choose Player to play with (Enter ID): ")
                if int(player_chosen) in lobby:
                    data = comm.send(player_chosen)
                    print(data)
                    input("Press any key to choose another player..")
            else:
                try:
                    lobby = comm.send("get")
                    # print("Waiting for players to join...")
                except:
                    pass

    # comm.close()


if __name__ == "__main__":
    main()
