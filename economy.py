inventory = {
    'W' : 100, # Cho sẵn 100 gỗ ban đầu để lát test xây dựng cho dễ
    'S' : 0,
    'M' : 0,
    'T' : 0,
}

base_rate = {
    'W' : 3,
    'S' : 3,
    'M' : 1,
    'T' : 1
}

build_cost = {
    'W': {'W': 10},            # Xưởng gỗ
    'S': {'W': 20, 'S': 10},   # Mỏ Đá 
    'M': {'S': 50, 'M': 5},    # Giếng Mana 
    'T': {'W': 100, 'M': 20}   # Nhà Tech 
}

# --- BỘ CHUYỂN ĐỔI NGÔN NGỮ (Adapter) ---
# Dịch tên công trình từ map.py sang mã W, S, M, T của Đạt
def lay_ma_cong_trinh(tile):
    b = tile["building"]
    if b in ["village", "treetop_village", "port_village"]: 
        return 'W'
    if b == "mining_village": 
        return 'S'
    if b in ["magical_village", "magical_port_village"]: 
        return 'M'
    if b == "Tower_of_light": 
        return 'T'
    return 'E'

def count_adjacent(x, y, grid):
    rows = len(grid)
    cols = len(grid[0])
    directions = [(-1,0), (1,0), (0, -1), (0, 1)]
    count = 0

    current_key = lay_ma_cong_trinh(grid[x][y])
    for dx, dy in directions:
        nx = x + dx
        ny = y + dy
        if 0 <= nx < rows and 0 <= ny < cols:
            if lay_ma_cong_trinh(grid[nx][ny]) == current_key:
                count += 1
    return count

def one_production(x, y, grid):
    current_key = lay_ma_cong_trinh(grid[x][y])
    if current_key == "E":
        return 0
    neighbor = count_adjacent(x, y, grid)
    return base_rate[current_key] * (1 + 0.25 * neighbor)

# Hàm này sẽ được main.py gọi mỗi 1 giây
def cap_nhat_tai_nguyen(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    san_luong_moi_giay = {'W': 0, 'S': 0, 'M': 0, 'T': 0}
    
    # Quét toàn bộ map 12x12
    for x in range(rows):
        for y in range(cols):
            san_luong = one_production(x, y, grid)
            if san_luong > 0:
                loai_tai_nguyen = lay_ma_cong_trinh(grid[x][y])
                san_luong_moi_giay[loai_tai_nguyen] += san_luong
                
    # Cộng vào kho
    for tai_nguyen, so_luong in san_luong_moi_giay.items():
        inventory[tai_nguyen] += so_luong
        
    print(f"Storage: Wood [{inventory['W']}] | Stone [{inventory['S']}] | Mana [{inventory['M']}] | Tech [{inventory['T']}]")