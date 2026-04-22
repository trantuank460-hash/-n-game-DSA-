import pygame
import random

class Player(pygame.sprite.Sprite):
    """
    Lớp đại diện cho phi thuyền của người chơi (player)
    
    Attributes:
        speed (int): Tốc độ di chuyển của phi thuyền ( thay đổi tùy theo màn hoặc nâng cấp khi ăn được viên năng lượng )
        hp (int): Số lượng máu (sinh mạng) còn lại
        power_level (int): Cấp độ sức mạnh của đạn
        
    Methods:
        update(): Xử lý logic di chuyển 4 hướng từ bàn phím và giới hạn biên
        shoot(): Khởi tạo đối tượng Bullet tại vị trí hiện tại của phi thuyền
    """
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(midbottom=(400, 590))
        self.speed = 7
        self.hp = 4
        self.power_level = 1

class Enemy(pygame.sprite.Sprite):
    """
    Lớp quản lý các máy bay kẻ thù sinh ra ngẫu nhiên
    
    Args:
        speed_mult (float): Hệ số nhân tốc độ, dùng để tăng độ khó theo level
        
    Logic:
        Kẻ thù tự động di chuyển từ trên xuống dưới và tự hủy (kill) khi
        vượt quá giới hạn màn hình để giải phóng bộ nhớ
    """
    def __init__(self, speed_mult):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(x=random.randrange(770), y=random.randrange(-100, -40))
        self.speed_y = random.randrange(2, 5) * speed_mult

class Bullet(pygame.sprite.Sprite):
    """
    Lớp quản lý đạn bắn ra từ người chơi.
    
    Args:
        x (int): Tọa độ X khởi tạo
        y (int): Tọa độ Y khởi tạo
        power (int): Cấp độ sức mạnh ảnh hưởng đến kích thước viên đạn
        
    Optimization:
        Sử dụng cơ chế tự hủy khi rect.bottom < 0 để tránh tràn bộ nhớ
    """
    def __init__(self, x, y, power=1):
        super().__init__()
        self.image = pygame.Surface((5 * power, 15))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed_y = -10

class Item(pygame.sprite.Sprite):
    """
    Lớp đại diện cho các vật phẩm hỗ trợ rơi ra từ kẻ thù
    
    Types:
        'hp': Hồi máu cho người chơi
        'powerup': Nâng cấp kích thước/sức mạnh đạn
    """
    def __init__(self, x, y):
        super().__init__()
        self.type = random.choice(['hp', 'powerup'])
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 255, 0) if self.type == 'hp' else (128, 0, 128))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_y = 3

def spawn_enemy():
    """
    Hàm bổ trợ để khởi tạo một đối tượng Enemy mới
    Thêm đối tượng vào các nhóm quản lý tương ứng (Sprite Groups)
    """
    pass # Code triển khai nằm trong vòng lặp chính

def check_collisions():
    """
    Giải thuật xử lý va chạm chính của game
    Sử dụng AABB Collision để xác định tương tác giữa
    - Bullet vs Enemy (Tiêu diệt địch, rơi vật phẩm)
    - Player vs Enemy (Giảm máu người chơi)
    - Player vs Item (Tăng máu hoặc nâng cấp đạn)
    """
    pass # Code triển khai nằm trong vòng lặp chính


# --- LỆNH IN DOCSTRINGS RA MÀN HÌNH ---
if __name__ == "__main__":
    print("--- THÔNG TIN CHI TIẾT CÁC LỚP TRONG GAME ---")
    
    # In docstring của lớp Player
    print("\n[LỚP PLAYER]:")
    print(Player.__doc__)
    
    # In docstring của lớp Enemy
    print("-" * 30)
    print("[LỚP ENEMY]:")
    print(Enemy.__doc__)
    
    # In docstring của lớp Bullet
    print("-" * 30)
    print("[LỚP BULLET]:")
    print(Bullet.__doc__)
    
    # In docstring của lớp Item
    print("-" * 30)
    print("[LỚP ITEM]:")
    print(Item.__doc__)

    # In docstring của các hàm
    print("-" * 30)
    print("[HÀM SPAWN ENEMY]:")
    print(spawn_enemy.__doc__)

    print("-" * 30)
    print("[HÀM CHECK COLLISIONS]:")
    print(check_collisions.__doc__)
    
    print("\n--- KẾT THÚC PHẦN GIỚI THIỆU ---\n")
