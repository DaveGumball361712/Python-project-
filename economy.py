import math

class EconomyManager:
    def __init__(self):
        self.inventory = {'W': 1211, 'S': 1110, 'M': 1110, 'T': 11110}
        self.base_rate = {'W': 3, 'S': 3, 'M': 1, 'T': 1}
        self.production_per_sec = {'W': 0, 'S': 0, 'M': 0, 'T': 0}
        self.buy_count = {  
            "forest2" : 0, "forest3": 0, "forest4": 0,
        }
        self.COST_FORMULA = {
            "forest2": {"W": (2, 1)},
            "forest3": {"W": (5, 2.5)},
            "forest4": {"W": (8, 4), "S": (5, 2.5)},
            "rocks2": {"W": (8,4)},
            "rocks3": {"W": (10, 5), "S": {3,1}},
            "treetop_village": {"W": (15, 7.5)},
            "treetop_village2": {"W": (30, 10),"S":(15,5)},
            "mushroom2": {"W": (6,3)},

            "mining_village": {"W": (5, 2.5), "S" :(2,1)},
            "mining_village2": {"W": (10, 5), "S": (5, 2.5)},

            "village_group": {"W": (5, 2.5)},
            "village_group2": {"W": (10, 5), "S": (4,2)},
            
            "magical_village_group": {"W": (5, 2.5), "M": (1, 0.5)},
            "magical_village_group2": {"W": (14, 7), "S": (2, 1), "M": (5, 2)},
            
            "tower_of_light": {"W": (25,0), "M": (15,0)},
            "tower_of_light2": {"W": (50,0), "M": (25,0)},
            
            "the_stone": {"S": (100,0), "M": (100,0)}
        }
        self.price_group = {
            "village": "village_group",
            "village2":"village_group2",
            "port_village": "village_group",
            "port_village2":"village_group2",
            "magical_village": "magical_village_group",
            "magical_port_village" :"magical_village_group",
            "magical_village2": "magical_village_group2",
            "magical_port_village2" :"magical_village_group2",
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
            "tower_of_light": "M", "tower_of_light2": "M"
        }

        self.ADJACENT_BOOST = {
            "forest": {"W": 25}, "forest2": {"W": 25}, "forest3": {"W": 25}, "forest4": {"W": 50},
            "rocks2": {"S": 25}, "rocks3": {"S": 25},
 
            "village": {"W": 25, "S": 25},
            "village2": {"W": 50, "S": 50},
            
            "mining_village": {"S": 50},
            "mining_village2": {"S": 100},
            
            "treetop_village": {"W": 50},
            "treetop_village2": {"W": 100},

            "magical_village": {"W": 25, "M": 25},
            "magical_village2": {"W": 50, "M": 50},
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

    def tile_key(self, tile):
        return tile["building"] if tile["building"] is not None else tile["type"]
 
    def get_boost(self, key):
        return self.ADJACENT_BOOST.get(key, {})
 
    def adjacent_bonus(self, x, y, grid, res):
        rows, cols = len(grid), len(grid[0])
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        total = 0
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                total += self.get_boost(self.tile_key(grid[nx][ny])).get(res, 0)
        return total

    def one_production(self, x, y, grid):
        res = self.get_res_type(grid[x][y])
        if res == "E":
            return 0

        bonus = self.adjacent_bonus(x, y, grid, res)
        return self.base_rate[res] * (1 + bonus / 100)

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
        print("Chua co gia cho:", key)
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