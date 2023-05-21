class Game:
    """
    Class to represent Rock Scissors Paper game.
    """

    def __init__(self, id_: int):
        """
        :param id_: int
        """
        self.p1_moved = False
        self.p2_moved = False
        self.id = id_
        self.ready = False
        self.moves = [None, None]
        self.wins = [0, 0]
        self.ties = 0
        self.rounds = 0

    def get_player_move(self, player: [0, 1]):
        """
        Method to get the move of a player.

        :param player: [0,1]
        :return: move
        """
        return self.moves[player]

    def play(self, player: [0, 1], move: str):
        """
        Method to make a move.
        :param player: [0,1]
        :param move: [R, P, S]
        :return: None
        """
        self.moves[player] = move
        if player == 0:
            self.p1_moved = True
        else:
            self.p2_moved = True

    def connected(self):
        """
        Method to check if both players are connected.
        :return:
        """
        return self.ready

    def both_moved(self):
        """
        Method to check if both players have made a move.
        :return:
        """
        return self.p1_moved and self.p2_moved

    def winner(self) -> [-1, 0, 1]:
        """
        Method to determine the winner of a round.
        :return: [-1, 0, 1]
        """
        p1 = self.moves[0].upper()[0]
        p2 = self.moves[1].upper()[0]
        winner = -1
        if p1 == "R" and p2 == "S":
            winner = 0
        elif p1 == "S" and p2 == "R":
            winner = 1
        elif p1 == "P" and p2 == "R":
            winner = 0
        elif p1 == "R" and p2 == "P":
            winner = 1
        elif p1 == "S" and p2 == "P":
            winner = 0
        elif p1 == "P" and p2 == "S":
            winner = 1
        self.rounds += 1
        return winner

    def reset_moves(self):
        """
        Method to reset the moves of both players.
        :return: None
        """
        self.p1_moved = False
        self.p2_moved = False
