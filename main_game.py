
import pygame
import random
import pygame_menu
#import bluetooth_utils

pygame.init()
clock = pygame.time.Clock()

# setting the display
displayWidth = 1024
displayHeight = 768
gameDisplay = pygame.display.set_mode((displayWidth, displayHeight))
pygame.display.set_caption('Go Time Geese')

# setting fonts and colours
largeFont = pygame.font.SysFont("timesnewromanttf", 115)
mediumFont = pygame.font.SysFont("timesnewromanttf", 70)
smallFont = pygame.font.SysFont("timesnewromanttf", 40)
black = (0, 0, 0)
white = (255, 255, 255)
red = (200, 0, 0)
green = (0, 200, 0)
blue = (65,102,245)
brightRed = (255, 0, 0)
brightGreen = (0, 255, 0)
brightBlue = (69,177,232)
_players = 2 # default

# creating white background
background = pygame.Surface(gameDisplay.get_size())
background.fill(white)


def text_box(text, font, colour):
    text_surf = font.render(text, True, colour)
    return text_surf, text_surf.get_rect()


def load_image(imagename, sizex, sizey):
    image = pygame.image.load(imagename)
    image = pygame.transform.scale(image, (sizex, sizey))
    return image


def quitgame():
    pygame.quit()
    quit()


def set_num_players(value, num_players):
    global _players
    _players = num_players


def get_num_players():
    global _players
    return _players


# game intro screen with title and "start" and "quit" buttons
def main_menu():
    menu = pygame_menu.Menu('Go Time Geese', displayWidth, displayHeight,
                            theme=pygame_menu.themes.THEME_BLUE)
    menu.add.selector('Number of Players :', [('2', 2), ('3', 3), ('4', 4)],
                      onchange=set_num_players,
                      default=get_num_players() - 2)
    menu.add.button('Head to Waiting Room', waiting_room)
    menu.mainloop(gameDisplay)


def waiting_room():
    menu = pygame_menu.Menu('Waiting...', displayWidth, displayHeight,
                            theme=pygame_menu.themes.THEME_BLUE,
                            onclose=pygame_menu.events.RESET)

    num_players = get_num_players()
    # players_joined = bluetooth_utils.number_of_devices()
    # test with dummy values

    players_joined = 0

    players_label = menu.add.label(f"{players_joined}/{num_players}",
                                   align=pygame_menu.locals.ALIGN_CENTER,
                                   font_size=100,
                                   font_name=pygame_menu.font.FONT_PT_SERIF,
                                   font_color=black, padding=10)
    menu.add.label("players have joined",
                   align=pygame_menu.locals.ALIGN_CENTER,
                   font_size=50,
                   font_name=pygame_menu.font.FONT_PT_SERIF,
                   font_color=black, padding=10)

    while players_joined != num_players:
        # Application events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

        if menu.is_enabled():
            menu.draw(gameDisplay)
            menu.update(events)

        # Update surface
        pygame.display.flip()

        # Update players_joined
        players_joined += 1
        players_label.set_title(f"{players_joined}/{num_players}")
        # Wait for 1 second
        pygame.time.wait(1000)

    menu.add.button('Start Game', start_game)
    menu.mainloop(gameDisplay)


# start_game() helper function - ensures that goose is within display boundaries
def check_boundaries(x, y, goose_width, goose_height):
    # going past right
    if x > displayWidth - goose_width:
        x = displayWidth - goose_width

    # going past left
    if x < 0:
        x = 0

    # going past bottom
    if y > displayHeight - goose_height:
        y = displayHeight - goose_height

    # going past top
    if y < 0:
        y = 0

    return x, y


# main game is started - move the goose around the screen
def start_game():
    # goose position is (x, y) where (0,0) is the top left corner of the screen
    x = displayWidth * 0.43
    y = displayHeight * 0.38

    # change in position
    x_change = 0
    y_change = 0

    speed = 20

    goose_width = 120
    goose_height = 200
    goose_img = load_image('goose.png', goose_width, goose_height)

    while True:
        gameDisplay.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # dummy variable to simulate player's action
        player_1_action = random.randint(0, 4)

        # 0 is neutral state (no moving)
        # 1 is up, 2 is right, 3 is down, 4 is left
        #     1
        #  4     2
        #     3

        if player_1_action == 0:
            x_change = 0
            y_change = 0

        elif player_1_action == 1:
            x_change = 0
            y_change = -speed

        elif player_1_action == 2:
            x_change = speed
            y_change = 0

        elif player_1_action == 3:
            x_change = 0
            y_change = speed

        elif player_1_action == 4:
            x_change = -speed
            y_change = 0

        print(player_1_action)
        # update goose position
        x += x_change
        y += y_change
        x, y = check_boundaries(x, y, goose_width, goose_height)
        gameDisplay.blit(goose_img, (x, y))

        pygame.display.update()
        clock.tick(60)


main_menu()
quitgame()
