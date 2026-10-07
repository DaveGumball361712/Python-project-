import pygame as py
import random as r

# Hằng số kích thước
ROWS = 12
COLLUMS = 12
TILE = 48

class GameMap:
    def __init__(self):
        self.LOGO_CELLS = [(5,5), (5,6), (6,5), (6,6)]
        
        # Tải hình ảnh và lưu thành thuộc tính của Class
        self.forest = py.image.load("images/forest.png").convert_alpha()
        self.forest = py.transform.scale(self.forest, (TILE, TILE))
        
        self.fields = py.image.load("images/fields.png").convert_alpha()
        self.fields = py.transform.scale(self.fields, (TILE, TILE))
        
        self.rocks = py.image.load("images/Rocks.png").convert_alpha()
        self.rocks = py.transform.scale(self.rocks, (TILE, TILE))
        
        self.water = py.image.load("images/water.png").convert_alpha()
        self.water = py.transform.scale(self.water, (TILE, TILE))
        
        self.logo = py.image.load("images/logo-ptit.png").convert_alpha()
        self.logo = py.transform.scale(self.logo, (TILE, TILE))
        
        # Tạo mảng 2 chiều ngẫu nhiên
        self.game_map = [[r.choice([self.forest, self.fields, self.rocks, self.water]) for col in range(COLLUMS)] for row in range(ROWS)]
        
        # Đặt logo PTIT
        lr, lc = r.choice(self.LOGO_CELLS)
        self.game_map[lr][lc] = self.logo

    def draw(self, screen):
        # Hàm này chỉ làm nhiệm vụ vẽ, không có vòng lặp while nào cả
        for row in range(ROWS):
            for col in range(COLLUMS):
                # Tọa độ X là cột ngang, Y là hàng dọc
                x = col * TILE
                y = row * TILE
                screen.blit(self.game_map[row][col], (x, y))