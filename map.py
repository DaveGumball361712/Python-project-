import pygame as py
import random as r
from menu import Button
from economy import EconomyManager
import sys, os

ROWS=12
COLLUMS=12
TILE=48

MAP_WIDTH=COLLUMS*TILE
UI_WIDTH = 250 
WIDTH = MAP_WIDTH + UI_WIDTH
HEIGHT=ROWS*TILE
LOGO_CELLS=[(5,5),(5,6),(6,5),(6,6)]

BUILDING_RULES={    #Luat xay dung cong trinh
    "village":{"on":["fields"],"next_to":{}},
    "port_village":{"on":["fields"],"next_to":{"water":1},"diagonal":False},
    "mining_village":{"on":["fields"],"next_to":{"rocks":2},"diagonal":False},
    "magical_village":{"on":["fields"],"next_to":{"mushroom":1},"diagonal":False},
    "magical_port_village":{"on":["fields"],"next_to":{"mushroom":1,"water":1},"diagonal":False},
    "treetop_village":{"on":["forest"],"next_to":{"forest":4},"diagonal":False},
    "tower_of_light":{"on":["fields"],"next_to":{},"needs":["magical_village","magical_port_village"],"diagonal":False},
}

ONE_TIME_BUILDING={   #Cac cong trinh chi xay duoc 1 lan
    "tower_of_light",
} 

UPGRADE={      #Nang cap
    "forest":"forest2","forest2":"forest3","forest3":"forest4",
    "rocks":"rocks2","rocks2":"rocks3",
    "mushroom":"mushroom2",
    "village":"village2",
    "mining_village":"mining_village2",
    "treetop_village":"treetop_village2",
    "port_village":"port_village2",
    "tower_of_light":"tower_of_light2",
    "magical_village":"magical_village2",
    "magical_port_village":"magical_port_village2",
    "logo": "the_stone",
}

BUILD_PRIORITY = [    #Thu tu uu tien xay dung
    "tower_of_light",
    "treetop_village",        
    "magical_port_village",   
    "magical_village",        
    "port_village",           
    "mining_village",         
    "village",                
]


def load_images():     #Ham load hinh anh
    def load(name):    #Ham nap ten anh
        img = py.image.load("images/" + name)
        return py.transform.scale(img,(TILE,TILE))     

    def load_icon(name):
        img = py.image.load("images/" + name).convert_alpha()
        return py.transform.scale(img, (25, 25))
    
    return {
        "icon_wood": load_icon("icon_wood.png"),
        "icon_stone": load_icon("icon_stone.png"),
        "icon_magic": load_icon("icon_magic.png"),
        "icon_tech": load_icon("icon_tech.png"),
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
        "mushroom2":load("mushroom2.png"),
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
        "magical_port_village":load("magical_port_village.png"),
        "magical_port_village2":load("magical_port_village2.png"),
        "magical_village":load("magical_village.png"),
        "magical_village2":load("magical_village2.png"),
        "the_stone": load("the_stone.png"),
    }

def grow_blob(occupied, size):
    empties = [(row,col) for row in range(ROWS) for col in range(COLLUMS) if (row,col) not in occupied]
    if not empties:
        return []
    seed = r.choice(empties)
    blob = [seed]; occupied.add(seed); frontier = [seed]
    while len(blob) < size and frontier:
        cell = r.choice(frontier)                     
        neighbors = [(cell[0]+dr,cell[1]+dc) for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]]
        neighbors = [(nr,nc) for (nr,nc) in neighbors
                if 0<=nr<ROWS and 0<=nc<COLLUMS and (nr,nc) not in occupied]
        if neighbors:
            next = r.choice(neighbors)                       
            blob.append(next); occupied.add(next); frontier.append(next)
        else:
            frontier.remove(cell)                     
    return blob

def generate_map():  
    lr,lc=r.choice(LOGO_CELLS)  
    n_forest=r.randint(37,40)   
    n_rocks=r.randint(14,15)    
    n_water=r.randint(27,33)    
    n_mushroom=4                
    n_fields=144-1-n_forest-n_rocks-n_water-n_mushroom     
    occupied = {(lr,lc)}                     
    water = []; remaining = n_water
    while remaining > 0:
        lake_size = min(remaining, r.randint(3,7))  
        blob = grow_blob(occupied, lake_size)
        water += blob; remaining -= len(blob)
    water = set(water)
    bag=(["forest"]*n_forest+["rocks"]*n_rocks+["fields"]*n_fields+["mushroom"]*n_mushroom)
    r.shuffle(bag)              
    game_map = []; i = 0
    for row in range(ROWS):
        hang = []
        for col in range(COLLUMS):
            if (row,col) == (lr,lc):     type = "logo"
            elif (row,col) in water:     type = "water"
            else:                        type = bag[i]; i += 1
            hang.append({"type":type,"building":None,"level":0,"darkness":False})
        game_map.append(hang)
    return game_map

def draw_map(screen, game_map, images):    #ham ve map
    for row in range(ROWS):
        for col in range(COLLUMS):
            tile = game_map[row][col]
            screen.blit(images[tile["type"]], (col*TILE, row*TILE))
            b = tile["building"]
            if b is not None and b in images:
                screen.blit(images[b], (col*TILE, row*TILE)) 

def neighbor_tile(game_map,row,col,diagonal=True):     #ham kiem tra o lan can
    direction=[(-1,0),(1,0),(0,1),(0,-1)]              
    if diagonal:
        direction+=[(1,1),(-1,-1),(1,-1),(-1,1)]       
    result=[]                                          
    for dr,dc in direction:                            
        nr,nc=row+dr,col+dc                            
        if 0<=nr<ROWS and 0<=nc<COLLUMS:               
            result.append(game_map[nr][nc])            
    return result

def count_neighbor_tile(game_map,row,col,diagonal=True):        #ham dem cac o lan can
    count={}
    for on in neighbor_tile(game_map,row,col,diagonal):         
        name=on["type"].rstrip("0123456789")                    
        count[name]=count.get(name,0)+1                         
    return count

def building_exists(game_map, name):                  #ham kiem tra building da ton tai chua
    for row in game_map:
        for tile in row:
            if tile["building"] is not None and tile["building"].rstrip("0123456789")==name:    
                return True
    return False          

def placement(game_map,row,col,name):           #ham kiem tra dieu kien xay
    on=game_map[row][col]                       
    rule=BUILDING_RULES[name]                   
    if name in ONE_TIME_BUILDING and building_exists(game_map,name):    
        return False        
    diagonal=rule.get("diagonal",True)     
    if on["type"]not in rule["on"]:    
        return False
    if on["building"] is not None or on["darkness"]:        
        return(False)
    count=count_neighbor_tile(game_map,row,col,diagonal)    
    for type, need in rule["next_to"].items():              
        if count.get(type,0)<need:                          
            return False
    needs=rule.get("needs",[])                              
    if needs:                                               
        has=0   
        for on in neighbor_tile(game_map,row,col,diagonal=False):     
            if on["building"] is not None and on["building"].rstrip("0123456789") in needs:     
                has+=1
        if has<1:
            return False     
    return True

def building_check(game_map):       #ham de kiem tra so luong cong trinh phai co trong 1 map duoc tao
    for row in range(ROWS):
        for col in range(COLLUMS):
            if placement(game_map, row, col, "treetop_village"):      
                return True
    return False    

def building_for_tile(game_map, row, col):              #ham xac dinh cong trinh duoc xay tren 1 tile
    for name in BUILD_PRIORITY:                         
        if placement(game_map, row, col, name):         
            return name                                 
    return                                         

def generate_map_new():                                 
    for _ in range(1000):                
        game_map = generate_map()
        if building_check(game_map):
            return game_map                
    return game_map            

def build(game_map, row, col, name):                   #ham xay cong trinh
    if not placement(game_map, row, col, name):        
        return False                                   
    tile = game_map[row][col]                          
    tile["building"] = name                            
    tile["level"] = 1
    return True

def up(game_map, row, col, eco):                            #ham nang cap cong trinh
    tile = game_map[row][col]                          
    if tile["darkness"]:                               
        return
    if tile["building"] is not None:                   
        upgrade = UPGRADE.get(tile["building"])        
        if upgrade is not None:                        
            if eco.try_buy(upgrade):
                tile["building"] = upgrade                 
                tile["level"] += 1                         
        return
    name = building_for_tile(game_map, row, col)       
    if name is not None:   
        if eco.try_buy(name):                          
            build(game_map, row, col, name)                
        return
    upgrade = UPGRADE.get(tile["type"])                
    if upgrade is not None:   
        if eco.try_buy(upgrade):                         
            tile["type"] = upgrade