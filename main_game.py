import bluetooth_utils
import collections
import math
import pygame


# Game constants
TRAIL_LEN = 5
GRID_ROWS = 30
GRID_COLS = 30

# Size/Dimension constants
PAUSED_TEXT_SIZE = 100
GRID_CELL_DIM = 10
SCORE_BOARD_SIZE = 30
SCORE_BOARD_SEPARATOR = 1
SCORE_TEXT_SIZE = 22
SCORE_TEXT_OFFSET_X = 8
SCORE_TEXT_OFFSET_Y = 9
SCORE_TEXT_DX = 76

# Time constants
FPS = 20
PLAYER_SPEED = 2.5

# Generic colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Player 0 colors
PLAYER_0_TERRITORY = (255, 0, 0)
PLAYER_0_SELF = (139, 0, 0)
PLAYER_0_TRAIL = (233, 150, 122)
# Player 1 colors
PLAYER_1_TERRITORY = (255, 255, 0)
PLAYER_1_SELF = (102, 102, 0)
PLAYER_1_TRAIL = (240, 230, 140)
# Player 2 colors
PLAYER_2_TERRITORY = (0, 0, 255)
PLAYER_2_SELF = (25, 25, 112)
PLAYER_2_TRAIL = (173, 216, 230)
# Player 3 colors
PLAYER_3_TERRITORY = (0, 255, 0)
PLAYER_3_SELF = (0, 100, 0)
PLAYER_3_TRAIL = (173, 255, 47)


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

    def get_row(self) -> int:
        return self._row

    def get_col(self) -> int:
        return self._col

    def get_trail(self) -> iter:
        return iter(self._trail)

    def move(self, dx: float, dy: float):
        pos_changed = False
        old_row = self._row
        old_col = self._col
        # Execute the change dx.
        if dx != 0:
            self._x += dx
            self._x = max(self._x, 0)
            self._x = min(self._x, (GRID_COLS - 1) * GRID_CELL_DIM)
            new_col = math.floor(self._x / GRID_CELL_DIM)
            if self._col != new_col:
                self._col = new_col
                pos_changed = True
        else:
            self._x = (self._col + 0.5) * GRID_CELL_DIM
        # Execute the change dy.
        if dy != 0:
            self._y += dy
            self._y = max(self._y, 0)
            self._y = min(self._y, (GRID_ROWS - 1) * GRID_CELL_DIM)
            new_row = math.floor(self._y / GRID_CELL_DIM)
            if self._row != new_row:
                self._row = new_row
                pos_changed = True
        else:
            self._y = (self._row + 0.5) * GRID_CELL_DIM
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


def main():
    global game_grid, player_points

    num_players = game_start()

    game_grid = [[-1 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    player_points = [0 for _ in range(num_players)]
    players = [Player(index) for index in range(num_players)]

    # Needed for collision detection logic. Allocated once and reused to
    # help with game performance.
    player_bools = [False for _ in range(num_players)]

    pygame.init()

    # player_colors[player_index][x]
    # x=0 -> Territory Color
    # x=1 -> Current Position Color
    # x=2 -> Trail Color
    player_colors = [
        (PLAYER_0_TERRITORY, PLAYER_0_SELF, PLAYER_0_TRAIL),
        (PLAYER_1_TERRITORY, PLAYER_1_SELF, PLAYER_1_TRAIL),
        (PLAYER_2_TERRITORY, PLAYER_2_SELF, PLAYER_2_TRAIL),
        (PLAYER_3_TERRITORY, PLAYER_3_SELF, PLAYER_3_TRAIL)
    ]

    # Used in drawing the players' scores. Instantiated once and reused to
    # help with game performance.
    score_font = pygame.font.SysFont("timesnewromanttf", SCORE_TEXT_SIZE)

    window_width = GRID_CELL_DIM * GRID_COLS
    window_height = GRID_CELL_DIM * GRID_ROWS + SCORE_BOARD_SIZE
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Go Time Geese")

    clock = pygame.time.Clock()
    is_paused = False

    while True:
        # Handle quit event.
        quit_game = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game = True
                break
        if quit_game:
            break

        if bluetooth_utils.get_paused():
            # If the game has just been paused, draw the "Paused" text.
            if not is_paused:
                is_paused = True
                screen.fill(WHITE)
                text_surface = pygame.font.SysFont("timesnewromanttf", PAUSED_TEXT_SIZE).render("Paused", True, BLACK)
                text_rectangle = text_surface.get_rect()
                text_rectangle.center = (window_width // 2, window_height // 3)
                screen.blit(text_surface, text_rectangle)
                pygame.display.update()
            # Before rewinding the game loop, don't forget to tick the clock.
            clock.tick(FPS)
            continue
        else:
            is_paused = False

        # Handle directional input to move players.
        for player_index in range(num_players):
            player_dir = bluetooth_utils.get_direction(player_index)
            dx, dy = 0, 0
            if player_dir == bluetooth_utils.DIR_LEFT:
                dx = -PLAYER_SPEED
            elif player_dir == bluetooth_utils.DIR_RIGHT:
                dx = PLAYER_SPEED
            elif player_dir == bluetooth_utils.DIR_UP:
                dy = -PLAYER_SPEED
            elif player_dir == bluetooth_utils.DIR_DOWN:
                dy = PLAYER_SPEED
            players[player_index].move(dx, dy)

        # Handle collision detection between players. Implements the algorithm
        # discussed in meeting 5.
        for player_index in range(num_players):
            player_bools[player_index] = False
        # Consider all possible pairs of players.
        for p1_index in range(num_players - 1):
            p1 = players[p1_index]
            for p2_index in range(p1_index + 1, num_players):
                p2 = players[p2_index]
                # Case 1: Head-on collision
                if p1.get_row() == p2.get_row() and p1.get_col() == p2.get_col():
                    player_bools[p1_index] = True
                    player_bools[p2_index] = True
                # Case 2: p1 is on the trail of p2
                elif (p1.get_row(), p1.get_col()) in p2.get_trail():
                    player_bools[p2_index] = True
                # Case 3: p2 is on the trail of p1
                elif (p2.get_row(), p2.get_col()) in p1.get_trail():
                    player_bools[p1_index] = True
        # Now that we enforced the rules fairly on all players, we can start
        # re-spawning them as needed.
        for player_index in range(num_players):
            if player_bools[player_index]:
                players[player_index].reset()

        # Draw the game screen.
        screen.fill(WHITE)
        # Step 1: Draw the grid with the territories.
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                p = game_grid[row][col]
                if p != -1:
                    pygame.draw.rect(screen, player_colors[p][0], (GRID_CELL_DIM * col, GRID_CELL_DIM * row,
                                                                   GRID_CELL_DIM, GRID_CELL_DIM))
        # Step 2: Draw the players along with their trails.
        for player_index in range(num_players):
            player = players[player_index]
            for (row, col) in player.get_trail():
                pygame.draw.rect(screen, player_colors[player_index][2],
                                 (GRID_CELL_DIM * col, GRID_CELL_DIM * row, GRID_CELL_DIM, GRID_CELL_DIM))
            pygame.draw.rect(screen, player_colors[player_index][1],
                             (GRID_CELL_DIM * player.get_col(), GRID_CELL_DIM * player.get_row(),
                              GRID_CELL_DIM, GRID_CELL_DIM))
        # Step 3: Draw the scoreboard.
        pygame.draw.rect(screen, BLACK, (0, GRID_CELL_DIM * GRID_ROWS, window_width, SCORE_BOARD_SEPARATOR))
        for player_index in range(num_players):
            score_text = f"P{player_index + 1}: {player_points[player_index]}"
            text_surface = score_font.render(score_text, True, player_colors[player_index][1])
            text_rect = text_surface.get_rect()
            text_rect.left = SCORE_TEXT_OFFSET_X + player_index * SCORE_TEXT_DX
            text_rect.top = GRID_CELL_DIM * GRID_ROWS + SCORE_TEXT_OFFSET_Y
            screen.blit(text_surface, text_rect)

        pygame.display.update()
        clock.tick(FPS)

    bluetooth_utils.stop()
    pygame.quit()
    print("Thank you for playing!")


main()
