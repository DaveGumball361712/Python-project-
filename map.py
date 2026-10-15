import pygame as py
import random as r
from menu import Button
from Economy import EconomyManager
from ui import SidePanel

ROWS=12
COLLUMS=12
TILE=48

MAP_WIDTH=COLLUMS*TILE
UI_WIDTH = 250 
WIDTH = MAP_WIDTH + UI_WIDTH
HEIGHT=ROWS*TILE
LOGO_CELLS=[(5,5),(5,6),(6,5),(6,6)]
IMAGE_DATA={      #Chuyen doi hinh anh thanh du lieu
    "forest":"forest","forest2":"forest2","forest3":"forest3","forest4":"forest4",
    "fields":"fields",
    "rocks":"rocks","rocks2":"rocks2","rocks3":"rocks3",
    "water":"water",
    "logo":"logo",
    "mushroom":"mushroom","mushroom2":"mushroom2",
}

BUILDING_IMAGE_DATA={       #Chuyen doi hinh anh thanh du lieu cho cong trinh
    "tower_of_light":"tower_of_light","tower_of_light2":"tower_of_light2",
    "village":"village","village2":"village2",
    "port_village":"port_village","port_village2":"port_village2",
    "mining_village":"mining_village","mining_village2":"mining_village2",
    "treetop_village":"treetop_village","treetop_village2":"treetop_village2",
    "magical_port_village":"magical_port_village","magical_port_village2":"magical_port_village2",
    "magical_village":"magical_village","magical_village2":"magical_village2",
}

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
        img=py.image.load("images/"+name).convert_alpha() #img se load anh dua vao duong dan cua file images/tencuaanh
        return py.transform.scale(img,(TILE,TILE))      #hien ra hinh anh theo ti le cua bien SCALE 

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

def generate_map():  #ham tao map
    lr,lc=r.choice(LOGO_CELLS)  #bien chon hang va cot cua logo 
    n_forest=r.randint(37,40)   #bien chon so forest tren ban do
    n_rocks=r.randint(14,15)    #bien chon so rocks tren ban do
    n_water=r.randint(27,33)    #bien chon so water tren ban do
    n_mushroom=4                #bien chon so mushroom tren ban do
    n_fields=144-1-n_forest-n_rocks-n_water-n_mushroom     #tinh cac o fields bang cach lay 144 tru so cac o con lai
    occupied = {(lr,lc)}                     
    water = []; remaining = n_water
    while remaining > 0:
        lake_size = min(remaining, r.randint(3,7))  
        blob = grow_blob(occupied, lake_size)
        if not blob:
            break
        water += blob; remaining -= len(blob)
    water = set(water)
    bag=(["forest"]*n_forest+["rocks"]*n_rocks+["fields"]*n_fields+["mushroom"]*n_mushroom)
    r.shuffle(bag)              #sau do random toan bo so o trong bag de chung xuat hien ngau nhien
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
            tile=game_map[row][col]   #game_map chua hang va cot
            screen.blit(images[IMAGE_DATA[tile["type"]]],(col*TILE,row*TILE))    #tai hang va cot dang xet, in hinh anh trung voi type da khai bao
            b=tile["building"]    #ham tro den "building" trong tile
            if b is not None:    #neu b khac None thi se gan hinh anh cua building ghi de len type trung voi BUILDING_IMAGE_DATA
                img=BUILDING_IMAGE_DATA.get(b)
                if img is not None:      
                    screen.blit(images[img],(col*TILE,row*TILE))    #ve lop cong trinh

def neighbor_tile(game_map,row,col,diagonal=True):     #ham kiem tra o lan can
    direction=[(-1,0),(1,0),(0,1),(0,-1)]              #cac huong lan can khong tinh duong cheo:tren,duoi,phai,trai
    if diagonal:
        direction+=[(1,1),(-1,-1),(1,-1),(-1,1)]       #neu tinh duong cheo thi them cac huong: duoi phai,tren trai,duoi trai, tren phai
    result=[]                                   
    for dr,dc in direction:                            #bien dr,dc chi huong dang xet
        nr,nc=row+dr,col+dc                            #nr,nc la cac o lan can
        if 0<=nr<ROWS and 0<=nc<COLLUMS:               #ham dieu kien de nr,nc khong vuot khoi map
            result.append(game_map[nr][nc])            #sau do them cac o lan can vao result trong game_map
    return result

def count_neighbor_tile(game_map,row,col,diagonal=True):        #ham dem cac o lan can
    count={}
    for on in neighbor_tile(game_map,row,col,diagonal):         #xet cac o lan can dua vao ket qua của neighbor_tile
        name=on["type"].rstrip("0123456789")                    #kiem tra type cua tile do va loai bo so (vd:forest2-->forest)
        count[name]=count.get(name,0)+1                         #sau do dem o nay xuat hien may lan trong o lan can, neu chua xuat hien lan nao thi mac dinh là 0 sau do +1
    return count

def building_exists(game_map, name):                  #ham kiem tra building da ton tai chua
    for row in game_map:
        for tile in row:
            if tile["building"] is not None and tile["building"].rstrip("0123456789")==name:    #neu building khac none va da ton tai tren tile dang xet thi return True
                return True
    return False          

def placement(game_map,row,col,name):           #ham kiem tra dieu kien xay
    on=game_map[row][col]                       #xet hang,cot tren game_map
    rule=BUILDING_RULES[name]                   #xet luat tren list BUILDING_RULES
    if name in ONE_TIME_BUILDING and building_exists(game_map,name):    #Kiem tra xem tren tile co phai la o xay 1 lan va da ton tai chua
        return False        #neu thoa man thi return false
    diagonal=rule.get("diagonal",True)     
    if on["type"]not in rule["on"]:    #neu type khong thoa man dieu kien on cua BUILDING RULE thi return fakse
        return False
    if on["building"] is not None or on["darkness"]:        #neu tile do da duoc xay dung hoac da dinh darkness thi return false
        return(False)
    count=count_neighbor_tile(game_map,row,col,diagonal)    #dem cac loai o lan can cua tile dang xet
    for type, need in rule["next_to"].items():              #vong lap for voi cac o co dieu kien next_to
        if count.get(type,0)<need:                          #neu tile dang xet khong du cac o lan can thi false
            return False
    needs=rule.get("needs",[])                              
    if needs:                                               #xet cac tile co dieu kien needs
        has=0   
        for on in neighbor_tile(game_map,row,col,diagonal=False):     #kiem tra cac tile lan can cua tile dang xet
            if on["building"] is not None and on["building"].rstrip("0123456789") in needs:     #neu on thoa dieu kien khac none va on dung voi needs thi bien has+1
                has+=1
        if has<1:
            return False     #neu khong du thi return false
    return True

def building_check(game_map):       #ham de kiem tra so luong cong trinh phai co trong 1 map duoc tao
    for row in range(ROWS):
        for col in range(COLLUMS):
            if placement(game_map, row, col, "treetop_village"):      #neu trong 1 map co it nhat 1 tile thoa dieu kien dat treetop_village thi return true 
                return True
    return False    #neu khong thi false va lap lai cho den khi het map

def building_for_tile(game_map, row, col):              #ham xac dinh cong trinh duoc xay tren 1 tile
    for name in BUILD_PRIORITY:                         #muc do uu tien lay tu list BUILD_PRIORITY
        if placement(game_map, row, col, name):         #xet xem tile dang xet co thoa dieu kien placement khong, xet tu tren xuong duoi
            return name                                 #neu thoa man thi return name
    return None                                         

def generate_map_new():                                 #sau khi da hoan thanh buiding_check thi luc nay ta se tao moi map lien tuc cho den khi co 1 map thoa man dieu kien building_check
    for _ in range(1000):                
        game_map = generate_map()
        if building_check(game_map):
            return game_map               
    return game_map            

def build(game_map, row, col, name):                   #ham xay cong trinh
    if not placement(game_map, row, col, name):        #kiem tra xem name nay xay duoc gi trong placement
        return False                                   #neu khong du dieu kien thi return false
    tile = game_map[row][col]                          #neu du dieu kien thi tile tham chieu toi game_map theo hang cot
    tile["building"] = name                            #sau do nhap cac chi so mac dinh vao dict theo ten cong trinh
    tile["level"] = 1
    return True

def up(game_map, row, col, eco):                            #ham nang cap cong trinh
    tile = game_map[row][col]                          #xet tile tren game_map theo hang cot
    if tile["darkness"]:                               #neu o da dinh darkness thi khong the nang cap
        return
    if tile["building"] is not None:                   #neu da co building thi moi nang cap duoc
        upgrade = UPGRADE.get(tile["building"])        #sau do ta se nang cap cong trinh dua vao ten trong UPGRADE
        if upgrade is not None:                        #neu tile dang xet co du lieu trong upgrade
            if eco.try_buy(upgrade):
                tile["building"] = upgrade                 #thi se gan du lieu vao cho upgrade
                tile["level"] += 1                         #moi 1 lan nang cap thi level them 1
        return
    name = building_for_tile(game_map, row, col)       #neu o trong thi thu xay dung
    if name is not None:    
        if eco.try_buy(name):                           #neu tile dang xet co the xay duoc
            build(game_map, row, col, name)                #sau do bat dau xay dung cong trinh moi
        return
    upgrade = UPGRADE.get(tile["type"])                #neu khong phai o trong(vd:forest)
    if upgrade is not None:   
        if eco.try_buy(upgrade):                         #thi se nang cap dia hinh(vd forest-->forest2)
            tile["type"] = upgrade

def run_game(screen):                                  #ham de chay game
    images=load_images()                        
    game_map=generate_map_new()
    eco = EconomyManager()
    clock = py.time.Clock()

    is_playing = True
    is_paused = False
    time_multiplier = 1

    def action_quit():
        nonlocal is_playing
        is_playing = False

    def action_pause():
        nonlocal is_paused
        is_paused = not is_paused
        # Gọi UI để nó đổi giao diện nút bấm
        ui_panel.toggle_pause_ui(is_paused)

    # HÀM XỬ LÝ KHI BẤM NÚT SPEED
    def action_speed():
        nonlocal time_multiplier
        # Xoay vòng tốc độ: 1 -> 2 -> 4 -> quay lại 1
        if time_multiplier == 1:
            time_multiplier = 2
        elif time_multiplier == 2:
            time_multiplier = 4
        else:
            time_multiplier = 1
        
        ui_panel.toggle_speed_ui(time_multiplier)

    #create UI
    ui_panel = SidePanel(MAP_WIDTH, UI_WIDTH, HEIGHT, action_quit, action_pause, action_speed, TILE, ROWS, COLLUMS)

    while is_playing:
        dt = clock.tick(60) / 1000.0 

        if not is_paused:
            game_dt = dt * time_multiplier
            eco.update(game_dt, game_map)

        # Lấy tọa độ chuột
        mouse_x, mouse_y = py.mouse.get_pos()

        # Event listener
        for event in py.event.get(): 
            if event.type==py.QUIT: 
                return "QUIT"
            
            ui_panel.handle_event(event)

            # ham bat click chuot trai xem dang click tren hang nao cot nao
            if event.type==py.MOUSEBUTTONDOWN and event.button == 1:
                # xet xem chuot dang o cot nao bang cach chia cho TILE(48) (VD: 200/48=4,16 --> dang o cot 4)
                col=event.pos[0]//TILE
                row=event.pos[1]//TILE
                # if hang va cot trong ban do, thi se thu dung ham up(..) -> co nang cap duoc hay khong?
                if 0<=row<ROWS and 0<=col<COLLUMS:
                    # Khóa không cho người chơi nâng cấp/xây nhà nếu đang Pause
                    if not is_paused: 
                        up(game_map, row, col, eco)
        
        # Create Map
        draw_map(screen, game_map,images)

        # Create menu
        ui_panel.draw(screen, mouse_x, mouse_y, eco, images, is_paused, game_map)

        py.display.flip()
    return "QUIT"

if __name__=="__main__":
    py.init()
    screen=py.display.set_mode((WIDTH,HEIGHT))
    run_game(screen)
    py.quit()