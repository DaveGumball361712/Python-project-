import pygame
import sys
import menu
import map

pygame.init()
screen = pygame.display.set_mode((576, 576))
pygame.display.set_caption("Stop the Darkness - Đồ án Nhóm")

# THÊM LẠI ĐỒNG HỒ FPS ĐỂ GAME KHÔNG BỊ TREO
clock = pygame.time.Clock()

trang_thai = "MENU"
man_hinh_menu = menu.MainMenu(screen)
ban_do_game = map.GameMap()

# TẠO ĐỒNG HỒ BÁO THỨC CỘNG TÀI NGUYÊN
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
            
            # Lắng nghe tiếng chuông báo thức
            if event.type == SU_KIEN_1_GIAY:
                tai_nguyen_go += 5
                print(f"Tick tock... 1 second passed! Current wood: {tai_nguyen_go}")

        ban_do_game.draw(screen)
        pygame.display.flip()
        
    # CHỐT CHẶN TỐC ĐỘ: Bắt buộc phải có để máy không bị văng
    clock.tick(60)