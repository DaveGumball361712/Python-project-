import pygame as py
import random as r

ROWS=12
COLLUMS=12
TILE=48
WIDTH=COLLUMS*TILE
HEIGHT=ROWS*TILE
LOGO_CELLS=[(5,5),(5,6),(6,5),(6,6)]


def load_images():
    def load(name):
        img=py.image.load("images/"+name).convert_alpha()
        return py.transform.scale(img,(TILE,TILE))
    return {
        "forest": load("forest.png"),
        "fields": load("fields.png"),
        "rocks":  load("Rocks.png"),
        "water":  load("water.png"),
        "logo":   load("logo-ptit.png"),
    }


def generate_map(images):
    lr,lc=r.choice(LOGO_CELLS)
    n_forest=r.randint(37,40)
    n_rocks=r.randint(14,15)
    n_water=r.randint(15,18)
    n_fields=144-1-n_forest-n_rocks-n_water
    bag=([images["forest"]]*n_forest+[images["rocks"]]*n_rocks+[images["water"]]*n_water+[images["fields"]]*n_fields)
    r.shuffle(bag)
    game_map=[]
    i=0
    for row in range(ROWS):
        hang=[]
        for col in range(COLLUMS):
            if (row,col)==(lr,lc):
                hang.append(images["logo"])
            else:
                hang.append(bag[i]); i+=1
        game_map.append(hang)
    return game_map


def draw_map(screen, game_map):
    for row in range(ROWS):
        for col in range(COLLUMS):
            screen.blit(game_map[row][col],(col*TILE,row*TILE))


def run_game(screen):
    images=load_images()
    game_map=generate_map(images)
    while True:
        for event in py.event.get():
            if event.type==py.QUIT:
                return "QUIT"
        draw_map(screen, game_map)
        py.display.flip()


if __name__=="__main__":
    py.init()
    screen=py.display.set_mode((WIDTH,HEIGHT))
    run_game(screen)
    py.quit()