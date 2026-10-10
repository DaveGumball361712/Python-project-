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

def generate_map():  #ham tao map
    lr,lc=r.choice(LOGO_CELLS)  #bien chon hang va cot cua logo 
    n_forest=r.randint(37,40)   #bien chon so forest tren ban do
    n_rocks=r.randint(14,15)    #bien chon so rocks tren ban do
    n_water=r.randint(15,18)    #bien chon so water tren ban do
    n_mushroom=4                #bien chon so mushroom tren ban do
    n_fields=144-1-n_forest-n_rocks-n_water-n_mushroom     #tinh cac o fields bang cach lay 144 tru so cac o con lai
    bag=(["forest"]*n_forest+["rocks"]*n_rocks+["water"]*n_water+["fields"]*n_fields+["mushroom"]*n_mushroom)
    r.shuffle(bag)              #sau do random toan bo so o trong bag de chung xuat hien ngau nhien
    game_map=[]                 #tao bien game_map rong
    i=0                                                 
    for row in range(ROWS):     #so row 
        map=[]                  #map rong
        for col in range(COLLUMS):#so collums
            type="logo" if (row,col)==(lr,lc) else bag[i]   #type xem hang,cot dang xet co chua logo hay khong
            if type != "logo":     #neu khong phai logo thi bien i+1
                i+=1
            map.append({            #them vao map[] ten loai o do cung voi cac chi so mac dinh khac
                "type":type,
                "building":None,
                "level":0,
                "darkness":False,
            })
        game_map.append(map)     #sau khi ket thuc vong lap thi game_map se chua du lieu trong map
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
            if on["building"] is not None and on["building"].rstrip("123456789") in needs:     #neu on thoa dieu kien khac none va on dung voi needs thi bien has+1
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

def up(game_map, row, col):                            #ham nang cap cong trinh
    tile = game_map[row][col]                          #xet tile tren game_map theo hang cot
    if tile["darkness"]:                               #neu o da dinh darkness thi khong the nang cap
        return
    if tile["building"] is not None:                   #neu da co building thi moi nang cap duoc
        upgrade = UPGRADE.get(tile["building"])        #sau do ta se nang cap cong trinh dua vao ten trong UPGRADE
        if upgrade is not None:                        #neu tile dang xet co du lieu trong upgrade
            tile["building"] = upgrade                 #thi se gan du lieu vao cho upgrade
            tile["level"] += 1                         #moi 1 lan nang cap thi level them 1
        return
    name = building_for_tile(game_map, row, col)       #neu o trong thi thu xay dung
    if name is not None:                               #neu tile dang xet co the xay duoc
        build(game_map, row, col, name)                #sau do bat dau xay dung cong trinh moi
        return
    upgrade = UPGRADE.get(tile["type"])                #neu khong phai o trong(vd:forest)
    if upgrade is not None:                            #thi se nang cap dia hinh(vd forest-->forest2)
        tile["type"] = upgrade

def run_game(screen):                                  #ham de chay game
    images=load_images()                        
    game_map=generate_map_new()
    is_playing = True
    def action_quit():
        nonlocal is_playing
        is_playing = False
    font_small = py.font.Font(None,24)
    font_main = py.font.Font(None,32)

    btn_quit = Button(x=MAP_WIDTH + 220, y=556, width=30, height=30, text="x", action=action_quit)

    def resource_text(surface, x, y, width, amount, increment, icon_img):
        # Icon resource
        surface.blit(icon_img, (x +5, y + 8))
        # Current amount
        amt_text = font_main.render(str(amount), True, (50, 50, 50))
        surface.blit(amt_text, (x + 35, y + 10))
        # Current increment
        inc_text = font_small.render(f"+{increment}", True, (100, 100, 100))

        inc_x = x + width - inc_text.get_width() - 5 
        surface.blit(inc_text, (inc_x, y + 20))

    res_height = 80
    col_width = UI_WIDTH // 2 
    row_height = res_height // 2

    resource_surface = py.Surface((UI_WIDTH, res_height))
    resource_surface.fill((204,201,195))
    line_color = (170, 155, 140)
    py.draw.line(resource_surface, line_color, (0,row_height), (UI_WIDTH, row_height), 3)
    py.draw.line(resource_surface, line_color, (col_width, 0), (col_width, res_height), 2)
    py.draw.line(resource_surface, line_color, (0, res_height-2), (UI_WIDTH, res_height-2), 3)

    Information_Surface = py.Surface((UI_WIDTH, HEIGHT))
    Information_Surface.fill((204,201,195))
    
    while is_playing:
        mouse_x, mouse_y = py.mouse.get_pos()
        # Event listener
        for event in py.event.get(): 
            if event.type==py.QUIT: 
                return "QUIT"
            
            btn_quit.handle_event(event)

            # ham bat click chuot trai xem dang click tren hang nao cot nao
            if event.type==py.MOUSEBUTTONDOWN:
                # xet xem chuot dang o cot nao bang cach chia cho TILE(48) (VD: 200/48=4,16 --> dang o cot 4)
                col=event.pos[0]//TILE
                row=event.pos[1]//TILE
                # if hang va cot trong ban do, thi se thu dung ham up(..) -> co nang cap duoc hay khong?
                if 0<=row<ROWS and 0<=col<COLLUMS:
                    up(game_map,row,col)
        
        # Create Map
        draw_map(screen, game_map,images)

        # Create Layer 1 (Resource)
        screen.blit(resource_surface, (MAP_WIDTH,0))
        # Change amount and increment
        resource_text(screen, MAP_WIDTH, 0, col_width, amount=1, increment=5, icon_img=images["icon_wood"])
        resource_text(screen, MAP_WIDTH + col_width, 0, col_width, amount=1, increment=6, icon_img=images["icon_stone"])
        resource_text(screen, MAP_WIDTH, row_height, col_width, amount=1, increment=5, icon_img=images["icon_magic"])
        resource_text(screen, MAP_WIDTH + col_width, row_height, col_width, amount=1, increment=6, icon_img=images["icon_tech"])

        # Create Layer 2 (Information)
        screen.blit(Information_Surface, (MAP_WIDTH, 80))

        if mouse_x >= MAP_WIDTH and mouse_y < 80:
            col_idx = (mouse_x - MAP_WIDTH) // 125
            row_idx = mouse_y // 40

            # { (row, col): [Tên, Số lượng, Tốc độ thu thập] } 
            resource_data = {
                (0, 0): ["Wood", 1, 5.2],
                (0, 1): ["Stone", 1, 6.0],
                (1, 0): ["Mana", 1, 5.0],
                (1, 1): ["Tech", 1, 6.0]
            }

            # Information of resource rely on mouse_pos
            current_res = resource_data.get((row_idx, col_idx))

            if current_res:
                res_name = current_res[0]
                res_amount = current_res[1]
                res_rate = current_res[2]

                line1 = f"{res_name}: {res_amount}"
                line2 = f"+{res_rate:.1f} per second"

                text1 = font_small.render(line1, True, (60, 60, 60))
                text2 = font_small.render(line2, True, (60, 60, 60))

                screen.blit(text1, (MAP_WIDTH + 15, 100))
                screen.blit(text2, (MAP_WIDTH + 15, 130))

        # create button
        btn_quit.update()
        screen.blit(btn_quit.image, btn_quit.rect)

        py.display.flip()
    return "QUIT"

if __name__=="__main__":
    py.init()
    screen=py.display.set_mode((WIDTH,HEIGHT))
    run_game(screen)
    py.quit()