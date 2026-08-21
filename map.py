import pygame as py
import random as r
ROWS=12
COLLUMS=12
TILE=48
WIDTH=COLLUMS*TILE
HEIGHT=ROWS*TILE
LOGO_CELLS=[(5,5),(5,6),(6,5),(6,6)]
py.init()
screen=py.display.set_mode((WIDTH,HEIGHT))
forest=py.image.load("images/forest.png").convert_alpha()
forest=py.transform.scale(forest,(TILE,TILE))
fields=py.image.load("images/fields.png").convert_alpha()
fields=py.transform.scale(fields,(TILE,TILE))
rocks=py.image.load("images/Rocks.png").convert_alpha()
rocks=py.transform.scale(rocks,(TILE,TILE))
water=py.image.load("images/water.png").convert_alpha()
water=py.transform.scale(water,(TILE,TILE))
logo=py.image.load("images/logo-ptit.png").convert_alpha()
logo=py.transform.scale(logo,(TILE,TILE))
lr,lc=r.choice(LOGO_CELLS)
running=True
game_map=[[r.choice([forest,fields,rocks,water]) for col in range(COLLUMS)] for row in range(ROWS)]
game_map[lr][lc]=logo
while running:
    for event in py.event.get():
        if event.type==py.QUIT:
            running=False
    for row in range(ROWS):
        for col in range(COLLUMS):
            x=row*TILE
            y=col*TILE
            screen.blit(game_map[row][col],(x,y))
    py.display.flip()
py.quit()