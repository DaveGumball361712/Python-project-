`import pygame

ROWS = 12
COLLUMS = 12
TILE = 48
WIDTH = COLLUMS * TILE
HEIGHT = ROWS * TILE

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for row in range(ROWS):
        for col in range(COLLUMS):
            x = col * TILE
            y = row * TILE
            rect = pygame.Rect(x, y, TILE, TILE)
            pygame.draw.rect(screen, (95, 140, 100), rect)          
            pygame.draw.rect(screen, (25, 25, 35), rect, 1)         

    pygame.display.flip()

pygame.quit()