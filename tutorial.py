import random as r
import pygame as py

class Tutorial:
    def __init__(self, game_map, rows, cols, tile, is_treetop_spot):
        self.rows, self.cols, self.tile = rows, cols, tile
        self.active = True
        self.step = 1
        self.blink_timer = 0.0
        self.blink_on = True

        forests = [(row, col)
                    for row in range(rows) for col in range(cols)
                    if game_map[row][col]["type"]=="forest"
                    and game_map[row][col]["building"] is None
                    and not is_treetop_spot(row, col)]
        self.target = r.choice(forests) if forests else None

        self.messages = {
            1: "Darkness is trying to take over this land, but you can still stop it! Let's start by producing some wood. Click on the forest to upgrade it.",
            2: "The available upgrade is based on the four adjacent areas, so be sure to look around and experiment a bit.Upgrade anything to start. Good luck!",
        }

    def allowed(self, row, col):
        if self.step == 1:
            return (row, col) == self.target
        return True   

    def on_action(self, row, col, changed):
        if not changed:
            return
        if self.step == 1 and (row, col) == self.target:
            self.step = 2
        elif self.step == 2:
            self.active = False   

    def update(self, dt):
        self.blink_timer += dt
        if self.blink_timer >= 0.2:     
            self.blink_timer = 0.0
            self.blink_on = not self.blink_on

    def wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines = []
        current = ""
        for w in words:
            test = w if current == "" else current + " " + w
            if font.size(test)[0] <= max_width:   
                current = test
            else:
                if current:
                    lines.append(current)          
                current = w                        
        if current:
            lines.append(current)
        return lines

    def draw(self, screen, font):
        if self.step == 1 and self.target:
            row, col = self.target
            rect = py.Rect(col*self.tile, row*self.tile, self.tile, self.tile)
            py.draw.rect(screen, (102,178,255), rect, 4)          
            if self.blink_on:                                   
                y = col*self.tile + self.tile//2
                x = row*self.tile
                py.draw.polygon(screen, (102,178,255),
                                [(y-10, x-20), (y+10, x-20), (y, x-4)])
        msg = self.messages.get(self.step)
        if msg:
            map_width = self.cols * self.tile
            padding = 10
            line_height = font.get_linesize()
            lines = self.wrap_text(msg, font, map_width - 2*padding)   
            banner_height = len(lines) * line_height + 2*padding
            x0 = self.rows*self.tile - banner_height
            py.draw.rect(screen, (204, 201, 195), (0, x0, map_width, banner_height))
            py.draw.line(screen, (170, 155, 140), (0, x0), (map_width, x0), 3)
            for i, line in enumerate(lines):
                text = font.render(line, True, (40, 40, 40))
                screen.blit(text, (padding, x0 + padding + i*line_height))


