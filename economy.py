import math

class EconomyManager:
    def __init__(self):
        self.inventory = {'W': 12, 'S': 0, 'M': 0, 'T': 0}
        self.production_per_sec = {'W': 0, 'S': 0, 'M': 0, 'T': 0}
        self.buy_count = {}

        # Giá mua: mỗi tài nguyên là (base, step) -> giá = base + step * số lần đã mua
        self.COST_FORMULA = {
            "forest2": {"W": (2, 1)},
            "forest3": {"W": (5, 2.5)},
            "forest4": {"W": (8, 4), "S": (5, 2.5)},
            "rocks2": {"W": (8, 4)},
            "rocks3": {"W": (10, 5), "S": (3, 1)},
            "treetop_village": {"W": (15, 7.5)},
            "treetop_village2": {"W": (30, 10), "S": (15, 5)},
            "mushroom2": {"W": (6, 3)},

            "mining_village": {"W": (5, 2.5), "S": (2, 1)},
            "mining_village2": {"W": (10, 5), "S": (5, 2.5)},

            "village_group": {"W": (5, 2.5)},
            "village_group2": {"W": (10, 5), "S": (4, 2)},
            "village_group3": {"W": (20, 10), "S": (10, 5)},
            "village_group4": {"W": (40, 20), "S": (20, 10)},

            "magical_village_group": {"W": (5, 2.5), "M": (1, 0.5)},
            "magical_village_group2": {"W": (14, 7), "S": (2, 1), "M": (5, 2)},

            "tower_of_light": {"W": (25, 0), "M": (15, 0)},
            "tower_of_light2": {"W": (50, 0), "M": (25, 0)},

            "the_stone": {"S": (100, 0), "M": (100, 0)}
        }

        # Các công trình dùng chung một mức giá
        self.price_group = {
            "village": "village_group",
            "village2": "village_group2",
            "village3": "village_group3",
            "village4": "village_group4",
            "port_village": "village_group",
            "port_village2": "village_group2",
            "port_village3": "village_group3",
            "port_village4": "village_group4",
            "magical_village": "magical_village_group",
            "magical_port_village": "magical_village_group",
            "magical_village2": "magical_village_group2",
            "magical_port_village2": "magical_village_group2",
        }

        self.timer = 0.0
        self.tick_rate = 1.0

        # SẢN LƯỢNG GỐC: mỗi công trình / địa hình ra những tài nguyên nào, mỗi loại bao nhiêu (mỗi phút)
        # Loại ghi ĐẦU TIÊN là tài nguyên chính. Không có trong bảng -> không sinh gì.
        # W = gỗ, S = đá, M = mana, T = technology
        self.BASE_PRODUCTION = {
            # Địa hình
            "forest2": {"W": 3}, "forest3": {"W": 5}, "forest4": {"W": 10},
            "rocks2": {"S": 3}, "rocks3": {"S": 7},
            "mushroom2": {"W": 1.5, "M": 2},

            # Làng gỗ
            "village": {}, "village2": {},
            "port_village": {"W": 3}, "port_village2": {"W": 5},
            "treetop_village": {"W": 4}, "treetop_village2": {"W": 7},

            # Làng đá
            "mining_village": {"S": 2}, "mining_village2": {"S": 5},

            # Làng mana
            "magical_village": {"M": 2}, "magical_village2": {"M": 5},
            "magical_port_village": {"M": 2}, "magical_port_village2": {"M": 5},

            # Tháp ánh sáng
            "tower_of_light": {"M": 1.2}, "tower_of_light2": {"M": 3},
        }

        # % cộng thêm mà một ô đem lại cho các ô kề
        self.ADJACENT_BOOST = {
            "forest": {"W": 25}, "forest2": {"W": 25}, "forest3": {"W": 25}, "forest4": {"W": 50},
            "rocks": {"S": 25}, "rocks2": {"S": 25}, "rocks3": {"S": 25},

            "village": {"W": 25, "S": 25},
            "village2": {"W": 50, "S": 50},
            "village3": {"W": 75, "S": 75},
            "village4": {"W": 100, "S": 100},

            "mining_village": {"S": 50},
            "mining_village2": {"S": 100},

            "treetop_village": {"W": 50},
            "treetop_village2": {"W": 100},

            "magical_village": {"W": 25, "M": 25},
            "magical_village2": {"W": 50, "M": 50},
        }

    # Tên đại diện của ô: công trình nếu có, không thì địa hình
    def tile_key(self, tile):
        return tile["building"] if tile["building"] is not None else tile["type"]

    # Bảng sản lượng gốc của một ô, ví dụ {"M": 1, "W": 2}
    def get_base(self, tile):
        return self.BASE_PRODUCTION.get(self.tile_key(tile), {})

    def get_boost(self, key):
        return self.ADJACENT_BOOST.get(key, {})

    def adjacent_bonus(self, x, y, grid, res):
        rows, cols = len(grid), len(grid[0])
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        total = 0
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                if not grid[nx][ny].get["darkness", False]:
                    total += self.get_boost(self.tile_key(grid[nx][ny])).get(res, 0)
        return total

    # Sản lượng của MỘT ô cho TẤT CẢ tài nguyên, ví dụ {"M": 1.25, "W": 2.5}
    def tile_production(self, x, y, grid):
        if grid[x][y].get["darkness", False]: return{}
        result = {}
        for res, base in self.get_base(grid[x][y]).items():
            bonus = self.adjacent_bonus(x, y, grid, res)
            result[res] = base * (1 + bonus / 100)
        return result

    # Tổng sản lượng cả map
    def total_production(self, grid):
        total = {'W': 0.0, 'S': 0.0, 'M': 0.0, 'T': 0.0}
        for x in range(len(grid)):
            for y in range(len(grid[0])):
                for res, amount in self.tile_production(x, y, grid).items():
                    total[res] += amount
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
        if key in self.COST_FORMULA:
            count = self.buy_count.get(key, 0)
            cost = {}
            for res, (base, step) in self.COST_FORMULA[key].items():
                cost[res] = math.floor(base + step * count)
            return cost
        return {}   # Chưa khai báo giá -> trả về rỗng, try_buy sẽ chặn

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
        # Sản lượng mỗi phút của cả map
        self.production_per_sec = self.total_production(game_map)
        # Cộng vào kho theo thời gian trôi qua
        for res, amount in self.production_per_sec.items():
            self.inventory[res] += amount * (dt / 60.0)