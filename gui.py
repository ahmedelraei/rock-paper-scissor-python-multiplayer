import pygame
from communication import Communication, Event
from game import Game

pygame.font.init()

width = 700
height = 700
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")


class Button:
    def __init__(self, text, x, y, color, width=150, height=100, value=None):
        self.text = text
        self.value = str(value) if value is not None else text
        self.x = x
        self.y = y
        self.color = color
        self.width = width
        self.height = height

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont("comicsans", 40)
        text = font.render(self.text, 1, (255, 255, 255))
        win.blit(text, (self.x + round(self.width / 2) - round(text.get_width() / 2),
                        self.y + round(self.height / 2) - round(text.get_height() / 2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False


def redraw_window(win, game: Game, p, invitation=None):
    win.fill((128, 128, 128))
    if invitation:
        accept_btn.draw(win)
        decline_btn.draw(win)
    elif not game and lobby_btns:
        for btn in lobby_btns:
            btn.draw(win)
    elif not lobby_btns:
        font = pygame.font.SysFont("comicsans", 80)
        text = font.render("Waiting for Player...", 1, (255, 0, 0), True)
        win.blit(text, (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2))
    else:
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Your Move", 1, (0, 255, 255))
        win.blit(text, (80, 200))

        text = font.render("Opponents", 1, (0, 255, 255))
        win.blit(text, (380, 200))

        move1 = game.get_player_move(0)
        move2 = game.get_player_move(1)
        if game.both_moved():
            text1 = font.render(move1, 1, (0, 0, 0))
            text2 = font.render(move2, 1, (0, 0, 0))
        else:
            if game.p1_moved and p == 0:
                text1 = font.render(move1, 1, (0, 0, 0))
            elif game.p1_moved:
                text1 = font.render("Locked In", 1, (0, 0, 0))
            else:
                text1 = font.render("Waiting...", 1, (0, 0, 0))

            if game.p2_moved and p == 1:
                text2 = font.render(move2, 1, (0, 0, 0))
            elif game.p2_moved:
                text2 = font.render("Locked In", 1, (0, 0, 0))
            else:
                text2 = font.render("Waiting...", 1, (0, 0, 0))

        if p == 1:
            win.blit(text2, (100, 350))
            win.blit(text1, (400, 350))
        else:
            win.blit(text1, (100, 350))
            win.blit(text2, (400, 350))

        for btn in btns:
            btn.draw(win)

    pygame.display.update()


accept_btn = Button("Accept Invitation", 50, 100, (255, 0, 0), 500)
decline_btn = Button("Decline Invitation", 50, 350, (255, 0, 0), 500)
btns = [Button("Rock", 50, 500, (0, 0, 0)), Button("Scissors", 250, 500, (255, 0, 0)),
        Button("Paper", 450, 500, (0, 255, 0))]
lobby_btns = []


def main():
    global lobby_btns
    run = True
    clock = pygame.time.Clock()
    try:
        comm = Communication()
        player = comm.get_player()
        player = player and int(player) or None
        print(player)
        print(f"You are player {player}")
    except Exception as e:
        print("ERROR ", e)
    game = None
    invitation = None
    message = "get"
    while run:
        try:
            data = comm.send(message)
            print(data)
        except Exception as e:
            run = False
            break
        if isinstance(data, Game):
            print(data)
            game = data
            invitation = None
            message = Event(type=Event.EventType.PLAY)
        if isinstance(data, Event):
            event = data
            if event.type == Event.EventType.INVITE:
                player_id = event.message
                accept_btn.text = f"Accept Invitation From Player {player_id}"
                invitation = player_id
            elif event.type == Event.EventType.DECLINE:
                invitation = None
                message = "get"
            elif event.type == Event.EventType.PLAYER:
                player = int(event.message)
                message = Event(type=Event.EventType.PLAY)
                # print(f"You are player {player} in this game")

        elif isinstance(data, list):
            lobby = data
            lobby_btns = []
            y = 0
            for player in lobby:
                y += 130
                lobby_btns.append(Button(f"Player: {player}", 250, y, (255, 0, 0), value=player))
        if isinstance(game, Game):
            if game.both_moved():
                redraw_window(win, game, player)
                pygame.time.delay(500)
                # try:
                #     game = comm.send("reset")
                # except Exception as e:
                #     run = False
                #     print("Couldn't get game")
                #     print(e)
                #     break

                font = pygame.font.SysFont("comicsans", 90)
                if (game.winner() == 1 and player == 1) or (game.winner() == 0 and player == 0):
                    text = font.render("You Won!", 1, (255, 0, 0))
                elif game.winner() == -1:
                    text = font.render("Tie Game!", 1, (255, 0, 0))
                else:
                    text = font.render("You Lost...", 1, (255, 0, 0))

                win.blit(text, (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2))
                pygame.display.update()
                pygame.time.delay(2000)
                game = None
                message = 'get'

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for btn in lobby_btns:
                    if btn.click(pos):
                        event: Event = comm.send(btn.value)
                        if isinstance(event, Event):
                            player = int(event.message)
                            message = Event(type=Event.EventType.PLAY)
                if accept_btn.click(pos):
                    message = Event(type=Event.EventType.PLAY)
                    comm.send(Event(type=Event.EventType.ACCEPT, message=str(invitation)))
                    game = comm.recieve(4096)
                    print(game)
                    invitation = None
                    player = 1

                if decline_btn.click(pos):
                    message = 'get'
                    comm.send(Event(type=Event.EventType.DECLINE, message=str(invitation)))
                    invitation = None

                if game:
                    for btn in btns:
                        if btn.click(pos) and game.connected():
                            print("BTN: ", btn.text)
                            if player == 0:
                                if not game.p1_moved:
                                    comm.send(Event(type=Event.EventType.PLAY, message=btn.text))
                            else:
                                if not game.p2_moved:
                                    comm.send(Event(type=Event.EventType.PLAY, message=btn.text))
        redraw_window(win, game if isinstance(game, Game) else None, player, invitation=invitation)
        pygame.time.delay(500)
        pygame.display.update()


def menu_screen():
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        win.fill((128, 128, 128))
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Click to Play!", 1, (255, 0, 0))
        win.blit(text, (100, 200))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False

    main()


while True:
    menu_screen()
