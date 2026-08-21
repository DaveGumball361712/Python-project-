class DarknessManager:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        
        # 1. Khởi tạo bằng một List rỗng (chỉ cần dùng cặp ngoặc vuông)
        self.path_queue = [] 
        
        self.current_tick_rate = 0.1 
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
                # 2. Lệnh append() nhét thêm phần tử vào cuối List
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
            return
        
        self.timer += delta_time
        if self.timer >= self.current_tick_rate:
            self.timer -= self.current_tick_rate
            
            # 3. Lệnh pop(0) lấy phần tử ở vị trí đầu tiên (index 0) ra khỏi List
            x, y = self.path_queue.pop(0)
            self.darkened_cells.add((x, y))