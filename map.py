import pygame as py
import random as r
from menu import Button

ROWS=12
COLLUMS=12
TILE=48

MAP_WIDTH=COLLUMS*TILE
UI_WIDTH = 250 
WIDTH = MAP_WIDTH + UI_WIDTH
HEIGHT=ROWS*TILE
LOGO_CELLS=[(5,5),(5,6),(6,5),(6,6)]
IMAGE_DATA={
    "forest":"forest",
    "fields":"fields",
    "rocks":"rocks",
    "water":"water",
    "logo":"logo",
    "mushroom":"mushroom",
}
BUILDING_IMAGE_DATA={
    "tower":"tower",
    "village":"village",
    "port_village":"port_village",
    "mining_village":"mining_village",
    "treetop_village":"treetop_village",
    "magical_port_village2":"magical_port_village2",
}
BUILDING_RULES={
    "village":{"on":["fields"],"next_to":{}},
    "port_village":{"on":["fields"],"next_to":{"water":1}},
    "mining_village":{"on":["fields"],"next_to":{"rocks":2}},
    "magical_village":{"on":["fields"],"next_to":{"mushroom":1}},
    "magical_port_village":{"on":["fields"],"next_to":{"mushroom":1,"water":1}},
    "treetop_village":{"on":["forest"],"next_to":{"forest":4},"diagonal":False},
    "tower_of_light":{"on":["fields"],"next_to":{},"needs":["magical_village"]}
}

BUILD_PRIORITY = [
    "treetop_village",        
    "magical_port_village",   
    "magical_village",        
    "port_village",           
    "mining_village",         
    "village",                
]

def load_images():
    def load(name):
        img=py.image.load("images/"+name).convert_alpha()
        return py.transform.scale(img,(TILE,TILE))
    return {
        "forest":load("forest.png"),
        "forest2":load("forest2.png"),
        "forest3":load("forest3.png"),
        "forest4":load("forest4.png"),
        "fields":load("fields.png"),
        "rocks":load("rocks.png"),
        "rocks2":load("rocks2.png"),
        "rocks3":load("rocks3.png"),
        "water":load("water.png"),
        "logo":load("logo-ptit.png"),
        "mushroom":load("mushroom.png"),
        "tower_of_light":load("tower.png"),
        "tower_of_light2":load("tower2.png"),
        "village":load("village.png"),
        "village2":load("village2.png"),
        "treetop_village":load("treetop_village.png"),
        "treetop_village2":load("treetop_village2.png"),
        "mining_village":load("mining_village.png"),
        "mining_village2":load("mining_village2.png"),
        "port_village":load("port_village.png"),
        "port_village2":load("port_village2.png"),
        "magical_port_village2":load("magical_port_village2.png"),
    }

def generate_map():
    lr,lc=r.choice(LOGO_CELLS)
    n_forest=r.randint(37,40)
    n_rocks=r.randint(14,15)
    n_water=r.randint(15,18)
    n_mushroom=4
    n_fields=144-1-n_forest-n_rocks-n_water-n_mushroom
    bag=(["forest"]*n_forest+["rocks"]*n_rocks+["water"]*n_water+["fields"]*n_fields+["mushroom"]*n_mushroom)
    r.shuffle(bag)
    game_map=[]
    i=0
    for row in range(ROWS):
        map=[]
        for col in range(COLLUMS):
            type="logo" if (row,col)==(lr,lc) else bag[i]
            if type != "logo":
                i+=1
            map.append({
                "type":type,
                "building":None,
                "level":0,
                "darkness":False,
            })
        game_map.append(map)
    return game_map

def draw_map(screen, game_map, images):
    for row in range(ROWS):
        for col in range(COLLUMS):
            tile=game_map[row][col]
            screen.blit(images[IMAGE_DATA[tile["type"]]],(col*TILE,row*TILE))
            b=tile["building"]
            if b is not None:
                img=BUILDING_IMAGE_DATA.get(b)
                if img is not None:
                    screen.blit(images[img],(col*TILE,row*TILE))

def neighbor_tile(game_map,row,col,diagonal=True):
    direction=[(-1,0),(1,0),(0,1),(0,-1)]
    if diagonal:
        direction+=[(1,1),(-1,-1),(1,-1),(-1,1)]
    result=[]
    for dr,dc in direction:
        nr,nc=row+dr,col+dc
        if 0<=nr<ROWS and 0<=nc<COLLUMS:
            result.append(game_map[nr][nc])
    return result

def count_neighbor_tile(game_map,row,col,diagonal=True):
    count={}
    for on in neighbor_tile(game_map,row,col,diagonal):
        count[on["type"]]=count.get(on["type"],0)+1
    return count

def placement(game_map,row,col,name):
    on=game_map[row][col]
    rule=BUILDING_RULES[name]
    diagonal=rule.get("diagonal",True)
    if on["type"]not in rule["on"]:
        return False
    if on["building"] is not None or on["darkness"]:
        return(False)
    count=count_neighbor_tile(game_map,row,col,diagonal)
    for type, need in rule["next_to"].items():
        if count.get(type,0)<need:
            return False
    for b in rule.get("needs",[]):
        has=0
        for o in neighbor_tile(game_map,row,col,diagonal=True):
            if o["building"]==b:
                has+=1
        if has < 1:
            return False
    return True

def building_check(game_map):
    for row in range(ROWS):
        for col in range(COLLUMS):
            if placement(game_map, row, col, "treetop_village"):
                return True
    return False

def building_for_tile(game_map, row, col):
    for name in BUILD_PRIORITY:
        if placement(game_map, row, col, name):
            return name          
    return None                 

def generate_map_new():
    for _ in range(1000):                
        game_map = generate_map()
        if building_check(game_map):
            return game_map               
    return game_map                      

def build(game_map, row, col, name):
    if not placement(game_map, row, col, name):
        return False
    tile = game_map[row][col]
    tile["building"] = name
    tile["level"] = 1
    return True

def run_game(screen):
    images=load_images()
    game_map=generate_map_new()
    is_playing = True
    def action_quit():
        nonlocal is_playing
        is_playing = False
    btn_build_village = Button(x=MAP_WIDTH + 125, y=450, width=160, height=50, text="Build")

    btn_quit = Button(x=MAP_WIDTH + 125, y=520, width=160, height=50, text="Quit", action=action_quit)

    while is_playing:
        for event in py.event.get():
            if event.type==py.QUIT:
                return "QUIT"
            # event listener
            btn_build_village.handle_event(event)
            btn_quit.handle_event(event)

            if event.type==py.MOUSEBUTTONDOWN:
                col=event.pos[0]//TILE
                row=event.pos[1]//TILE
                if 0<=row<ROWS and 0<=col<COLLUMS:
                    name=building_for_tile(game_map,row,col)
                    if name is not None:
                        build(game_map,row,col,name)
        draw_map(screen, game_map,images)

        # create background for menu in game
        py.draw.rect(screen, (0,0,0), (MAP_WIDTH, 0, UI_WIDTH, HEIGHT))

        # create button
        btn_build_village.update()
        screen.blit(btn_build_village.image, btn_build_village.rect)

        btn_quit.update()
        screen.blit(btn_quit.image, btn_quit.rect)

        py.display.flip()
    return "QUIT"

if __name__=="__main__":
    py.init()
    screen=py.display.set_mode((WIDTH,HEIGHT))
    run_game(screen)
    py.quit()