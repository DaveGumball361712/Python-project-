import pygame
import sys
import menu
import map
import darkness
import economy 

pygame.init()
screen = pygame.display.set_mode((map.WIDTH, map.HEIGHT))
pygame.display.set_caption("Stop the Darkness - Đồ án Nhóm")

clock = pygame.time.Clock()

trang_thai = "MENU"
man_hinh_menu = menu.MainMenu(screen)

# 1. TÍCH HỢP MAP CỦA PHÚT
hinh_anh_map = map.load_images()
ban_do_game = map.generate_map_new()

# 2. TÍCH HỢP BÓNG TỐI CỦA BẢO
quan_ly_bong_toi = darkness.DarknessManager(map.COLLUMS, map.ROWS)
# Đặt tốc độ khởi đầu chuẩn 6s/ô của Bảo (nếu cậu muốn test nhanh 0.2s thì thêm dấu # ở đầu dòng dưới nhé)
quan_ly_bong_toi.set_resistance_level(0)

# Hàm phụ trợ: Quét bản đồ của Phút để báo cấp độ Tower of Light cho Bảo
def dong_bo_cap_do_thap(game_map, dark_mgr):
    cap_do_thap = 0
    for r in range(map.ROWS):
        for c in range(map.COLLUMS):
            tile = game_map[r][c]
            # Chỉ tính tháp khi ô đó chưa bị bóng tối nuốt
            if not tile["darkness"] and tile["building"] is not None:
                if tile["building"] == "tower_of_light":
                    cap_do_thap = max(cap_do_thap, 1)
                elif tile["building"] == "tower_of_light2":
                    cap_do_thap = max(cap_do_thap, 2)
    dark_mgr.set_resistance_level(cap_do_thap)

# Bộ đếm thời gian 1 giây
SU_KIEN_1_GIAY = pygame.USEREVENT + 1
pygame.time.set_timer(SU_KIEN_1_GIAY, 1000)

while True:
    if trang_thai == "MENU":
        ket_qua = man_hinh_menu.run()
        if ket_qua == "QUIT":
            pygame.quit()
            sys.exit()
        elif ket_qua == "PLAYING":
            trang_thai = "GAME" 

    elif trang_thai == "GAME":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # TƯƠNG TÁC CHUỘT: GỌI HÀM up() CỦA PHÚT + CẬP NHẬT THÁP CHO BẢO
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Click chuột trái
                    col = event.pos[0] // map.TILE
                    row = event.pos[1] // map.TILE
                    if 0 <= row < map.ROWS and 0 <= col < map.COLLUMS:
                        map.up(ban_do_game, row, col)
                        # Sau khi xây/nâng cấp, kiểm tra xem có Tower of Light không để báo cho Bảo
                        dong_bo_cap_do_thap(ban_do_game, quan_ly_bong_toi)
            
            # NHỊP ĐẾM MỖI GIÂY
            if event.type == SU_KIEN_1_GIAY:
                # 1. Gọi não bộ kinh tế của Đạt
                economy.cap_nhat_tai_nguyen(ban_do_game)
                
                # 2. Gọi thuật toán bóng tối của Bảo
                o_bi_nuot = quan_ly_bong_toi.update(1.0)
                if o_bi_nuot:
                    # Lưu ý: Bảo trả về (x, y) tương ứng với (col, row)
                    c_dark, r_dark = o_bi_nuot
                    if 0 <= r_dark < map.ROWS and 0 <= c_dark < map.COLLUMS:
                        ban_do_game[r_dark][c_dark]["darkness"] = True
                    
                    # Nếu bóng tối nuốt trúng ô có Tower of Light thì cập nhật giảm kháng cự về 0
                    dong_bo_cap_do_thap(ban_do_game, quan_ly_bong_toi)
                    print(f"!!! Bong toi nuot o (col={c_dark}, row={r_dark}) | Toc do: {quan_ly_bong_toi.current_tick_rate}s/o !!!")

                # 3. Kiểm tra điều kiện Thua của Bảo (khi đã nuốt hết 144 ô)
                if quan_ly_bong_toi.check_lose_condition() and len(quan_ly_bong_toi.darkened_cells) >= map.ROWS * map.COLLUMS:
                    print("--- GAME OVER: Ban do da bi bong toi nuot sach! ---")
                    trang_thai = "MENU" # Tạm thời quay về Menu (lát nữa nối với màn hình Lose của Tony)

        # VẼ BẢN ĐỒ CỦA PHÚT
        map.draw_map(screen, ban_do_game, hinh_anh_map)
        
        # VẼ ĐỒ HỌA BÓNG TỐI CHE LẤP CỦA BẢO (cell_x là cột, cell_y là hàng)
        for cell_x, cell_y in quan_ly_bong_toi.darkened_cells:
            toa_do_x = cell_x * map.TILE
            toa_do_y = cell_y * map.TILE
            
            mang_den = pygame.Surface((map.TILE, map.TILE))
            mang_den.set_alpha(200) 
            mang_den.fill((0, 0, 0)) 
            screen.blit(mang_den, (toa_do_x, toa_do_y))
            
        pygame.display.flip()
        
    clock.tick(60)