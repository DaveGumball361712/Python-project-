import pygame as py
import map
import darkness
from economy import EconomyManager
from ui import SidePanel

def run_game(screen):
    clock = py.time.Clock()
    
    # init data
    map_imgs = map.load_images()
    game_map = map.generate_map_new()
    eco_manager = EconomyManager()
    dark_manager = darkness.DarknessManager(map.COLLUMS, map.ROWS)
    
    # init tutorial
    from tutorial import Tutorial
    font_tutorial = py.font.SysFont('arial', 20, bold=True)
    tutorial_mgr = Tutorial(game_map, map.ROWS, map.COLLUMS, map.TILE, lambda r, c: False)
    
    is_paused = False
    time_multiplier = 1
    is_win = False
    running = True
    next_state = "MENU"
    
    # ui callbacks
    def action_quit():
        nonlocal running, next_state
        running = False
        next_state = "MENU"

    def action_pause():
        nonlocal is_paused, is_win
        if is_win: return # thang roi thi block nut pause
        is_paused = not is_paused
        ui_panel.toggle_pause_ui(is_paused)

    def action_speed():
        nonlocal time_multiplier
        if time_multiplier == 1:
            time_multiplier = 2
        elif time_multiplier == 2:
            time_multiplier = 4
        else:
            time_multiplier = 1
        ui_panel.toggle_speed_ui(time_multiplier)

    def action_refresh():
        nonlocal game_map, eco_manager, dark_manager, tutorial_mgr, is_win, is_paused
        game_map = map.generate_map_new()
        eco_manager = EconomyManager()
        dark_manager = darkness.DarknessManager(map.COLLUMS, map.ROWS)
        tutorial_mgr = Tutorial(game_map, map.ROWS, map.COLLUMS, map.TILE, lambda r, c: False)
        is_win = False
        is_paused = False

    # init ui panel
    ui_panel = SidePanel(map.MAP_WIDTH, map.UI_WIDTH, map.HEIGHT, action_quit, action_pause, action_speed,action_refresh, map.TILE, map.ROWS, map.COLLUMS)
    ui_panel.toggle_pause_ui(False)
    ui_panel.toggle_speed_ui(1)
    
    # game loop
    while running:
        dt = clock.tick(60) / 1000.0
        mouse_x, mouse_y = py.mouse.get_pos()
        
        # update logic
        if not is_paused:
            game_dt = dt * time_multiplier          # nhân hệ số tua nhanh

            eco_manager.update(game_dt, game_map)   # kinh tế tua theo tốc độ

            # Bóng tối chỉ lan sau khi tutorial kết thúc
            if not tutorial_mgr.active:
                o_bi_nuot = dark_manager.update(game_dt)   # <-- game_dt, KHÔNG phải dt
                if o_bi_nuot:
                    c_dark, r_dark = o_bi_nuot
                    if 0 <= r_dark < map.ROWS and 0 <= c_dark < map.COLLUMS:
                        game_map[r_dark][c_dark]["darkness"] = True
                    dark_manager.dong_bo_cap_do_thap(game_map)

            # Nháy mũi tên tutorial (chạy khi CÒN tutorial)
            if tutorial_mgr.active:
                tutorial_mgr.update(dt)
                
        # check lose
        if dark_manager.check_lose_condition() and len(dark_manager.darkened_cells) >= map.ROWS * map.COLLUMS:
            print("--- GAME OVER: Ban do da bi nuot sach! ---")
            return "MENU"
            
        # event loop
        for event in py.event.get():
            if event.type == py.QUIT:
                return "QUIT"
                
            ui_panel.handle_event(event)
            
            # handle click xay nha
            if event.type == py.MOUSEBUTTONDOWN and event.button == 1:
                col = event.pos[0] // map.TILE
                row = event.pos[1] // map.TILE
                if 0 <= row < map.ROWS and 0 <= col < map.COLLUMS:
                    if not is_paused:
                        # chan click neu bam sai o tutorial
                        if tutorial_mgr.active and not tutorial_mgr.allowed(row, col):
                            continue 
                        
                        tile = game_map[row][col]
                        before=(tile["type"],tile["building"],tile["level"])
                        
                        map.up(game_map, row, col, eco_manager)
                        dark_manager.dong_bo_cap_do_thap(game_map)
                        
                        # gui ket qua cho tutorial
                        if tutorial_mgr.active:
                            tile = game_map[row][col]
                            after=(tile["type"],tile["building"],tile["level"])
                            tutorial_mgr.on_action(row, col, before != after)
                        
                        # check win
                        if game_map[row][col]["type"] == "the_stone":
                            dark_manager.trigger_win_condition()
                            is_win = True
                            is_paused = True
                            ui_panel.toggle_pause_ui(True)
                            
        # render
        screen.fill((0, 0, 0))
        map.draw_map(screen, game_map, map_imgs)

        # render darkness
        for cell_x, cell_y in dark_manager.darkened_cells:
            dark_layer = py.Surface((map.TILE, map.TILE))
            dark_layer.set_alpha(200)
            dark_layer.set_alpha(255)
            dark_layer.fill((0, 0, 0))
            screen.blit(dark_layer, (cell_x * map.TILE, cell_y * map.TILE))
            
        ui_panel.draw(screen, mouse_x, mouse_y, eco_manager, map_imgs, is_paused, game_map)
        
        # render tutorial
        if tutorial_mgr.active:
            tutorial_mgr.draw(screen, font_tutorial)
        
        # render win ui
        if is_win:
            banner_height = 90
            pos_y = map.HEIGHT - banner_height
            
            # bg & border
            py.draw.rect(screen, (204, 201, 195), (0, pos_y, map.MAP_WIDTH, banner_height))
            py.draw.line(screen, (170, 155, 140), (0, pos_y), (map.MAP_WIDTH, pos_y), 3)
            
            font_win = py.font.SysFont('arial', 20, bold=True)
            font_sub = py.font.SysFont('arial', 16, italic=True)
            
            win_text = font_win.render("You saved the land from the darkness! Great job!", True, (40, 40, 40))
            sub_text = font_sub.render("Press the [X] button to return to the menu.", True, (100, 100, 100))
            
            pos_x_win = (map.MAP_WIDTH - win_text.get_width()) // 2
            pos_x_sub = (map.MAP_WIDTH - sub_text.get_width()) // 2
            
            screen.blit(win_text, (pos_x_win, pos_y + 20))
            screen.blit(sub_text, (pos_x_sub, pos_y + 55))
            
        py.display.flip()
        
    return next_state