import pygame as py
from menu import Button

class SidePanel:
    def __init__(self, map_width, ui_width, height, action_quit):
        self.map_width = map_width
        self.ui_width = ui_width
        self.height = height
        
        # Khởi tạo Font
        self.font_small = py.font.Font(None, 24)
        self.font_main = py.font.Font(None, 32)
        
        # Kích thước khu vực
        self.res_height = 80
        self.col_width = self.ui_width // 2 
        self.row_height = self.res_height // 2

        # Tạo Surface cho Layer 1 (Tài nguyên)
        self.resource_surface = py.Surface((self.ui_width, self.res_height))
        self.resource_surface.fill((204, 201, 195))
        line_color = (170, 155, 140)
        py.draw.line(self.resource_surface, line_color, (0, self.row_height), (self.ui_width, self.row_height), 3)
        py.draw.line(self.resource_surface, line_color, (self.col_width, 0), (self.col_width, self.res_height), 2)
        py.draw.line(self.resource_surface, line_color, (0, self.res_height-2), (self.ui_width, self.res_height-2), 3)

        # Tạo Surface cho Layer 2 (Thông tin)
        self.info_surface = py.Surface((self.ui_width, self.height))
        self.info_surface.fill((204, 201, 195))
        
        # Khởi tạo nút Quit
        self.btn_quit = Button(x=self.map_width + 220, y=556, width=30, height=30, text="x", action=action_quit)

    # Hàm phụ hỗ trợ vẽ chữ tài nguyên 
    def _draw_resource_text(self, surface, x, y, width, amount, increment, icon_img):
        surface.blit(icon_img, (x + 5, y + 8))
        amt_text = self.font_main.render(str(amount), True, (50, 50, 50))
        surface.blit(amt_text, (x + 35, y + 10))
        inc_text = self.font_small.render(f"+{increment}", True, (100, 100, 100))
        inc_x = x + width - inc_text.get_width() - 5 
        surface.blit(inc_text, (inc_x, y + 20))

    # Hàm bắt sự kiện UI
    def handle_event(self, event):
        self.btn_quit.handle_event(event)

    # Hàm để vẽ toàn bộ UI ra màn hình
    def draw(self, screen, mouse_x, mouse_y, eco, images):
        # 1. Vẽ Layer 1 (Resource)
        screen.blit(self.resource_surface, (self.map_width, 0))
        
        self._draw_resource_text(screen, self.map_width, 0, self.col_width, 
                    amount=eco.inventory['W'], increment=eco.production_per_sec['W'], icon_img=images["icon_wood"])
        self._draw_resource_text(screen, self.map_width + self.col_width, 0, self.col_width, 
                    amount=eco.inventory['S'], increment=eco.production_per_sec['S'], icon_img=images["icon_stone"])
        self._draw_resource_text(screen, self.map_width, self.row_height, self.col_width, 
                    amount=eco.inventory['M'], increment=eco.production_per_sec['M'], icon_img=images["icon_magic"])
        self._draw_resource_text(screen, self.map_width + self.col_width, self.row_height, self.col_width, 
                    amount=eco.inventory['T'], increment=eco.production_per_sec['T'], icon_img=images["icon_tech"])

        # Layer 2 (Information)
        screen.blit(self.info_surface, (self.map_width, 80))

        if mouse_x >= self.map_width and mouse_y < 80:
            col_idx = (mouse_x - self.map_width) // 125
            row_idx = mouse_y // 40

            resource_data = {
                (0, 0): ["Wood", int(eco.inventory['W']), eco.production_per_sec['W']],
                (0, 1): ["Stone", int(eco.inventory['S']), eco.production_per_sec['S']],
                (1, 0): ["Mana", int(eco.inventory['M']), eco.production_per_sec['M']],
                (1, 1): ["Tech", int(eco.inventory['T']), eco.production_per_sec['T']]
            }

            current_res = resource_data.get((row_idx, col_idx))
            if current_res:
                res_name, res_amount, res_rate = current_res
                line1 = f"{res_name}: {res_amount}"
                line2 = f"+{res_rate:.1f} per second"

                text1 = self.font_small.render(line1, True, (60, 60, 60))
                text2 = self.font_small.render(line2, True, (60, 60, 60))

                screen.blit(text1, (self.map_width + 15, 100))
                screen.blit(text2, (self.map_width + 15, 130))

        # Vẽ nút bấm
        self.btn_quit.update()
        screen.blit(self.btn_quit.image, self.btn_quit.rect)