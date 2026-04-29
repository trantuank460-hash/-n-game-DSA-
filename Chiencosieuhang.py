import pygame
import random
import math
import os

# --- CẤU HÌNH ---
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
RED, GREEN, YELLOW = (255, 0, 0), (0, 255, 0), (255, 255, 0)
BLUE, PURPLE, ORANGE = (0, 0, 255), (128, 0, 128), (255, 165, 0)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chiến Cơ Siêu Hạng - Kỷ Nguyên Boss")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# --- HÀM TẢI TÀI NGUYÊN (CÓ FALLBACK BẢO VỆ) ---
def get_image(filename, size, fallback_color):
    try:
        img = pygame.image.load(filename).convert_alpha()
        return pygame.transform.scale(img, size)
    except FileNotFoundError:
        surf = pygame.Surface(size)
        surf.fill(fallback_color)
        return surf

def get_sound(filename):
    try: return pygame.mixer.Sound(filename)
    except FileNotFoundError: return type('NoSound', (), {'play': lambda self: None})()

# --- TẢI ẢNH & ÂM THANH (KÍCH THƯỚC ĐÃ ĐƯỢC PHÓNG TO) ---
img_bg = get_image("background.png", (WIDTH, HEIGHT), BLACK)
img_player = get_image("player.png", (75, 60), BLUE)        # To hơn
img_enemy = get_image("enemy.png", (60, 60), RED)           # To hơn
img_boss = get_image("boss.png", (180, 150), PURPLE)        # Boss to hoành tráng
img_bullet = get_image("bullet.png", (15, 25), YELLOW)      # Kích thước cơ bản của đạn
img_enemy_bullet = get_image("enemy_bullet.png", (15, 25), ORANGE) # Đạn địch to hơn
img_hp = get_image("hp.png", (35, 35), GREEN)               # Icon to hơn
img_power = get_image("powerup.png", (35, 35), BLUE)        # Icon to hơn

snd_shoot = get_sound("shoot.wav")
snd_explosion = get_sound("explosion.wav")

# ================= CÁC LỚP ĐỐI TƯỢNG (CLASSES) =================

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, power=1):
        super().__init__()
        # Kích thước chiều ngang cơ bản to hơn (10) và tăng lên khi ăn powerup
        bullet_width = 10 + (power * 4) 
        bullet_height = 30 
        self.image = pygame.transform.scale(img_bullet, (bullet_width, bullet_height))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0: self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y=5, speed_x=0):
        super().__init__()
        self.image = img_enemy_bullet
        self.rect = self.image.get_rect(midtop=(x, y))
        self.speed_y = speed_y
        self.speed_x = speed_x

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.top > HEIGHT or self.rect.left < 0 or self.rect.right > WIDTH: 
            self.kill()

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.type = random.choice(['hp', 'powerup'])
        self.image = img_hp if self.type == 'hp' else img_power
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_y = 3

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT: self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = img_player
        self.rect = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT-10))
        self.speed = 7
        self.hp = 5
        self.power_level = 1
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 200 # Khóa tốc độ bắn 

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH: self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0: self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT: self.rect.y += self.speed

        # Bắn đạn tự động khi giữ phím Space
        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.shoot()
                self.last_shot = now

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top, self.power_level)
        all_sprites.add(bullet)
        bullets.add(bullet)
        snd_shoot.play()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.image = img_enemy
        # Sinh ngẫu nhiên trên cùng, tránh mép
        self.rect = self.image.get_rect(x=random.randrange(50, WIDTH-50), y=random.randrange(-100, -40))
        
        # Di chuyển ngang dọc
        self.speed_x = random.choice([-2, 2]) * (1 + level * 0.1)
        self.speed_y = random.uniform(0.5, 1.5) + (level * 0.1)
        
        # Biến để kiểm soát bắn
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = random.randint(1500, 3500) # 1.5s - 3.5s bắn 1 lần

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Dội lại khi chạm tường hai bên
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed_x *= -1
            self.rect.y += 20 # Tiến xuống một chút khi dội tường

        # Xóa nếu bay quá màn hình
        if self.rect.top > HEIGHT:
            self.kill()

        # Bắn đạn
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay and self.rect.y > 0:
            self.shoot()
            self.last_shot = now

    def shoot(self):
        eb = EnemyBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(eb)
        enemy_bullets.add(eb)

class Boss(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.image = img_boss
        self.rect = self.image.get_rect(center=(WIDTH//2, -150))
        self.hp = 30 + (level * 20) 
        self.max_hp = self.hp
        
        self.time_counter = 0
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = max(500, 1500 - (level * 100)) # Màn càng cao bắn càng lẹ

    def update(self):
        # Xuất hiện từ từ vào màn hình
        if self.rect.top < 50:
            self.rect.y += 2
        else:
            # Di chuyển ngang hình sin mượt mà
            self.time_counter += 0.05
            self.rect.x = (WIDTH//2 - self.rect.width//2) + math.sin(self.time_counter) * (WIDTH//2 - 100)

        # Boss Bắn đạn
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay and self.rect.top >= 50:
            self.shoot()
            self.last_shot = now

    def shoot(self):
        # Bắn đạn chùm 3 viên xòe ra
        for speed_x in [-3, 0, 3]:
            eb = EnemyBullet(self.rect.centerx, self.rect.bottom, speed_y=6, speed_x=speed_x)
            all_sprites.add(eb)
            enemy_bullets.add(eb)

    def draw_hp_bar(self, surface):
        # Vẽ thanh máu Boss
        bar_width = 400
        bar_height = 15
        fill = (self.hp / self.max_hp) * bar_width
        outline_rect = pygame.Rect(WIDTH//2 - bar_width//2, 20, bar_width, bar_height)
        fill_rect = pygame.Rect(WIDTH//2 - bar_width//2, 20, fill, bar_height)
        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 2)


# ================= KHỞI TẠO GAME =================
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
boss_group = pygame.sprite.Group() 
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group() 
items = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

score = 0
level = 1
enemies_to_spawn_boss = 15
enemies_killed = 0
boss_active = False
running = True

def draw_ui():
    score_txt = font.render(f"Score: {score} | Level: {level}", True, WHITE)
    hp_txt = font.render(f"HP: {'♥' * player.hp}", True, GREEN)
    power_txt = font.render(f"Power: Lv.{player.power_level}", True, YELLOW)
    screen.blit(score_txt, (10, 10))
    screen.blit(hp_txt, (10, 40))
    screen.blit(power_txt, (10, 70))

    if boss_active:
        warning_txt = font.render("WARNING: BOSS INCOMING!", True, RED)
        # Nhấp nháy text cảnh báo Boss
        if pygame.time.get_ticks() % 1000 < 500:
            screen.blit(warning_txt, (WIDTH//2 - 120, HEIGHT//2))

# ================= VÒNG LẶP CHÍNH =================
while running:
    clock.tick(FPS)
    
    # 1. BẮT SỰ KIỆN
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. CẬP NHẬT TRẠNG THÁI
    all_sprites.update()

    # --- QUẢN LÝ KẺ ĐỊCH VÀ BOSS ---
    if not boss_active:
        # Nếu chưa đủ kill thì sinh quái nhỏ
        if enemies_killed < enemies_to_spawn_boss:
            if len(enemies) < (5 + level):
                e = Enemy(level)
                all_sprites.add(e)
                enemies.add(e)
        # Đủ kill và dọn sạch quái nhỏ -> Gọi Boss
        elif len(enemies) == 0:
            boss_active = True
            boss = Boss(level)
            all_sprites.add(boss)
            boss_group.add(boss)
    else:
        # Nếu Boss đã chết -> Chuyển màn
        if len(boss_group) == 0:
            boss_active = False
            level += 1
            enemies_killed = 0
            enemies_to_spawn_boss += 5 # Tăng số quái yêu cầu cho màn sau
            player.hp = min(player.hp + 2, 8) # Hồi máu qua màn

    # --- XỬ LÝ VA CHẠM ---
    # Đạn người chơi trúng Kẻ thù nhỏ
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        snd_explosion.play()
        score += 10
        enemies_killed += 1
        if random.random() < 0.15: # 15% rơi đồ
            it = Item(hit.rect.centerx, hit.rect.centery)
            all_sprites.add(it)
            items.add(it)

    # Đạn người chơi trúng Boss
    boss_hits = pygame.sprite.groupcollide(boss_group, bullets, False, True)
    for boss_hit in boss_hits:
        boss_hit.hp -= player.power_level # Đạn mạnh thì trừ máu Boss nhiều hơn
        score += 5
        if boss_hit.hp <= 0:
            snd_explosion.play()
            boss_hit.kill()
            score += 1000 * level

    # Người chơi ăn Item
    item_hits = pygame.sprite.spritecollide(player, items, True)
    for item in item_hits:
        if item.type == 'hp' and player.hp < 8: player.hp += 1
        elif item.type == 'powerup' and player.power_level < 5: player.power_level += 1

    # Người chơi trúng Đạn của kẻ thù
    if pygame.sprite.spritecollide(player, enemy_bullets, True):
        player.hp -= 1
        snd_explosion.play()
        if player.power_level > 1: player.power_level -= 1 # Trúng đạn bị tụt level súng
        if player.hp <= 0: running = False

    # Người chơi đâm trúng thân Kẻ thù hoặc Boss
    if pygame.sprite.spritecollide(player, enemies, True) or pygame.sprite.spritecollide(player, boss_group, False):
        player.hp -= 2
        snd_explosion.play()
        if player.hp <= 0: running = False

    # 3. VẼ LÊN MÀN HÌNH
    try: screen.blit(img_bg, (0, 0))
    except TypeError: screen.fill(BLACK)
        
    all_sprites.draw(screen)
    draw_ui()
    
    # Vẽ thanh máu Boss nếu Boss đang xuất hiện
    if boss_active and len(boss_group) > 0:
        boss.draw_hp_bar(screen)

    pygame.display.flip()

print(f"GAME OVER - Score: {score} - Level: {level}")
pygame.quit()