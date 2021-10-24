
import pygame
import random

pygame.init()
clock = pygame.time.Clock()

# setting the display
displayWidth = 1024
displayHeight = 768
gameDisplay = pygame.display.set_mode((displayWidth,displayHeight))
pygame.display.set_caption('Go Time Geese')

# setting fonts and colours
largeFont = pygame.font.SysFont("timesnewromanttf",115)
smallFont = pygame.font.SysFont("timesnewromanttf",40)
black = (0, 0, 0)
white = (255, 255, 255)
red = (200, 0, 0)
green = (0, 200, 0)
brightRed = (255, 0, 0)
brightGreen = (0, 255, 0)

# creating white background
background = pygame.Surface(gameDisplay.get_size())
background.fill(white)

def text_box(text, font, colour):
   textSurf = font.render(text, True, colour)
   return textSurf, textSurf.get_rect()


def load_image(imagename, sizex, sizey):
    image = pygame.image.load(imagename)
    image = pygame.transform.scale(image, (sizex, sizey))
    return image


def button(msg,x,y,w,h,ic,ac,action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(gameDisplay, ac,(x,y,w,h))
        if click[0] == 1 and action != None:
            # pygame.mixer.music.load('sounds/click.wav')
            # pygame.mixer.music.play(0)
            action()
    else:
        pygame.draw.rect(gameDisplay, ic,(x,y,w,h))
    textSurf, textRect = text_box(msg, smallFont, black)
    textRect.center = (x+w/2, y+h/2)
    gameDisplay.blit(textSurf, textRect)


def quitgame():
    pygame.quit()
    quit()

# game intro screen with title and "start" and "quit" buttons
def game_intro():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gameDisplay.blit(background, (0, 0))
        TextSurf, TextRect = text_box("Go Time Geese", largeFont, black)
        TextRect.center = (displayWidth/2, displayHeight/3)
        gameDisplay.blit(TextSurf, TextRect)

        button("Start",220,420,200,100,green,brightGreen,start_game)
        button("Quit",620,420,200,100,red,brightRed,quitgame)

        pygame.display.update()
        clock.tick(15)

# start_game() helper function - ensures that goose is within display boundaries
def check_boundaries(x, y, gooseWidth, gooseHeight):
    # going past right
    if x > displayWidth - gooseWidth:
        x = displayWidth - gooseWidth

    # going past left
    if x < 0:
        x = 0

    # going past bottom
    if y > displayHeight - gooseHeight:
        y = displayHeight - gooseHeight

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

    gooseWidth = 120
    gooseHeight = 200
    gooseImg = load_image('goose.png', gooseWidth, gooseHeight)

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
            y_change = -speed

        elif player_1_action == 2:
            x_change = speed

        elif player_1_action == 3:
            y_change = speed

        elif player_1_action == 4:
            x_change = -speed

        print(player_1_action)
        # update goose position
        x += x_change
        y += y_change
        x, y = check_boundaries(x, y, gooseWidth, gooseHeight)
        gameDisplay.blit(gooseImg, (x,y))

        pygame.display.update()
        clock.tick(60)


game_intro()
quitgame()