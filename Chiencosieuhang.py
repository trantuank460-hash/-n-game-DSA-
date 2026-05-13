import pygame
import random
import math
import os

#CẤU HÌNH
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

#PHÔNG CHỮ TIẾNG VIỆT
# Sử dụng tahoma hoặc segoe ui thay cho Arial để đảm bảo tương thích Unicode
font_name = "tahoma"
font = pygame.font.SysFont(font_name, 24)
font_title = pygame.font.SysFont(font_name, 48, bold=True)
font_large = pygame.font.SysFont(font_name, 36)

#HÀM TẢI TÀI NGUYÊN
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

#TẢI ẢNH
img_bg = get_image("background.png", (WIDTH, HEIGHT), BLACK)
img_player = get_image("player.png", (75, 60), BLUE)
img_enemy = get_image("enemy.png", (60, 60), RED)
img_boss = get_image("boss.png", (180, 150), PURPLE)
img_bullet = get_image("bullet.png", (15, 25), YELLOW)
img_enemy_bullet = get_image("enemy_bullet.png", (15, 25), ORANGE)
img_hp = get_image("hp.png", (35, 35), GREEN)
img_power = get_image("powerup.png", (35, 35), BLUE)

#TẢI ÂM THANH
snd_shoot = get_sound("shoot.wav")
snd_explosion_small = get_sound("explosion_small.wav") # Tiếng nổ quái nhỏ
snd_explosion_boss = get_sound("explosion_boss.wav")   # Tiếng nổ khi giết boss
snd_player_hit = get_sound("explosion.wav")            # Tiếng nổ khi người chơi bị trúng đòn

def play_background_music():
    try:
        pygame.mixer.music.load("music_bg.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Không thể tải nhạc nền: {e}")

#CÁC LỚP ĐỐI TƯỢNG (CLASSES)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, power=1):
        super().__init__()
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
        self.max_hp = 8
        self.power_level = 1
        self.max_power = 5
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 200

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH: self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0: self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT: self.rect.y += self.speed

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
        self.rect = self.image.get_rect(x=random.randrange(50, WIDTH-50), y=random.randrange(-100, -40))
        self.speed_x = random.choice([-2, 2]) * (1 + level * 0.1)
        self.speed_y = random.uniform(0.5, 1.5) + (level * 0.1)
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = random.randint(1500, 3500)

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed_x *= -1
            self.rect.y += 20

        if self.rect.top > HEIGHT:
            self.kill()

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
        self.base_shoot_delay = max(500, 1500 - (level * 100))
        
        # Cấu trúc Máy trạng thái (State Machine) cho AI
        self.state = "ENTER"
        self.state_timer = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()

        # Trạng thái 1: Boss tiến vào màn hình
        if self.state == "ENTER":
            if self.rect.top < 50:
                self.rect.y += 2
            else:
                self.state = "HOVER"
                self.state_timer = now

        # Trạng thái 2: Di chuyển hình sin và bắn đạn tỏa
        elif self.state == "HOVER":
            self.time_counter += 0.05
            self.rect.x = (WIDTH//2 - self.rect.width//2) + math.sin(self.time_counter) * (WIDTH//2 - 100)

            if now - self.last_shot > self.base_shoot_delay:
                self.shoot_spread()
                self.last_shot = now

            if now - self.state_timer > 5000:
                self.state = random.choice(["SWOOP", "BURST"])
                self.state_timer = now

        # Trạng thái 3: Theo dõi tọa độ X của người chơi và bắn đạn thẳng liên tục
        elif self.state == "SWOOP":
            if self.rect.centerx < player.rect.centerx - 10:
                self.rect.x += 4
            elif self.rect.centerx > player.rect.centerx + 10:
                self.rect.x -= 4

            if now - self.last_shot > 300:
                self.shoot_straight()
                self.last_shot = now

            if now - self.state_timer > 3000:
                self.state = "HOVER"
                self.state_timer = now

        # Trạng thái 4: Xả đạn nhanh tại chỗ
        elif self.state == "BURST":
            if now - self.last_shot > 150:
                self.shoot_burst()
                self.last_shot = now

            if now - self.state_timer > 2000:
                self.state = "HOVER"
                self.state_timer = now

    def shoot_spread(self):
        for speed_x in [-4, -2, 0, 2, 4]:
            eb = EnemyBullet(self.rect.centerx, self.rect.bottom, speed_y=6, speed_x=speed_x)
            all_sprites.add(eb)
            enemy_bullets.add(eb)

    def shoot_straight(self):
        eb = EnemyBullet(self.rect.centerx, self.rect.bottom, speed_y=8, speed_x=0)
        all_sprites.add(eb)
        enemy_bullets.add(eb)

    def shoot_burst(self):
        speed_x = random.choice([-3, -1.5, 0, 1.5, 3])
        eb = EnemyBullet(self.rect.centerx, self.rect.bottom, speed_y=7, speed_x=speed_x)
        all_sprites.add(eb)
        enemy_bullets.add(eb)

    def draw_hp_bar(self, surface):
        bar_width = 400
        bar_height = 15
        fill = (self.hp / self.max_hp) * bar_width
        outline_rect = pygame.Rect(WIDTH//2 - bar_width//2, 20, bar_width, bar_height)
        fill_rect = pygame.Rect(WIDTH//2 - bar_width//2, 20, fill, bar_height)
        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 2)


#QUẢN LÝ TRẠNG THÁI TRÒ CHƠI 

all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
boss_group = pygame.sprite.Group() 
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group() 
items = pygame.sprite.Group()
player = None

score = 0
level = 1
enemies_to_spawn_boss = 15
enemies_killed = 0
boss_active = False

def reset_game():
    global all_sprites, enemies, boss_group, bullets, enemy_bullets, items, player
    global score, level, enemies_to_spawn_boss, enemies_killed, boss_active

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

def draw_ui():
    score_txt = font.render(f"Score: {score} | Level: {level}", True, WHITE)
    hp_txt = font.render(f"HP: {player.hp}/{player.max_hp}", True, GREEN)
    power_txt = font.render(f"Power: Lv.{player.power_level}/{player.max_power}", True, YELLOW)
    screen.blit(score_txt, (10, 10))
    screen.blit(hp_txt, (10, 40))
    screen.blit(power_txt, (10, 70))

    if boss_active:
        warning_txt = font.render("WARNING: BOSS INCOMING!", True, RED)
        if pygame.time.get_ticks() % 1000 < 500:
            screen.blit(warning_txt, (WIDTH//2 - 120, HEIGHT//2))

def draw_text_center(surface, text, font_type, color, y_offset):
    text_surface = font_type.render(text, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH//2, y_offset))
    surface.blit(text_surface, text_rect)

# Khởi động nhạc nền
play_background_music()

# Trạng thái điều khiển tổng thể
game_state = "MENU"
running = True

#VÒNG LẶP CHÍNH
while running:
    clock.tick(FPS)
    
    # 1. BẮT SỰ KIỆN
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == "MENU":
                if event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = "PLAYING"
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif game_state == "GAME_OVER":
                if event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = "PLAYING"
                if event.key == pygame.K_ESCAPE:
                    running = False

    # 2. XỬ LÝ LOGIC THEO TRẠNG THÁI
    try: 
        screen.blit(img_bg, (0, 0))
    except TypeError: 
        screen.fill(BLACK)

    if game_state == "MENU":
        draw_text_center(screen, "CHIẾN CƠ SIÊU HẠNG", font_title, WHITE, HEIGHT//3)
        draw_text_center(screen, "Nhấn ENTER để Bắt Đầu", font_large, YELLOW, HEIGHT//2)
        draw_text_center(screen, "Nhấn ESC để Thoát", font_large, RED, HEIGHT//2 + 50)

    elif game_state == "GAME_OVER":
        draw_text_center(screen, "TRÒ CHƠI KẾT THÚC", font_title, RED, HEIGHT//3)
        draw_text_center(screen, f"Điểm của bạn: {score}", font_large, WHITE, HEIGHT//2 - 30)
        draw_text_center(screen, f"Cấp độ đạt được: {level}", font_large, WHITE, HEIGHT//2 + 10)
        draw_text_center(screen, "Nhấn ENTER để Chơi Lại", font_large, YELLOW, HEIGHT//2 + 80)
        draw_text_center(screen, "Nhấn ESC để Thoát", font_large, RED, HEIGHT//2 + 130)

    elif game_state == "PLAYING":
        all_sprites.update()

        if not boss_active:
            if enemies_killed < enemies_to_spawn_boss:
                if len(enemies) < (5 + level):
                    e = Enemy(level)
                    all_sprites.add(e)
                    enemies.add(e)
            elif len(enemies) == 0:
                boss_active = True
                boss = Boss(level)
                all_sprites.add(boss)
                boss_group.add(boss)
        else:
            if len(boss_group) == 0:
                boss_active = False
                level += 1
                enemies_killed = 0
                enemies_to_spawn_boss += 5
                player.hp = min(player.hp + 2, player.max_hp)

        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            snd_explosion_small.play()
            score += 10
            enemies_killed += 1
            if random.random() < 0.15:
                it = Item(hit.rect.centerx, hit.rect.centery)
                all_sprites.add(it)
                items.add(it)

        boss_hits = pygame.sprite.groupcollide(boss_group, bullets, False, True)
        for boss_hit in boss_hits:
            boss_hit.hp -= player.power_level
            score += 5
            if boss_hit.hp <= 0:
                snd_explosion_boss.play()
                boss_hit.kill()
                score += 1000 * level

        item_hits = pygame.sprite.spritecollide(player, items, True)
        for item in item_hits:
            if item.type == 'hp' and player.hp < player.max_hp: player.hp += 1
            elif item.type == 'powerup' and player.power_level < player.max_power: player.power_level += 1

        if pygame.sprite.spritecollide(player, enemy_bullets, True):
            player.hp -= 1
            snd_player_hit.play()
            if player.power_level > 1: player.power_level -= 1
            if player.hp <= 0: game_state = "GAME_OVER"

        if pygame.sprite.spritecollide(player, enemies, True) or pygame.sprite.spritecollide(player, boss_group, False):
            player.hp -= 2
            snd_player_hit.play()
            if player.hp <= 0: game_state = "GAME_OVER"

        all_sprites.draw(screen)
        draw_ui()
        
        if boss_active and len(boss_group) > 0:
            boss.draw_hp_bar(screen)

    # 3. CẬP NHẬT MÀN HÌNH
    pygame.display.flip()

pygame.quit()