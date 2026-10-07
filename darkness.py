class DarknessManager:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.path_queue = [] 
        self.current_tick_rate = 6.0 # 6 giây lan 1 ô để dễ test
        self.timer = 0.0
        self.darkened_cells = set() 
        
        self._generate_spiral_path()

    def _generate_spiral_path(self):
        top = 0
        bottom = self.rows - 1
        left = 0
        right = self.cols - 1
        total_cells = self.cols * self.rows
        
        while len(self.path_queue) < total_cells:
            for x in range(left, right + 1):
                self.path_queue.append((x, bottom))
            bottom -= 1
            if len(self.path_queue) >= total_cells: break
            
            for y in range(bottom, top - 1, -1):
                self.path_queue.append((right, y))
            right -= 1
            if len(self.path_queue) >= total_cells: break
            
            for x in range(right, left - 1, -1):
                self.path_queue.append((x, top))
            top += 1
            if len(self.path_queue) >= total_cells: break
            
            for y in range(top, bottom + 1):
                self.path_queue.append((left, y))
            left += 1

    def update(self, delta_time):
        if not self.path_queue:
            return None
        
        self.timer += delta_time
        if self.timer >= self.current_tick_rate:
            self.timer -= self.current_tick_rate
            
            x, y = self.path_queue.pop(0)
            self.darkened_cells.add((x, y))
            return (x, y) # Trả về tọa độ vừa bị nuốt
        return None
    def set_resistance_level(self, tower_level):
        """Thay đổi tốc độ loang dựa trên cấp độ của Tower of Light"""
        if tower_level == 1:
            self.current_tick_rate = 9.0  # 6s + 3s
        elif tower_level == 2:
            self.current_tick_rate = 12.0 # 6s + 3s + 3s
        else:
            self.current_tick_rate = 6.0  # Trở lại 6s nếu không có trụ hoặc trụ bị phá
    def check_lose_condition(self):
        """Báo Game Over khi bóng tối đã nuốt trọn toàn bộ ô trên bản đồ"""
        # Trả về True nếu danh sách đường đi đã cạn kiệt
        if len(self.path_queue) == 0:
            return True
        return False
        
    def trigger_win_condition(self):
        """Được gọi khi người chơi xây thành công công trình chiến thắng (The Stone)"""
        # Xóa sạch đường đi còn lại để đóng băng hoàn toàn bóng tối
        self.path_queue.clear()
# --- PHẦN TEST ĐỘC LẬP
if __name__ == "__main__":
    import time

    print("--- KHỞI TẠO BÓNG TỐI (Map 12x12) ---")
    manager = DarknessManager(12, 12)
    
    last_time = time.time()
    cells_swallowed = 0
    
    # Mẹo: Tua nhanh thời gian gấp 10 lần để cậu không phải ngồi đợi quá lâu
    # (6s trong game sẽ chỉ tốn 0.6s ngoài đời thực)
    TIME_MULTIPLIER = 3

    while True:
        current_time = time.time()
        # Nhân dt với hệ số tua nhanh
        dt = (current_time - last_time) * TIME_MULTIPLIER
        last_time = current_time
        
        # Gọi thuật toán
        swallowed_pos = manager.update(dt)
        
        if swallowed_pos:
            cells_swallowed += 1
            print(f"[{cells_swallowed}] Bóng tối nuốt ô {swallowed_pos} | Đang chờ: {manager.current_tick_rate}s/ô")
            
            # --- GIẢ LẬP SỰ KIỆN ---
            
            # 1. Sau khi nuốt 3 ô, giả lập người chơi xây Tower of Light Lv 1
            if cells_swallowed == 3:
                print("\n>>> SỰ KIỆN: Người chơi xây Tower of Light Lv 1!")
                manager.set_resistance_level(1)

            # 2. Sau khi nuốt 6 ô, giả lập nâng cấp lên Lv 2
            if cells_swallowed == 6:
                print("\n>>> SỰ KIỆN: Người chơi nâng cấp Tower of Light Lv 2!")
                manager.set_resistance_level(2)
                
            # 3. Sau khi nuốt 10 ô, giả lập xây xong The Stone (Điều kiện Thắng)
            if cells_swallowed == 10:
                print("\n>>> SỰ KIỆN: Người chơi xây xong THE STONE!")
                manager.trigger_win_condition()
        
        # --- KIỂM TRA THẮNG / THUA ---
        
        if manager.check_lose_condition():
            print("\n--- GAME OVER: Bản đồ đã bị nuốt sạch! ---")
            break
            
        # Nếu đường đi rỗng (do gọi hàm trigger_win_condition) mà chưa ăn hết map
        if not manager.path_queue and cells_swallowed < 144:
            print("\n--- YOU WIN: Bóng tối đã bị phong ấn hoàn toàn! ---")
            break
            
        time.sleep(0.01) # Ngủ 1 chút để không bị treo máy