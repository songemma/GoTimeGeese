import pygame

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
darkRed = (139, 0, 0)

length = 20
margin = 5

gameBoard = []

for row in range(10):
    gameBoard.append([])
    for column in range(10):
        gameBoard[row].append(0)

gameBoard[0][0] = 1

pygame.init()

windowWidth = 255
windowHeight = 255
windowSize = [windowWidth, windowHeight]
screen = pygame.display.set_mode(windowSize)

pygame.display.set_caption("test thingy")

exitGame = False

clock = pygame.time.Clock()

x1 = margin
y1 = margin
x1_change = 0
y1_change = 0

move = length + margin

while not exitGame:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exitGame = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                x1_change = -move
                y1_change = 0
            elif event.key == pygame.K_RIGHT:
                x1_change = move
                y1_change = 0
            elif event.key == pygame.K_UP:
                y1_change = -move
                x1_change = 0
            elif event.key == pygame.K_DOWN:
                y1_change = move
                x1_change = 0
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                x1_change = 0
                y1_change = 0
            elif event.key == pygame.K_RIGHT:
                x1_change = 0
                y1_change = 0
            elif event.key == pygame.K_UP:
                y1_change = -0
                x1_change = 0
            elif event.key == pygame.K_DOWN:
                y1_change = 0
                x1_change = 0

        if windowWidth > x1 + x1_change > 0 and windowHeight > y1 + y1_change > 0:
            x1 += x1_change
            y1 += y1_change

        column = x1 // (length + margin)
        row = y1 // (length + margin)
        gameBoard[row][column] = -1

    screen.fill(black)

    for row in range(10):
        for column in range(10):
            color = white
            if gameBoard[row][column] == -1:
                color = red
            pygame.draw.rect(screen,
                             color,
                             [(margin + length) * column + margin,
                              (margin + length) * row + margin,
                              length,
                              length])

    pygame.draw.rect(screen, darkRed, [x1, y1, length, length])
    pygame.display.update()
    clock.tick(60)

pygame.quit()
