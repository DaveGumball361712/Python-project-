import pygame
import sys
import menu
import map
import darkness

pygame.init()
screen = pygame.display.set_mode((576, 576))
pygame.display.set_caption("Stop the Darkness - Đồ án Nhóm")

clock = pygame.time.Clock()

trang_thai = "MENU"
man_hinh_menu = menu.MainMenu(screen)

# TÍCH HỢP MAP MỚI: Tải hình ảnh 1 lần và sinh bản đồ dữ liệu
hinh_anh_map = map.load_images()
ban_do_game = map.generate_map_new()

# Khởi tạo Nhạc trưởng Bóng tối
quan_ly_bong_toi = darkness.DarknessManager(12, 12)

# Bộ đếm thời gian
SU_KIEN_1_GIAY = pygame.USEREVENT + 1
pygame.time.set_timer(SU_KIEN_1_GIAY, 1000)
tai_nguyen_go = 0

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
            
            # Thời gian vẫn đếm nhịp đều đặn
            if event.type == SU_KIEN_1_GIAY:
                tai_nguyen_go += 5
                
                # Bóng tối tính toán mỗi giây
                o_bi_nuot = quan_ly_bong_toi.update(1.0)
                if o_bi_nuot:
                    print(f"!!! Darkness swallowed cell {o_bi_nuot} !!!")
                    # (Tương lai: Cập nhật biến "darkness": True vào dữ liệu map mới tại đây)

        # GỌI HÀM VẼ MAP KIỂU MỚI CỦA BẠN CẬU
        map.draw_map(screen, ban_do_game, hinh_anh_map)
        
        # GIỮ NGUYÊN ĐỒ HỌA BÓNG TỐI CHE LẤP CỦA ANH EM MÌNH
        for cell_x, cell_y in quan_ly_bong_toi.darkened_cells:
            toa_do_x = cell_x * 48
            toa_do_y = cell_y * 48
            
            mang_den = pygame.Surface((48, 48))
            mang_den.set_alpha(200) 
            mang_den.fill((0, 0, 0)) 
            screen.blit(mang_den, (toa_do_x, toa_do_y))
            
        pygame.display.flip()
        
    clock.tick(60)