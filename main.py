import pygame as py
import sys
import menu
import map
import darkness
from economy import EconomyManager
from ui import SidePanel

py.init()
# Mở rộng màn hình thành 826 x 576 (576 cho Map + 250 cho Sidebar UI của Tony & Đạt)
screen = py.display.set_mode((map.WIDTH, map.HEIGHT))
py.display.set_caption("Stop the Darkness - Đồ án Nhóm")

clock = py.time.Clock()

trang_thai = "MENU"
man_hinh_menu = menu.MainMenu(screen)

# 1. KHỞI TẠO MAP (PHÚT) + KINH TẾ (ĐẠT/TONY) + BÓNG TỐI (BẢO)
hinh_anh_map = map.load_images()
ban_do_game = map.generate_map_new()
quan_ly_kinh_te = EconomyManager()
quan_ly_bong_toi = darkness.DarknessManager(map.COLLUMS, map.ROWS)

# 2. KHỞI TẠO CÁC BIẾN CHO UI VÀ TRẠNG THÁI GAME
is_paused = False
time_multiplier = 1

def action_quit():
    global trang_thai
    trang_thai = "MENU"

def action_pause():
    global is_paused
    is_paused = not is_paused
    ui_panel.toggle_pause_ui(is_paused)

def action_speed():
    global time_multiplier
    if time_multiplier == 1:
        time_multiplier = 2
    elif time_multiplier == 2:
        time_multiplier = 4
    else:
        time_multiplier = 1
    ui_panel.toggle_speed_ui(time_multiplier)

# 3. KHỞI TẠO SIDEBAR UI CỦA TONY
ui_panel = SidePanel(map.MAP_WIDTH, map.UI_WIDTH, map.HEIGHT, action_quit, action_pause, action_speed, map.TILE, map.ROWS, map.COLLUMS)

while True:
    if trang_thai == "MENU":
        screen.fill((40, 40, 40)) # Xóa nền sạch sẽ khi ở Menu
        ket_qua = man_hinh_menu.run()
        if ket_qua == "QUIT":
            py.quit()
            sys.exit()
        elif ket_qua == "PLAYING":
            clock.tick(60) # Reset bộ đếm dt trước khi vào trận
            trang_thai = "GAME" 

    elif trang_thai == "GAME":
        dt = clock.tick(60) / 1000.0
        mouse_x, mouse_y = py.mouse.get_pos()
        
        # --- CẬP NHẬT LOGIC GAME (NẾU KHÔNG PAUSE) ---
        if not is_paused:
            game_dt = dt * time_multiplier
            
            # Cập nhật Kinh tế
            quan_ly_kinh_te.update(game_dt, ban_do_game)
            
            # Cập nhật Bóng tối
            o_bi_nuot = quan_ly_bong_toi.update(game_dt)
            if o_bi_nuot:
                c_dark, r_dark = o_bi_nuot
                if 0 <= r_dark < map.ROWS and 0 <= c_dark < map.COLLUMS:
                    ban_do_game[r_dark][c_dark]["darkness"] = True
                
                # Gọi hàm đồng bộ tháp TỪ ĐỐI TƯỢNG BÓNG TỐI (Đã dọn từ main sang darkness.py)
                quan_ly_bong_toi.dong_bo_cap_do_thap(ban_do_game)

        # Kiểm tra điều kiện Thua của Bảo
        if quan_ly_bong_toi.check_lose_condition() and len(quan_ly_bong_toi.darkened_cells) >= map.ROWS * map.COLLUMS:
            print("--- GAME OVER: Ban do da bi bong toi nuot sach! ---")
            trang_thai = "MENU"

        # --- XỬ LÝ SỰ KIỆN ---
        for event in py.event.get():
            if event.type == py.QUIT:
                py.quit()
                sys.exit()

            # Chuyển sự kiện cho UI xử lý (nút bấm)
            ui_panel.handle_event(event)

            # Xử lý click chuột xây nhà/nâng cấp
            if event.type == py.MOUSEBUTTONDOWN and event.button == 1:
                col = event.pos[0] // map.TILE
                row = event.pos[1] // map.TILE
                if 0 <= row < map.ROWS and 0 <= col < map.COLLUMS:
                    if not is_paused: # Chỉ cho xây khi không pause
                        map.up(ban_do_game, row, col, quan_ly_kinh_te)
                        quan_ly_bong_toi.dong_bo_cap_do_thap(ban_do_game)

        # --- VẼ LÊN MÀN HÌNH ---
        screen.fill((0, 0, 0)) # Xóa khung hình cũ
        
        # 1. Vẽ bản đồ của Phút
        map.draw_map(screen, ban_do_game, hinh_anh_map)
        
        # 2. Vẽ hiệu ứng bóng tối của Bảo
        for cell_x, cell_y in quan_ly_bong_toi.darkened_cells:
            toa_do_x = cell_x * map.TILE
            toa_do_y = cell_y * map.TILE
            mang_den = py.Surface((map.TILE, map.TILE))
            mang_den.set_alpha(200) 
            mang_den.fill((0, 0, 0)) 
            screen.blit(mang_den, (toa_do_x, toa_do_y))

        # 3. Vẽ toàn bộ giao diện UI của Tony
        ui_panel.draw(screen, mouse_x, mouse_y, quan_ly_kinh_te, hinh_anh_map, is_paused, ban_do_game)

        py.display.flip()