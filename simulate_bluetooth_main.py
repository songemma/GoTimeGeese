
import bluetooth_utils
import collections
import pygame
import math


TRAIL_LEN = 5
GRID_ROWS = 30
GRID_COLS = 30
GRID_CELL_DIM = 30
FPS = 10

# Declare these here as global variables so that we can access them
# from within the Player class.
game_grid: list
player_points: list


class Player:
    def __init__(self, player_index: int):
        self._player_index = player_index
        self._row, self._col = Player._get_home_cell(player_index)
        self._x = self._col * GRID_CELL_DIM
        self._y = self._row * GRID_CELL_DIM
        self._trail = collections.deque(maxlen=TRAIL_LEN)

    def get_x(self) -> float:
        return self._x

    def get_y(self) -> float:
        return self._y

    def get_row(self) -> int:
        return self._row

    def get_col(self) -> int:
        return self._col

    def get_trail(self) -> iter:
        return iter(self._trail)

    def move(self, dx: float, dy: float):
        pos_changed = False
        old_row = self._col
        old_col = self._row
        # Execute the change dx.
        if dx != 0:
            self._x += dx
            self._x = max(self._x, 0)
            self._x = min(self._x, (GRID_COLS - 1) * GRID_CELL_DIM)
            new_col = math.floor(self._x / GRID_CELL_DIM)
            if self._col != new_col:
                self._col = new_col
                pos_changed = True
        # Execute the change dy.
        if dy != 0:
            self._y += dy
            self._y = max(self._y, 0)
            self._y = min(self._y, (GRID_ROWS - 1) * GRID_CELL_DIM)
            new_row = math.floor(self._y / GRID_CELL_DIM)
            if self._row != new_row:
                self._row = new_row
                pos_changed = True
        # If needed, update the trail, grid, etc.
        if pos_changed:
            prev_player = game_grid[self._row][self._col]
            if prev_player != -1:
                player_points[prev_player] -= 1
            game_grid[self._row][self._col] = self._player_index
            player_points[self._player_index] += 1
            self._trail.append((old_row, old_col))

    def reset(self):
        # Clear the trail. Reset the points.
        self._trail.clear()
        player_points[self._player_index] = 0
        # Clear every cell previously owned by this player.
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                if game_grid[row][col] == self._player_index:
                    game_grid[row][col] = -1
        # Reset coordinates.
        self._row, self._col = Player._get_home_cell(self._player_index)
        self._x = self._col * GRID_CELL_DIM
        self._y = self._row * GRID_CELL_DIM

    @staticmethod
    def _get_home_cell(player_index):
        if player_index == 0:
            return 0, 0
        elif player_index == 1:
            return GRID_ROWS - 1, GRID_COLS - 1
        elif player_index == 2:
            return 0, GRID_COLS - 1
        elif player_index == 3:
            return GRID_ROWS - 1, 0


def game_start() -> int:
    """Helper function for asking the user for the number of players,
    starting bluetooth_utils, waiting for all players to connect, etc.
    Returns the number of players."""

    # Ask the user for the number of players.
    while True:
        user_in = input("Number of players? ")
        if user_in.isnumeric():
            num_players = int(user_in)
            if 2 <= num_players <= 4:
                break
        print("Please enter a number between 2 and 4.")

    # Start bluetooth_utils and wait for everybody to connect.
    bluetooth_utils.start(num_players)
    prev_connected = -1
    while True:
        new_connected = bluetooth_utils.number_of_devices()
        if prev_connected != new_connected:
            prev_connected = new_connected
            print(f"\rConnected: {new_connected}/{num_players}       ", end='')
        if new_connected == num_players:
            break
    print()

    # Un-pause the game in case somebody accidentally touched the pause
    # button on their controller.
    bluetooth_utils.clear_paused_status()

    print("Here we go!")
    return num_players


def game_stop():
    bluetooth_utils.stop()
    pygame.quit()
    print("Thank you for playing!")
    quit()


def main():
    global game_grid, player_points

    num_players = game_start()

    player_points = [0 for _ in range(num_players)]
    players = [Player(index) for index in range(num_players)]
    game_grid = [[-1 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

    # Initialize grid corners with player_num.
    for player_num in range(num_players):
        player = players[player_num]
        game_grid[player.get_row()][player.get_col()] = player_num

    # Start Pygame.
    pygame.init()

    # Set up colours.
    black = (0, 0, 0)
    white = (255, 255, 255)
    player0red = (255, 0, 0) # Player0's territory.
    player0darkRed = (139, 0, 0) # Player0's current position.
    player0Trail = (233,150,122) # Player0's trail.
    player1yellow = (255, 255, 0)
    player1darkYellow = (102,102,0)
    player1Trail = (240,230,140)
    player2Blue = (0, 0, 255)
    player2darkBlue = (25, 25, 112)
    player2Trail = (173, 216, 230)
    player3Green = (0, 255, 0)
    player3darkGreen = (0, 100, 0)
    player3Trail = (173,255,47)

    # player_colours[player_num][x]
    # where x is one of the following:
    # - 0 for territory,
    # - 1 for current position,
    # - 2 for trail
    player_colours = [
        (player0red, player0darkRed, player0Trail),
        (player1yellow, player1darkYellow, player1Trail),
        (player2Blue, player2darkBlue, player2Trail),
        (player3Green, player3darkGreen, player3Trail)
    ]

    windowWidth = GRID_CELL_DIM * GRID_COLS
    windowHeight = GRID_CELL_DIM * GRID_ROWS
    windowSize = [windowWidth, windowHeight]
    screen = pygame.display.set_mode(windowSize)

    pygame.display.set_caption("Go Time Geese")
    clock = pygame.time.Clock()
    game_time = 5 # Number of minutes per round.
    current_time = pygame.time.get_ticks()


    # Game loop with time condition.
    while current_time < game_time * 60 * 1000:
        # Update current_time.
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_stop()

        for player_num in range(num_players):
            player_dir = bluetooth_utils.get_direction(player_num)
            player_obj = players[player_num]

            if player_dir == bluetooth_utils.DIR_LEFT:
                x_change = -GRID_CELL_DIM
                y_change = 0

            elif player_dir == bluetooth_utils.DIR_RIGHT:
                x_change = GRID_CELL_DIM
                y_change = 0

            elif player_dir == bluetooth_utils.DIR_UP:
                y_change = -GRID_CELL_DIM
                x_change = 0

            elif player_dir == bluetooth_utils.DIR_DOWN:
                y_change = GRID_CELL_DIM
                x_change = 0

            elif player_dir == bluetooth_utils.DIR_NONE:
                x_change = 0
                y_change = 0

            else:
                x_change = 0
                y_change = 0
                print("Error in player_dir")

            # Update player position.
            player_obj.move(x_change, y_change)

        # TODO: Emre implements collision detection

        screen.fill(black)

        # Draw the grid's territories.
        for row in range(GRID_ROWS):
            for column in range(GRID_COLS):
                color = white
                # If the square is claimed, draw it with the
                # colour of whoever most recently claimed it.
                # Otherwise, draw white (it is unclaimed territory).
                if game_grid[row][column] != -1:
                    color = player_colours[game_grid[row][column]][0]
                pygame.draw.rect(screen,
                                 color,
                                 [GRID_CELL_DIM * column,
                                  GRID_CELL_DIM * row,
                                  GRID_CELL_DIM,
                                  GRID_CELL_DIM]
                                 )

        # Draw the players' current positions and trails.
        for player_num in range(num_players):
            player_obj = players[player_num]

            # Draw player_obj's trail.
            for (trail_row, trail_col) in player_obj.get_trail():
                pygame.draw.rect(screen,
                                 player_colours[player_num][2],
                                 [GRID_CELL_DIM * trail_row,
                                  GRID_CELL_DIM * trail_col,
                                  GRID_CELL_DIM,
                                  GRID_CELL_DIM]
                                 )
            # Draw player_obj's current position.
            pygame.draw.rect(screen,
                             player_colours[player_num][1],
                             [player_obj.get_x(),
                              player_obj.get_y(),
                              GRID_CELL_DIM,
                              GRID_CELL_DIM]
                             )
        pygame.display.update()
        clock.tick(FPS)

        if bluetooth_utils.get_paused():
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_stop()

                # Draw pause screen.
                screen.fill(white)
                text_surface = pygame.font.SysFont("timesnewromanttf", 115).render("Paused", True, black)
                text_rectangle = text_surface.get_rect()
                text_rectangle.center = (windowWidth / 2, windowHeight / 3)
                screen.blit(text_surface, text_rectangle)

                pygame.display.update()
                clock.tick(15)

            while bluetooth_utils.get_paused():
                pass

    # TODO: Display who won.

    game_stop()


main()

