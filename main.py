import pygame
import sys
import menu
import map
import darkness  # 1. Gọi file Bóng tối vào

pygame.init()
screen = pygame.display.set_mode((576, 576))
pygame.display.set_caption("Stop the Darkness - Đồ án Nhóm")

clock = pygame.time.Clock()

trang_thai = "MENU"
man_hinh_menu = menu.MainMenu(screen)
ban_do_game = map.GameMap()

# 2. Khởi tạo Nhạc trưởng Bóng tối (Bản đồ lưới kích thước 12x12)
quan_ly_bong_toi = darkness.DarknessManager(12, 12)

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
            
            # KHU VỰC THỜI GIAN CHẠY (Mỗi 1 giây)
            if event.type == SU_KIEN_1_GIAY:
                tai_nguyen_go += 5
                
                # 3. Bơm 1 giây vào cho Bóng tối tính toán
                o_bi_nuot = quan_ly_bong_toi.update(1.0)
                if o_bi_nuot:
                    print(f"!!! Darkness swallowed cell {o_bi_nuot} !!!")

        # KHU VỰC VẼ ĐỒ HỌA
        ban_do_game.draw(screen)
        
        # 4. Quét xem ô nào đã bị Bóng tối ăn thì lấy bút lông đen tô đè lên
        for cell_x, cell_y in quan_ly_bong_toi.darkened_cells:
            # Quy đổi tọa độ lưới sang pixel (1 ô = 48 pixel)
            toa_do_x = cell_x * 48
            toa_do_y = cell_y * 48
            
            # Tạo một tấm màng màu đen bán trong suốt (độ mờ 200/255)
            mang_den = pygame.Surface((48, 48))
            mang_den.set_alpha(200) 
            mang_den.fill((0, 0, 0)) 
            
            # In đè màng đen lên vị trí ô đất
            screen.blit(mang_den, (toa_do_x, toa_do_y))
            
        pygame.display.flip()
        
    clock.tick(60)