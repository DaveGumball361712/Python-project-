import pygame as py
import random as r
from darkness import DarknessManager

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


# [CẬP NHẬT 1]: Thêm darkness_manager và darkness_surface làm tham số để hàm có thể vẽ bóng tối
def draw_map(screen, game_map, darkness_manager, darkness_surface):
    for row in range(ROWS):
        for col in range(COLLUMS):
            x = col * TILE
            y = row * TILE
            
            # 1. Vẽ nền map trước
            screen.blit(game_map[row][col], (x, y))
            
            # 2. Vẽ bóng tối đè lên nếu ô (col, row) đã bị nuốt
            if (col, row) in darkness_manager.darkened_cells:
                screen.blit(darkness_surface, (x, y))


def run_game(screen):
    images=load_images()
    game_map=generate_map(images)
    
    # [CẬP NHẬT 2]: Khởi tạo Đồng hồ (Clock) và Quản lý bóng tối (DarknessManager)
    clock = py.time.Clock()
    darkness_manager = DarknessManager(COLLUMS, ROWS)
    
    # Tạo lớp phủ màu đen
    darkness_surface = py.Surface((TILE, TILE))
    darkness_surface.fill((0, 0, 0))
    # darkness_surface.set_alpha(200) # Nếu muốn bóng tối mờ mờ thấy nền dưới thì bỏ dấu # ở đầu dòng này

    while True:
        # Tính thời gian delta_time (dt) bằng giây
        dt = clock.tick(60) / 1000.0

        for event in py.event.get():
            if event.type==py.QUIT:
                return "QUIT"
                
        # [CẬP NHẬT 3]: Kích hoạt bộ đếm giờ của bóng tối mỗi khung hình
        darkness_manager.update(dt)
        
        # [CẬP NHẬT 4]: Truyền thêm biến vào hàm vẽ
        draw_map(screen, game_map, darkness_manager, darkness_surface)
        
        py.display.flip()


if __name__=="__main__":
    py.init()
    screen=py.display.set_mode((WIDTH,HEIGHT))
    run_game(screen)
    py.quit()