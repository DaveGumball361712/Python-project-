import pygame as py
import random as r

ROWS=12
COLLUMS=12
TILE=48
WIDTH=COLLUMS*TILE
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
Building_Image_Data={
    "tower":"tower",
    "village":"village",
    "port_village":"port_village",
    "mining_village":"mining_village",
    "treetop_village":"treetop_village",
}
BUILDING_RULES={
    "village":{"on":["fields"],"next_to":{}},
    "port_village":{"on":["fields"],"next_to":{"water":1}},
    "mining_village":{"on":["fields"],"next_to":{"rocks":2}},
    "magical_village":{"on":["fields"],"next_to":{"mushroom":1}},
    "magical_port_village":{"on":["fields"],"next_to":{"mushroom":1,"water":1}},
    "treetop_village":{"on":["forest"],"next_to":{"forest":4},"diagonal":False},
    "Tower_of_light":{"on":["fields"],"next_to":{},"needs":["magical village"]}
}

def load_images():
    def load(name):
        img=py.image.load("images/"+name).convert_alpha()
        return py.transform.scale(img,(TILE,TILE))
    return {
        "forest":load("forest.png"),
        "fields":load("fields.png"),
        "rocks":load("Rocks.png"),
        "water":load("water.png"),
        "logo":load("logo-ptit.png"),
        "mushroom":load("mushroom.png"),
        "tower_of_light":load("tower.png"),
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
        hang=[]
        for col in range(COLLUMS):
            type="logo" if (row,col)==(lr,lc) else bag[i]
            if type != "logo":
                i+=1
            hang.append({
                "type":type,
                "building":None,
                "level":0,
                "darkness":False,
            })
        game_map.append(hang)
    return game_map

def draw_map(screen, game_map, images):
    for row in range(ROWS):
        for col in range(COLLUMS):
            tile=game_map[row][col]
            tile_type=IMAGE_DATA[tile["type"]]
            screen.blit(images[tile_type],(col*TILE,row*TILE))

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
    while True:
        for event in py.event.get():
            if event.type==py.QUIT:
                return "QUIT"
        draw_map(screen, game_map,images)
        py.display.flip()

if __name__=="__main__":
    py.init()
    screen=py.display.set_mode((WIDTH,HEIGHT))
    run_game(screen)
    py.quit()