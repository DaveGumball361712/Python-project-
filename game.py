import pygame as py
import map
import darkness
from economy import EconomyManager
from ui import SidePanel

def run_game(screen):
    clock = py.time.Clock()
    
    # Khởi tạo dữ liệu ván mới (Reset mọi thứ mỗi khi bấm Start)
    hinh_anh_map = map.load_images()
    ban_do_game = map.generate_map_new()
    quan_ly_kinh_te = EconomyManager()
    quan_ly_bong_toi = darkness.DarknessManager(map.COLLUMS, map.ROWS)
    
    # CODE TUTORIAL Khởi tạo
    from tutorial import Tutorial
    font_tutorial = py.font.SysFont('arial', 20, bold=True)
    huong_dan = Tutorial(ban_do_game, map.ROWS, map.COLLUMS, map.TILE, lambda r, c: False)
    # ------------------------------------------------
    
    is_paused = False
    time_multiplier = 1
    is_win = False
    running = True
    ket_qua_tra_ve = "MENU"
    
    # Các hàm tương tác nút bấm UI
    def action_quit():
        nonlocal running, ket_qua_tra_ve
        running = False
        ket_qua_tra_ve = "MENU"

    def action_pause():
        nonlocal is_paused, is_win
        if is_win: return # Thắng rồi thì khóa nút Pause
        is_paused = not is_paused
        ui_panel.toggle_pause_ui(is_paused)

    def action_speed():
        nonlocal time_multiplier
        if time_multiplier == 1:
            time_multiplier = 2
        elif time_multiplier == 2:
            time_multiplier = 4
        else:
            time_multiplier = 1
        ui_panel.toggle_speed_ui(time_multiplier)

    # Khởi tạo UI
    ui_panel = SidePanel(map.MAP_WIDTH, map.UI_WIDTH, map.HEIGHT, action_quit, action_pause, action_speed, map.TILE, map.ROWS, map.COLLUMS)
    ui_panel.toggle_pause_ui(False)
    ui_panel.toggle_speed_ui(1)
    
    # Vòng lặp Game Play
    while running:
        dt = clock.tick(60) / 1000.0
        mouse_x, mouse_y = py.mouse.get_pos()
        
        # CẬP NHẬT LOGIC (Chỉ chạy khi không Pause)
        if not is_paused:
            game_dt = dt * time_multiplier
            quan_ly_kinh_te.update(game_dt, ban_do_game)
            
            o_bi_nuot = quan_ly_bong_toi.update(game_dt)
            if o_bi_nuot:
                c_dark, r_dark = o_bi_nuot
                if 0 <= r_dark < map.ROWS and 0 <= c_dark < map.COLLUMS:
                    ban_do_game[r_dark][c_dark]["darkness"] = True
                quan_ly_bong_toi.dong_bo_cap_do_thap(ban_do_game)
                
            # CODE TUTORIAL Cập nhật nháy
            if huong_dan.active:
                huong_dan.update(dt)
            # ----------------------------------------------------
                
        # Kiểm tra thua
        if quan_ly_bong_toi.check_lose_condition() and len(quan_ly_bong_toi.darkened_cells) >= map.ROWS * map.COLLUMS:
            print("--- GAME OVER: Ban do da bi nuot sach! ---")
            return "MENU"
            
        # XỬ LÝ SỰ KIỆN
        for event in py.event.get():
            if event.type == py.QUIT:
                return "QUIT"
                
            ui_panel.handle_event(event)
            
            # Xử lý click chuột xây nhà/nâng cấp
            if event.type == py.MOUSEBUTTONDOWN and event.button == 1:
                col = event.pos[0] // map.TILE
                row = event.pos[1] // map.TILE
                if 0 <= row < map.ROWS and 0 <= col < map.COLLUMS:
                    if not is_paused:
                        # CODE TUTORIAL Chặn click sai
                        if huong_dan.active and not huong_dan.allowed(row, col):
                            continue # Bấm sai ô hướng dẫn thì không cho xây
                        nha_cu = ban_do_game[row][col]["type"] # Nhớ nhà cũ
                        # -------------------------------------------------------
                        
                        map.up(ban_do_game, row, col, quan_ly_kinh_te)
                        quan_ly_bong_toi.dong_bo_cap_do_thap(ban_do_game)
                        
                        # CODE TUTORIAL Báo cáo kết quả
                        if huong_dan.active:
                            huong_dan.on_action(row, col, nha_cu != ban_do_game[row][col]["type"])
                        # --------------------------------------------------------
                        
                        # Kiểm tra thắng (Nâng cấp The Stone)
                        if ban_do_game[row][col]["type"] == "the_stone":
                            quan_ly_bong_toi.trigger_win_condition()
                            is_win = True
                            is_paused = True
                            ui_panel.toggle_pause_ui(True)
                            
        # VẼ ĐỒ HỌA
        screen.fill((0, 0, 0))
        map.draw_map(screen, ban_do_game, hinh_anh_map)
        
        for cell_x, cell_y in quan_ly_bong_toi.darkened_cells:
            mang_den = py.Surface((map.TILE, map.TILE))
            mang_den.set_alpha(200)
            mang_den.fill((0, 0, 0))
            screen.blit(mang_den, (cell_x * map.TILE, cell_y * map.TILE))
            
        ui_panel.draw(screen, mouse_x, mouse_y, quan_ly_kinh_te, hinh_anh_map, is_paused, ban_do_game)
        
        # CODE TUTORIAL Vẽ bảng hướng dẫn
        if huong_dan.active:
            huong_dan.draw(screen, font_tutorial)
        # ----------------------------------------------------------
        
      # VẼ BẢNG CHÚC MỪNG CHIẾN THẮNG (UI)
        if is_win:
            # Kích thước 
            banner_height = 90
            toa_do_y = map.HEIGHT - banner_height
            
            # Vẽ nền màu xám và viền màu nâu y hệt style của Phút
            py.draw.rect(screen, (204, 201, 195), (0, toa_do_y, map.MAP_WIDTH, banner_height))
            py.draw.line(screen, (170, 155, 140), (0, toa_do_y), (map.MAP_WIDTH, toa_do_y), 3)
            
            # Tạo 2 dòng chữ với kích thước khác nhau
            font_win = py.font.SysFont('arial', 20, bold=True)
            font_sub = py.font.SysFont('arial', 16, italic=True)
            
            chu_win = font_win.render("You saved the land from the darkness! Great job!", True, (40, 40, 40))
            chu_sub = font_sub.render("Press the [X] button to return to the menu.", True, (100, 100, 100)) # Dòng phụ màu xám nhạt hơn
            
            # Căn giữa tọa độ X cho cả 2 dòng
            toa_do_x_win = (map.MAP_WIDTH - chu_win.get_width()) // 2
            toa_do_x_sub = (map.MAP_WIDTH - chu_sub.get_width()) // 2
            
            # Vẽ lên màn hình 
            screen.blit(chu_win, (toa_do_x_win, toa_do_y + 20))
            screen.blit(chu_sub, (toa_do_x_sub, toa_do_y + 55))
        py.display.flip()
        
    return ket_qua_tra_ve