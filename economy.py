import math

class EconomyManager:
    def __init__(self):
        self.inventory = {'W': 1000, 'S': 1000, 'M': 1000, 'T': 0}
        self.base_rate = {'W': 3, 'S': 3, 'M': 1, 'T': 1}
        self.production_per_sec = {'W': 0, 'S': 0, 'M': 0, 'T': 0}
        self.buy_count = {  
            "forest2" : 0, "forest3": 0, "forest4": 0,
        }
        self.COST_FORMULA = {
            # Địa hình
            "forest2": {"W": (2, 1)},
            "forest3": {"W": (5, 2.5)},
            "forest4": {"W": (8, 4), "S": (5, 2.5)},
            "rocks2": {"W": (8, 4)},
            "rocks3": {"W": (10, 5), "S": (3, 1)},
            "mushroom2": {"W": (15, 5), "S": (15, 5)},

            # Nhóm làng cơ bản (village & port_village dùng chung nhóm giá)
            "village_group": {"W": (5, 2.5)},
            "village2": {"W": (15, 5), "S": (5, 2.5)},
            "port_village2": {"W": (15, 5), "S": (10, 5)},

            # Làng khai thác Đá (Cấp 1 chỉ tốn Gỗ để mở khóa Đá)
            "mining_village": {"W": (5, 2.5)},
            "mining_village2": {"W": (10, 5), "S": (5, 2.5)},

            # Làng trên cây
            "treetop_village": {"W": (15, 5)},
            "treetop_village2": {"W": (30, 10), "S": (15, 5)},

            # Làng phép thuật (Cấp 1 chỉ tốn Gỗ + Đá để mở khóa Mana)
            "magical_village": {"W": (20, 5), "S": (10, 2.5)},
            "magical_village2": {"W": (40, 10), "S": (20, 5), "M": (10, 2.5)},

            "magical_port_village": {"W": (25, 5), "S": (15, 5)},
            "magical_port_village2": {"W": (50, 10), "S": (30, 5), "M": (15, 5)},

            # Tháp ánh sáng
            "tower_of_light": {"W": (50, 0), "S": (50, 0), "M": (20, 0)},
            "tower_of_light2": {"W": (100, 0), "S": (100, 0), "M": (50, 0), "T": (20, 0)},

            # CÔNG TRÌNH CHIẾN THẮNG
            "the_stone": {"S": (100, 0), "M": (100, 0)},
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
        key = self.price_group.get(name, name)
        if key in self.COST_FORMULA:  # Kiểm tra theo key thay vì name
            count = self.buy_count.get(key, 0)
            cost = {}
            for res, (base, step) in self.COST_FORMULA[key].items():
                cost[res] = math.floor(base + step * count)
            return cost
        print("Chưa có giá cho:", key)
        return {}
    
    def try_buy(self, name):    
        key = self.price_group.get(name, name)
        cost = self.get_cost(name)
        if not cost:  # Chặn không cho xây nếu chưa khai báo giá
            return False
        if self.spend(cost):
            self.buy_count[key] = self.buy_count.get(key, 0) + 1 
            return True
        return False
    
    # Hàm được gọi liên tục để tính toán thời gian thực
    def update(self, dt, game_map):
        # 1. Reset về 0 ở ĐẦU hàm trước khi quét map
        self.production_per_sec = {'W': 0.0, 'S': 0.0, 'M': 0.0, 'T': 0.0}
        
        # 2. Quét toàn bộ map để tính tổng sản lượng hiện tại/giây
        for r in range(len(game_map)):
            for c in range(len(game_map[0])):
                tile = game_map[r][c]
                res_type = self.get_res_type(tile)
                if res_type != 'E':
                    prod = self.one_production(r, c, game_map)
                    self.production_per_sec[res_type] += prod
                    # Cộng tài nguyên thực tế theo thời gian trôi qua (dt)
                    self.inventory[res_type] += prod * (dt/60.0)