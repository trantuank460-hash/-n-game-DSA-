import pygame
import random

#Cấu hình 
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Đồ án Game: Chiến Cơ Siêu Hạng")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# Đạn 
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, power=1):
        super().__init__()
        self.image = pygame.Surface((5 * power, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

# Item rơi ngẫu nhiên 
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.type = random.choice(['hp', 'powerup'])
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREEN if self.type == 'hp' else PURPLE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_y = 3

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT:
            self.kill()

# Player 
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT-10))
        self.speed = 7
        self.hp = 4
        self.power_level = 1

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH: self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0: self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT: self.rect.y += self.speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top, self.power_level)
        all_sprites.add(bullet)
        bullets.add(bullet)

# Enemy 
class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed_mult):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(x=random.randrange(WIDTH-30), y=random.randrange(-100, -40))
        self.speed_y = random.randrange(2, 5) * speed_mult

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT:
            self.kill()

# KHỞI TẠO NHÓM ĐỐI TƯỢNG 
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
items = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# BIẾN TRẠNG THÁI GAME 
score = 0
level = 1
enemies_to_next_level = 10
enemies_killed = 0
running = True

def draw_ui():
    score_txt = font.render(f"Score: {score} | Level: {level}", True, WHITE)
    hp_txt = font.render(f"HP: {'♥' * player.hp}", True, RED)
    ammo_txt = font.render("Ammo: ∞", True, YELLOW)
    screen.blit(score_txt, (10, 10))
    screen.blit(hp_txt, (10, 40))
    screen.blit(ammo_txt, (10, 70))

# VÒNG LẶP CHÍNH 
while running:
    clock.tick(FPS)
    
    # 1. Sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # 2. Cập nhật
    all_sprites.update()
    items.update()

    # Sinh kẻ thù dựa trên Level (Level càng cao địch ra càng nhanh)
    if len(enemies) < (5 + level * 2):
        e = Enemy(1 + level * 0.2)
        all_sprites.add(e)
        enemies.add(e)

    # Va chạm: Đạn - Kẻ thù
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        score += 10
        enemies_killed += 1
        # Xác suất 20% rơi Item
        if random.random() < 0.2:
            it = Item(hit.rect.centerx, hit.rect.centery)
            all_sprites.add(it)
            items.add(it)
        
        # Chuyển màn
        if enemies_killed >= enemies_to_next_level:
            level += 1
            enemies_killed = 0
            enemies_to_next_level += 5 # Màn sau cần bắn nhiều hơn

    # Va chạm: Người chơi - Item
    item_hits = pygame.sprite.spritecollide(player, items, True)
    for item in item_hits:
        if item.type == 'hp' and player.hp < 6:
            player.hp += 1
        elif item.type == 'powerup':
            player.power_level += 1

    # Va chạm: Người chơi - Kẻ thù
    if pygame.sprite.spritecollide(player, enemies, True):
        player.hp -= 1
        if player.hp <= 0:
            running = False

    # 3. Vẽ
    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_ui()
    pygame.display.flip()

print(f"GAME OVER - Score: {score} - Level: {level}")
pygame.quit()