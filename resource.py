BASE_RATES = {
    "Lumber Mill": {"resource": "wood", "rate": 1.0},
    "Quarry":      {"resource": "stone", "rate": 1.0},
    "Mana Well":   {"resource": "mana", "rate": 0.5},
    "Tech Lab":    {"resource": "tech", "rate": 0.3},
}
 
# Chi phí xây dựng CẤP 1 -> CẤP 2 (điểm khởi đầu của hàm mũ)
BASE_COSTS = {
    "Lumber Mill": 50,   # đơn vị: wood (resource chính của nhà này)
    "Quarry":      50,   # đơn vị: stone
    "Mana Well":   80,   # mana rate thấp -> chi phí gốc cao hơn 1 chút
    "Tech Lab":    120,  # tech hiếm nhất -> chi phí gốc cao nhất
}
 
GROWTH_FACTOR = 1.5          # hệ số trượt giá: mỗi cấp đắt hơn 50%
LEVEL_RATE_BONUS = 0.15      # mỗi cấp +15% rate (tuyến tính nhẹ)
ADJACENCY_BONUS_PER_NEIGHBOR = 0.25   # từ resource_system.py, dùng lại ở đây
 
MAX_LEVEL = 8
 
# Mốc mở khóa tài nguyên chéo: level >= mốc thì cộng thêm resource đó vào cost
# ratio là % so với cost chính, dùng để tính amount phụ
CROSS_RESOURCE_THRESHOLDS = [
    (4, "mana", 0.30),   # từ level 4 trở đi, cộng thêm mana = 30% cost chính
    (7, "tech", 0.20),   # từ level 7 trở đi, cộng thêm tech = 20% cost chính
]

