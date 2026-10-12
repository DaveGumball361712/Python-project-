import pygame
import sys
import menu
import map
import darkness
import economy 

pygame.init()
# Mở rộng màn hình thành 826 x 576 (576 cho Map + 250 cho Sidebar UI của Tony & Đạt)
screen = pygame.display.set_mode((map.WIDTH, map.HEIGHT))
pygame.display.set_caption("Stop the Darkness - Đồ án Nhóm")

clock = pygame.time.Clock()

trang_thai = "MENU"
man_hinh_menu = menu.MainMenu(screen)

# 1. KHỞI TẠO MAP (PHÚT) + KINH TẾ (ĐẠT) + BÓNG TỐI (BẢO)
hinh_anh_map = map.load_images()
ban_do_game = map.generate_map_new()
quan_ly_kinh_te = economy.EconomyManager()
quan_ly_bong_toi = darkness.DarknessManager(map.COLLUMS, map.ROWS)
quan_ly_bong_toi.set_resistance_level(0) # Tốc độ chuẩn 6s/ô của Bảo

# 2. THIẾT LẬP GIAO DIỆN SIDEBAR UI CỦA TONY & ĐẠT
font_small = pygame.font.Font(None, 24)
font_main = pygame.font.Font(None, 32)

def action_quit():
    global trang_thai
    trang_thai = "MENU"

btn_quit = menu.Button(x=map.MAP_WIDTH + 220, y=556, width=30, height=30, text="x", action=action_quit)

def resource_text(surface, x, y, width, amount, increment, icon_img):
    surface.blit(icon_img, (x + 5, y + 8))
    amt_text = font_main.render(str(int(amount)), True, (50, 50, 50))
    surface.blit(amt_text, (x + 35, y + 10))
    inc_text = font_small.render(f"+{increment:.1f}", True, (100, 100, 100))
    inc_x = x + width - inc_text.get_width() - 5 
    surface.blit(inc_text, (inc_x, y + 20))

res_height = 80
col_width = map.UI_WIDTH // 2 
row_height = res_height // 2

resource_surface = pygame.Surface((map.UI_WIDTH, res_height))
resource_surface.fill((204, 201, 195))
line_color = (170, 155, 140)
pygame.draw.line(resource_surface, line_color, (0, row_height), (map.UI_WIDTH, row_height), 3)
pygame.draw.line(resource_surface, line_color, (col_width, 0), (col_width, res_height), 2)
pygame.draw.line(resource_surface, line_color, (0, res_height - 2), (map.UI_WIDTH, res_height - 2), 3)

Information_Surface = pygame.Surface((map.UI_WIDTH, map.HEIGHT))
Information_Surface.fill((204, 201, 195))

# Hàm phụ trợ: Đồng bộ cấp độ Tower of Light giữa Map của Phút và Bóng tối của Bảo
def dong_bo_cap_do_thap(game_map, dark_mgr):
    cap_do_thap = 0
    for r in range(map.ROWS):
        for c in range(map.COLLUMS):
            tile = game_map[r][c]
            if not tile["darkness"] and tile["building"] is not None:
                if tile["building"] == "tower_of_light":
                    cap_do_thap = max(cap_do_thap, 1)
                elif tile["building"] == "tower_of_light2":
                    cap_do_thap = max(cap_do_thap, 2)
    dark_mgr.set_resistance_level(cap_do_thap)

while True:
    if trang_thai == "MENU":
        screen.fill((40, 40, 40)) # Xóa nền sạch sẽ khi ở Menu
        ket_qua = man_hinh_menu.run()
        if ket_qua == "QUIT":
            pygame.quit()
            sys.exit()
        elif ket_qua == "PLAYING":
            clock.tick(60) # Reset bộ đếm dt trước khi vào trận
            trang_thai = "GAME" 

    elif trang_thai == "GAME":
        # Tính delta_time mượt theo từng khung hình (y hệt code của Đạt & Tony)
        dt = clock.tick(60) / 1000.0
        
        # 1. Cập nhật Kinh tế của Đạt
        quan_ly_kinh_te.update(dt, ban_do_game)
        
        # 2. Cập nhật Bóng tối của Bảo
        o_bi_nuot = quan_ly_bong_toi.update(dt)
        if o_bi_nuot:
            c_dark, r_dark = o_bi_nuot
            if 0 <= r_dark < map.ROWS and 0 <= c_dark < map.COLLUMS:
                ban_do_game[r_dark][c_dark]["darkness"] = True
            dong_bo_cap_do_thap(ban_do_game, quan_ly_bong_toi)

        # Kiểm tra điều kiện Thua của Bảo
        if quan_ly_bong_toi.check_lose_condition() and len(quan_ly_bong_toi.darkened_cells) >= map.ROWS * map.COLLUMS:
            print("--- GAME OVER: Ban do da bi bong toi nuot sach! ---")
            trang_thai = "MENU"

        mouse_x, mouse_y = pygame.mouse.get_pos()

        # 3. Bắt sự kiện chuột
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            btn_quit.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                col = event.pos[0] // map.TILE
                row = event.pos[1] // map.TILE
                if 0 <= row < map.ROWS and 0 <= col < map.COLLUMS:
                    # Gọi thẳng hàm up(game_map, row, col, eco) của Phút + Đạt!
                    map.up(ban_do_game, row, col, quan_ly_kinh_te)
                    dong_bo_cap_do_thap(ban_do_game, quan_ly_bong_toi)

        # 4. VẼ BẢN ĐỒ CỦA PHÚT
        map.draw_map(screen, ban_do_game, hinh_anh_map)
        
        # 5. VẼ BÓNG TỐI CỦA BẢO
        for cell_x, cell_y in quan_ly_bong_toi.darkened_cells:
            toa_do_x = cell_x * map.TILE
            toa_do_y = cell_y * map.TILE
            mang_den = pygame.Surface((map.TILE, map.TILE))
            mang_den.set_alpha(200) 
            mang_den.fill((0, 0, 0)) 
            screen.blit(mang_den, (toa_do_x, toa_do_y))

        # 6. VẼ SIDEBAR UI CỦA TONY & ĐẠT
        screen.blit(resource_surface, (map.MAP_WIDTH, 0))
        resource_text(screen, map.MAP_WIDTH, 0, col_width, 
                      amount=quan_ly_kinh_te.inventory['W'], increment=quan_ly_kinh_te.production_per_minute['W'], icon_img=hinh_anh_map["icon_wood"])
        resource_text(screen, map.MAP_WIDTH + col_width, 0, col_width, 
                      amount=quan_ly_kinh_te.inventory['S'], increment=quan_ly_kinh_te.production_per_minute['S'], icon_img=hinh_anh_map["icon_stone"])
        resource_text(screen, map.MAP_WIDTH, row_height, col_width, 
                      amount=quan_ly_kinh_te.inventory['M'], increment=quan_ly_kinh_te.production_per_minute['M'], icon_img=hinh_anh_map["icon_magic"])
        resource_text(screen, map.MAP_WIDTH + col_width, row_height, col_width, 
                      amount=quan_ly_kinh_te.inventory['T'], increment=quan_ly_kinh_te.production_per_minute['T'], icon_img=hinh_anh_map["icon_tech"])

        screen.blit(Information_Surface, (map.MAP_WIDTH, 80))

        # Hiển thị chi tiết khi rê chuột vào 4 ô tài nguyên trên Sidebar
        if mouse_x >= map.MAP_WIDTH and mouse_y < 80:
            col_idx = (mouse_x - map.MAP_WIDTH) // 125
            row_idx = mouse_y // 40

            resource_data = {
                (0, 0): ["Wood", int(quan_ly_kinh_te.inventory['W']), quan_ly_kinh_te.production_per_minute['W']],
                (0, 1): ["Stone", int(quan_ly_kinh_te.inventory['S']), quan_ly_kinh_te.production_per_minute['S']],
                (1, 0): ["Mana", int(quan_ly_kinh_te.inventory['M']), quan_ly_kinh_te.production_per_minute['M']],
                (1, 1): ["Tech", int(quan_ly_kinh_te.inventory['T']), quan_ly_kinh_te.production_per_minute['T']]
            }

            current_res = resource_data.get((row_idx, col_idx))
            if current_res:
                line1 = f"{current_res[0]}: {current_res[1]}"
                line2 = f"+{current_res[2]:.1f} per minute"
                text1 = font_small.render(line1, True, (60, 60, 60))
                text2 = font_small.render(line2, True, (60, 60, 60))
                screen.blit(text1, (map.MAP_WIDTH + 15, 100))
                screen.blit(text2, (map.MAP_WIDTH + 15, 130))

        # Nút X thoát ra Menu ở góc dưới bên phải
        btn_quit.update()
        screen.blit(btn_quit.image, btn_quit.rect)
            
        pygame.display.flip()