import pygame as py
from menu import Button

class SidePanel:
    def __init__(self, map_width, ui_width, height, action_quit, action_pause, action_speed, action_refresh, tile_size, rows, cols):
        self.map_width = map_width
        self.ui_width = ui_width
        self.height = height

        self.tile_size = tile_size
        self.rows = rows
        self.cols = cols
        
        # Khởi tạo Font
        self.font_small = py.font.Font(None, 24)
        self.font_main = py.font.Font(None, 28)
        
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
        
        # Quit Button
        self.btn_quit = Button(x=self.map_width + 220, y=556, width=30, height=30, text="x", action=action_quit)

        # Pause Button 
        self.btn_pause = Button(x=self.map_width + 180, y=556, width=30, height=30, text="II", action=action_pause)

        # Speed Button
        self.btn_speed = Button(x=self.map_width + 140, y=556, width=30, height=30, text="1x", action=action_speed)

        # Refresh Button
        self.btn_refresh = Button(x=self.map_width + 100, y=556, width=30, height=30, text="R", action=action_refresh)

    def _draw_info_section(self, screen, x, y, title, data_dict, images):
        title_surf = self.font_main.render(title, True, (20, 20, 20))
        screen.blit(title_surf, (x, y))
        y += 25
        
        # Vẽ Icon to, Tên và Level
        icon_name = data_dict.get("icon", "forest")
        screen.blit(images[icon_name], (x, y))
        
        name_surf = self.font_main.render(data_dict.get("name", "Unknown"), True, (20, 20, 20))
        screen.blit(name_surf, (x + 55, y))
        
        level_surf = self.font_small.render(f"Level {data_dict.get('level', 1)}", True, (80, 80, 80))
        screen.blit(level_surf, (x + 55, y + 25))
        y += 55

        res_to_icon = {'W': 'icon_wood', 'S': 'icon_stone', 'M': 'icon_magic', 'T': 'icon_tech'}
        
        # Vẽ Cost 
        cost = data_dict.get("cost")
        if cost:
            screen.blit(self.font_main.render("Cost:", True, (20, 20, 20)), (x, y))
            y += 25
            cx = x
            for res, amount in cost.items():
                icon_name = res_to_icon.get(res, "icon_wood") 
                icon_res = images[icon_name] 
                
                screen.blit(icon_res, (cx, y))
                cost_val = self.font_main.render(str(amount), True, (100, 80, 60))
                screen.blit(cost_val, (cx + 25, y))
                cx += 60
            y += 30

        # Vẽ Production 
        prod = data_dict.get("production")
        if prod:
            screen.blit(self.font_main.render("Production per minute:", True, (20, 20, 20)), (x, y))
            y += 25
            cx = x
            for res, amount in prod.items():
                icon_name = res_to_icon.get(res, "icon_wood")
                screen.blit(images[icon_name], (cx, y))
                
                prod_val = self.font_main.render(f"{amount:.1f}", True, (40, 140, 40))
                screen.blit(prod_val, (cx + 25, y))
                cx += 60
            y += 30

        # Vẽ Boost 
        boosts = data_dict.get("boosts")
        if boosts:
            screen.blit(self.font_main.render("Boost to adjacent:", True, (20, 20, 20)), (x, y))
            y += 25
            cx = x
            for res, percent in boosts.items():
                icon_name = res_to_icon.get(res, "icon_wood")
                screen.blit(images[icon_name], (cx, y))
                
                boost_val = self.font_main.render(f"{percent}%", True, (60, 60, 60))
                screen.blit(boost_val, (cx + 25, y))
                cx += 60
            y += 30
            
        return y

    def _extract_name_and_level(self, key):
        """Hàm phụ tự động tách tên và cấp độ: 'forest2' -> ('Forest', 2), 'forest' -> ('Forest', 1)"""
        base_key = key.rstrip("0123456789")
        lvl_str = key[len(base_key):]
        level = int(lvl_str) if lvl_str else 1
        display_name = base_key.replace("_", " ").title()
        return base_key, display_name, level

    def _get_tile_info(self, mouse_x, mouse_y, game_map, eco):
        if mouse_x >= self.map_width or mouse_y >= self.height:
            return None
            
        col = mouse_x // self.tile_size
        row = mouse_y // self.tile_size
        
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return None

        from map import UPGRADE, building_for_tile

        tile = game_map[row][col]

        # XÁC ĐỊNH ĐỐI TƯỢNG HIỆN TẠI 
        has_building = tile["building"] is not None
        current_key = tile["building"] if has_building else tile["type"]
        base_key, display_name, current_level = self._extract_name_and_level(current_key)

        current_data = {
            "name": display_name,
            "level": current_level,
            "icon": current_key,
            "boosts": eco.get_boost(current_key)
        }

        # Nếu ô hiện tại đang sản xuất tài nguyên 
        prod = {}
        for res, val in eco.tile_production(row, col, game_map).items():
            if val > 0:
                prod[res] = round(val, 2)
        if prod:
            current_data["production"] = prod

        # XÁC ĐỊNH BƯỚC NÂNG CẤP TIẾP THEO 
        next_key = None
        is_upgrade = True
        next_target_is_building = False

        if not tile.get("darkness", False):
            if has_building:
                # Nếu đã có nhà -> Tìm cấp tiếp theo của nhà 
                next_key = UPGRADE.get(tile["building"])
                next_target_is_building = True
            else:
                # Nếu chưa có nhà -> Kiểm tra xem ô này có xây được nhà mới không
                possible_building = building_for_tile(game_map, row, col)
                if possible_building is not None:
                    next_key = possible_building
                    is_upgrade = False
                    next_target_is_building = True
                else:
                    # Nếu không xây được nhà -> Kiểm tra nâng cấp địa hình 
                    next_key = UPGRADE.get(tile["type"])
                    next_target_is_building = False

        # ĐÓNG GÓI DỮ LIỆU NÂNG CẤP 
        upgrade_data = None
        if next_key is not None:
            next_base, next_name, next_level = self._extract_name_and_level(next_key)
            
            # Giả lập nâng cấp tạm thời trên ô đất để nhờ eco tính chính xác sản lượng 
            old_type, old_building, old_level = tile["type"], tile["building"], tile["level"]
            if next_target_is_building:
                tile["building"] = next_key
                tile["level"] = 1 if old_building is None else old_level + 1
            else:
                tile["type"] = next_key
                tile["level"] = old_level + 1

            next_prod = {}
            for res, val in eco.tile_production(row, col, game_map).items():
                if val > 0:
                    next_prod[res] = round(val, 2)

            # Trả lại nguyên trạng cho ô đất sau khi tính xong
            tile["type"], tile["building"], tile["level"] = old_type, old_building, old_level

            upgrade_data = {
                "is_upgrade": is_upgrade,
                "name": next_name,
                "level": next_level,
                "icon": next_key,
                "cost": eco.get_cost(next_key),
                "production": next_prod,
                "boosts": eco.get_boost(next_key)
            }

        hover_info = {"current": current_data}
        if upgrade_data:
            hover_info["upgrade"] = upgrade_data
            
        return hover_info

    # HÀM CẬP NHẬT GIAO DIỆN NÚT SPEED
    def toggle_speed_ui(self, current_multiplier):
        self.btn_speed.text = f"{current_multiplier}x"
        self.btn_speed._render_Button()

    # Hàm thay đổi giao diện nút Pause khi bấm
    def toggle_pause_ui(self, is_paused):
        # Nếu đang Pause thì hiện nút Play ( > ), ngược lại hiện Pause ( || )
        self.btn_pause.text = "►" if is_paused else "II"
        self.btn_pause._render_Button() # Gọi lại hàm render của class Button để cập nhật chữ

    # Hàm phụ hỗ trợ vẽ chữ tài nguyên 
    def _draw_resource_text(self, surface, x, y, width, amount, increment, icon_img):
        surface.blit(icon_img, (x + 5, y + 8))
        amt_text = self.font_main.render(str(int(amount)), True, (50, 50, 50))
        surface.blit(amt_text, (x + 35, y + 10))
        inc_text = self.font_small.render(f"+{increment:g}", True, (100, 100, 100))
        inc_x = x + width - inc_text.get_width() - 5 
        surface.blit(inc_text, (inc_x, y + 20))

    # Hàm bắt sự kiện UI
    def handle_event(self, event):
        self.btn_quit.handle_event(event)
        self.btn_pause.handle_event(event)
        self.btn_speed.handle_event(event)
        self.btn_refresh.handle_event(event)

    # Hàm để vẽ toàn bộ UI ra màn hình
    def draw(self, screen, mouse_x, mouse_y, eco, images, is_paused, game_map):
        # LAYER 1 
        screen.blit(self.resource_surface, (self.map_width, 0))
        self._draw_resource_text(screen, self.map_width, 0, self.col_width, 
                    amount=int(eco.inventory['W']), increment=round(eco.production_per_sec['W'], 1), icon_img=images["icon_wood"])
        self._draw_resource_text(screen, self.map_width + self.col_width, 0, self.col_width, 
                    amount=int(eco.inventory['S']), increment=round(eco.production_per_sec['S'], 1), icon_img=images["icon_stone"])
        self._draw_resource_text(screen, self.map_width, self.row_height, self.col_width, 
                    amount=int(eco.inventory['M']), increment=round(eco.production_per_sec['M'], 1), icon_img=images["icon_magic"])
        self._draw_resource_text(screen, self.map_width + self.col_width, self.row_height, self.col_width, 
                    amount=int(eco.inventory['T']), increment=round(eco.production_per_sec['T'], 1), icon_img=images["icon_tech"])

        # VẼ LAYER 2 
        screen.blit(self.info_surface, (self.map_width, 80))

        # Tooltip khi trỏ chuột vào thanh tài nguyên 
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
                line2 = f"+{res_rate:.1f} per minute"
                text1 = self.font_small.render(line1, True, (60, 60, 60))
                text2 = self.font_small.render(line2, True, (60, 60, 60))
                screen.blit(text1, (self.map_width + 15, 100))
                screen.blit(text2, (self.map_width + 15, 130))

        # Tooltip khi trỏ chuột vào bản đồ 
        elif mouse_x < self.map_width and mouse_y < self.height:
            # GỌI HÀM LẤY DATA TẠI ĐÂY
            hover_info = self._get_tile_info(mouse_x, mouse_y, game_map, eco)
            
            if hover_info:
                current_y = 90
                start_x = self.map_width + 10
                
                if "current" in hover_info:
                    current_y = self._draw_info_section(screen, start_x, current_y, "This area:", hover_info["current"], images)
                
                if "upgrade" in hover_info:
                    py.draw.line(screen, (170, 155, 140), (self.map_width, current_y), (self.map_width + self.ui_width, current_y), 2)
                    current_y += 10
                    title = "Click to upgrade to:" if hover_info["upgrade"].get("is_upgrade") else "Next upgrade:"
                    self._draw_info_section(screen, start_x, current_y, title, hover_info["upgrade"], images)

    
        self.btn_quit.update()
        screen.blit(self.btn_quit.image, self.btn_quit.rect)
        
        self.btn_pause.update()
        screen.blit(self.btn_pause.image, self.btn_pause.rect)

        self.btn_speed.update()
        screen.blit(self.btn_speed.image, self.btn_speed.rect)

        self.btn_refresh.update()
        screen.blit(self.btn_refresh.image, self.btn_refresh.rect)