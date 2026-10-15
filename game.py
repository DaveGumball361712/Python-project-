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
            # Làm mờ nhẹ phần bản đồ
            mo_nen = py.Surface((map.MAP_WIDTH, map.HEIGHT))
            mo_nen.set_alpha(150)
            mo_nen.fill((0, 0, 0))
            screen.blit(mo_nen, (0, 0))

            # Thông số kích thước Bảng
            bang_rong = 400
            bang_cao = 220
            toa_do_x = (map.MAP_WIDTH - bang_rong) // 2
            toa_do_y = (map.HEIGHT - bang_cao) // 2
            
            # Vẽ thân bảng màu xám tối & Viền vàng bo góc
            py.draw.rect(screen, (40, 40, 45), (toa_do_x, toa_do_y, bang_rong, bang_cao), border_radius=15)
            py.draw.rect(screen, (255, 215, 0), (toa_do_x, toa_do_y, bang_rong, bang_cao), 5, border_radius=15)

            # Vẽ chữ VICTORY
            font_win = py.font.SysFont('arial', 60, bold=True)
            chu_win = font_win.render("VICTORY!", True, (255, 215, 0))
            screen.blit(chu_win, (toa_do_x + bang_rong//2 - chu_win.get_width()//2, toa_do_y + 30))

            # Ghi chú thoát
            font_btn = py.font.SysFont('arial', 18, italic=True)
            chu_btn = font_btn.render("Nhan nut [ X ] o goc phai de ve Menu", True, (150, 150, 150))
            screen.blit(chu_btn, (toa_do_x + bang_rong//2 - chu_btn.get_width()//2, toa_do_y + 170))

        py.display.flip()
        
    return ket_qua_tra_ve