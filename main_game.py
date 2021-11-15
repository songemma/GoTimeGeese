import bluetooth_utils
import collections
import math


TRAIL_LEN = 5
GRID_ROWS = 30
GRID_COLS = 30
GRID_CELL_DIM = 10

# Declare these here as global variables so that we can access them
# from within the Player class.
game_grid: list
player_points: list


class Player:
    def __init__(self, player_index: int):
        self._player_index = player_index
        self._row, self._col = Player._get_home_cell(player_index)
        self._x = (self._col + 0.5) * GRID_CELL_DIM
        self._y = (self._row + 0.5) * GRID_CELL_DIM
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
            self._trail.append((self._row, self._col))

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
        self._x = (self._col + 0.5) * GRID_CELL_DIM
        self._y = (self._row + 0.5) * GRID_CELL_DIM

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
    print("Thank you for playing!")


def main():
    global game_grid, player_points

    num_players = game_start()
    game_grid = [[-1 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    player_points = [0 for _ in range(num_players)]
    players = [Player(index) for index in range(num_players)]

    # TODO: Initialize pygame stuff.

    while True:     # TODO: Update this condition with time limit.
        # TODO: Emma

        # TODO: Molly

        if bluetooth_utils.get_paused():
            # TODO: Blit "Paused" on the screen here.
            while bluetooth_utils.get_paused():
                pass

    # TODO: Display who won.

    game_stop()


main()
