import pygame as p

# THIẾT LẬP BUTTON
class Button(p.sprite.Sprite):
    def __init__(self, x, y, width, height, text, action = None, corner_radius = 15, border_width=5):
        super().__init__()

        # Khởi tạo biến có thuộc tính đối tượng
        self.action = action
        self.width = width
        self.height = height
        self.text = text
        self.border_width = border_width
        self.corner_radius = corner_radius
        # Màu của Button
        self.border_color = (140, 107, 83)
        self.bg_color = (204,201,195)
        self.hover_color = (235, 233, 228)
        self.is_hovered = False

        self.image = p.Surface((width,height))
        self.rect = self.image.get_rect(center = (x,y))
        self._render_Button()

    # Function tạo Button
    def _render_Button(self):
        current_bg = self.hover_color if self.is_hovered else self.bg_color
        p.draw.rect(self.image, current_bg, self.image.get_rect(), border_radius= self.corner_radius)
        p.draw.rect(self.image, self.border_color, self.image.get_rect(), width= self.border_width, border_radius=self.corner_radius)

    # Định dạng text
        font = p.font.Font(None, 36)
        text_surf = font.render(self.text, True, (0,0,0))
        text_rect = text_surf.get_rect(center=(self.width//2, self.height//2))
        self.image.blit(text_surf,text_rect)

    # Function xác định vị trí chuột + check hover
    def update(self):
        mouse_pos = p.mouse.get_pos()
        was_hoverred = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.is_hovered != was_hoverred:
            self._render_Button()

    # Funciton bắt event chuột
    def handle_event(self, event):
        if event.type == p.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action is not None:
                    self.action()

class MainMenu:
    def __init__(self,screen):
        self.screen= screen
        self.ui_group = p.sprite.Group()

        # biến để theo dõi sự kiện tiếp theo của menu
        self.next_state = None

        center_x = WIDTH // 2
        center_y = HEIGHT // 2
        
        start_btn = Button(center_x, center_y-50, 200, 60, "Start",action=self.StartGame)
        quit_btn = Button(center_x, center_y+50, 200, 60, "Quit",action=self.QuitGame)
        self.ui_group.add(start_btn, quit_btn)

    def StartGame(self):
        self.next_state = "PLAYING"
    def QuitGame(self):
        self.next_state = "QUIT"

    def run(self):
        self.next_state = None
        running = True

        while running:
            for event in p.event.get():
                if event.type == p.QUIT:
                    return "QUIT"
                for ui_element in self.ui_group:
                    ui_element.handle_event(event)

            if self.next_state is not None:
                return self.next_state

            self.ui_group.update()
            self.ui_group.draw(self.screen)
            p.display.flip()


# --- CHẠY THỬ CỤC BỘ ---
if __name__ == "__main__":
    import sys

    #thông số window
    ROWS = 12
    COLLUMS = 8
    TILE = 48
    WIDTH = COLLUMS * TILE
    HEIGHT = ROWS * TILE

    p.init()
    test_screen = p.display.set_mode((WIDTH,HEIGHT))

    test_menu = MainMenu(test_screen)

    result_state = test_menu.run()

    p.quit()
    sys.exit()