import math

class EconomyManager:
    def __init__(self):
        self.inventory = {'W': 12, 'S': 0, 'M': 0, 'T': 0}
        self.base_rate = {'W': 3, 'S': 3, 'M': 1, 'T': 1}
        self.production_per_minute = {'W': 0, 'S': 0, 'M': 0, 'T': 0}
        self.buy_count = {  
            "forest2" : 0, "forest3": 0, "forest4": 0,
        }
        self.COST_FORMULA = {
            "forest2": {"W": (2, 1)},
            "forest3": {"W": (5, 2.5)},
            "forest4": {"W": (8, 4), "S": (5, 2.5)},
            "rocks2": {"W": (8,4)},
            "rocks3": {"W": (10, 5), "S": {3,1}},

            "mining_village": {"W": (5, 2.5), "S" :(2,1)},
            "mining_village2": {"W: (10, 5), (5, 2.5)"},
            
            "village_group": {"W": (5, 2.5)},
            "magical_village": {"W": (5, 0), "M": (1, 0)},
        }
        self.price_group = {
            "village": "village_group",
            "port_village": "village_group",
        }

        self.timer = 0.0
        self.tick_rate = 1.0 
        
        self.building_to_res = {
            "village": "W", "village2": "W",
            "treetop_village": "W", "treetop_village2": "W",
            "port_village": "W", "port_village2": "W",
            "mining_village": "S", "mining_village2": "S",
            "magical_village": "M", "magical_village2": "M",
            "magical_port_village": "M", "magical_port_village2": "M",
            "tower_of_light": "T", "tower_of_light2": "T"
        }

    # Hàm lấy mã tài nguyên từ ô đất trên map
    def get_res_type(self, tile):
        b = tile["building"]
        if b is not None and b in self.building_to_res:
            return self.building_to_res[b]
            
        # Nếu không có công trình, xét đến Địa hình đã nâng cấp
        t = tile["type"]
        # Chỉ những địa hình cấp 2 trở lên mới trả về loại tài nguyên
        if t in ["forest2", "forest3", "forest4"]: return "W"
        if t in ["rocks2", "rocks3"]: return "S"
        if t in ["mushroom2"]: return "M"
        
        # Địa hình mặc định không sinh ra gì cả
        return "E"

    def count_adjacent(self, x, y, grid):
        rows, cols = len(grid), len(grid[0])
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        count = 0
        
        # Lấy loại tài nguyên của ô trung tâm đang xét (Từ công trình hoặc từ địa hình cấp 2)
        current_res = self.get_res_type(grid[x][y])
        if current_res == "E": 
            return 0
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                neighbor_tile = grid[nx][ny]
                
                # Mỏ đá đứng cạnh forest2, thì forest2 vẫn được tính là "forest" để buff cho gỗ, không buff cho đá.
                neighbor_type = neighbor_tile["type"].rstrip("0123456789")
                
                # Luật Buff
                if current_res == "W" and neighbor_type == "forest": count += 1
                elif current_res == "S" and neighbor_type == "rocks": count += 1
                elif current_res == "M" and neighbor_type == "mushroom": count += 1
                
        return count

    def one_production(self, x, y, grid):
        current_key = self.get_res_type(grid[x][y])
        if current_key == "E":
            return 0
            
        neighbor = self.count_adjacent(x, y, grid)
        
        # Nếu muốn level của Công trình ảnh hưởng đến số lượng tài nguyên:
        # level = grid[x][y].get("level", 1)
        # return (self.base_rate[current_key] * level) * (1 + 0.25 * neighbor)
        
        # Tạm thời giữ 
        return self.base_rate[current_key] * (1 + 0.25 * neighbor)

    def total_production(self, grid):
        rows = len(grid)
        cols = len(grid[0])
        total = {'W': 0, 'S': 0, 'M': 0, 'T': 0}
        for x in range(rows):
            for y in range(cols):
                current_key = self.get_res_type(grid[x][y])
                if current_key != "E":
                    total[current_key] += self.one_production(x, y, grid)
        return total
    
    # 4 hàm kiểm tra điều kiện, lấy giá và cho phép xây
    def can_afford(self, cost):
        for res, amount in cost.items():       
            if self.inventory[res] < amount:
                return False
        return True

    def spend(self, cost):
        if not self.can_afford(cost):
            return False
        for res, amount in cost.items():
            self.inventory[res] -= amount
        return True

    def get_cost(self, name):
        key = self.price_group.get(name,name)
        if name in self.COST_FORMULA:
            count = self.buy_count.get(key,0)
            cost = {}
            for res, (base, step) in self.COST_FORMULA[key].items():
                cost[res] = math.floor(base + step * count)
            return cost
        print("Chưa có giá cho:", key)
        return {}
    
    def try_buy(self, name):    
        key = self.price_group.get(name,name)
        cost = self.get_cost(key)
        if self.spend(cost):
            self.buy_count[key] = self.buy_count.get(key, 0) + 1 
            return True
        return False
    
    # Hàm được gọi liên tục để tính toán thời gian thực
    def update(self, dt, grid):
        self.timer += dt
        if self.timer >= self.tick_rate:
            self.timer -= self.tick_rate
            self.production_per_minute = self.total_production(grid)
            for res in self.production_per_minute:
                self.inventory[res] += self.production_per_minute[res]/60