import time
import subprocess
import os

inventory = {
    'W' : 0,
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
    'W': {'W': 10},            #Xưởng gỗ
    'S': {'W': 20, 'S': 10},   #Mỏ Đá 
    'M': {'S': 50, 'M': 5},    #Giếng Mana 
    'T': {'W': 100, 'M': 20}   #Nhà Tech 
}

def count_adjacent(x,y, grid):
    rows = len(grid)
    cols = len(grid[0])
    directions = [(-1,0), (1,0), (0, -1), (0, 1)]
    count = 0

    current_key = grid[x][y]
    for dx, dy in directions:
        nx = x + dx
        ny = y + dy
        
        if 0 <= nx < rows and 0 <= ny < cols:
            if grid[nx][ny] == current_key:
                count += 1
    return count

def one_production(x,y, grid):
    neighbor = count_adjacent(x,y,grid)
    current_key = grid[x][y]
    if current_key == "E":
        return 0
    
    production = base_rate[current_key]*(1 + 0.25*neighbor)
    return production

def total_production(grid):
    rows = len(grid)
    cols = len(grid[0])
    total_production = {'W': 0, 'S': 0, 'M': 0, 'T': 0}
    for x in range(rows):
        for y in range(cols):
            current_key = grid[x][y]
            if current_key != "E":
                total_production[current_key] += one_production(x,y,grid)
    return total_production

def build_structure(x,y,type,grid):
    if grid[x][y] == 'E':
        print("Xây thất bại!")
        return False
    chi_phi = build_cost[type] 
    for tai_nguyen, gia_tien in chi_phi.items():
        if inventory[tai_nguyen] < gia_tien:
            print('Không đủ tiền, xây thất bại!')
            return False

    for tai_nguyen, gia_tien in chi_phi.items:
        inventory[tai_nguyen] -= gia_tien

    grid[x][y] = type
    print(f'Xây nhà thành công!')
    return True

map_game = [
    ['E', 'W', 'W', 'S'],
    ['W', 'W', 'W', 'S'],
    ['S', 'S', 'M', 'T'],
    ['M', 'W', 'W', 'T']
]

print("START GAME!")

build_structure(0, 0, 'S', map_game) 
build_structure(1, 1, 'W', map_game) 
while True:
    subprocess.run('cls' if os.name == 'nt' else 'clear', shell=True)

    production_per_sec = total_production(map_game)
    for resource_kind in production_per_sec:
        inventory[resource_kind] += production_per_sec[resource_kind]
    print(f"""Storage:\n| Wood: {inventory['W']} wood\n| Stone: {inventory['S']} stone \n| Mana: {inventory['M']} mana \n| Technology: {inventory['T']} tech""")

    time.sleep(1)

    print("START GAME!\n")

