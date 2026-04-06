import pygame
import random
import asyncio

# Inicializáljuk a Pygame-et
pygame.init()
pygame.mixer.init()

# Ablak méretei
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Színek
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Képek méretei
VIKTOR_WIDTH = 80 * 2  
VIKTOR_HEIGHT = 100 * 2 
DRAGON_WIDTH = 120 * 2  
DRAGON_HEIGHT = 60 * 2 
COIN_WIDTH = 25
COIN_HEIGHT = 25
BACKGROUND_WIDTH = 800
BACKGROUND_HEIGHT = 600

# Ablak létrehozása
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galambocska")

font = pygame.font.Font(None, 36)
try:
    pixel_font = pygame.font.Font("PressStart2P-Regular.ttf", 20)
except:
    pixel_font = pygame.font.Font(None, 24)

# --- FÜGGVÉNYEK KÉPEK ÉS HANGOK BIZTONSÁGOS BETÖLTÉSÉHEZ ---
def load_image(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception as e:
        print(f"Hiba a kép betöltésekor ({path}): {e}")
        surf = pygame.Surface(size if size else (50, 50))
        surf.fill((255, 0, 0)) # Ha nincs meg a kép, egy piros kocka lesz helyette
        return surf

def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except:
        return None

# Képek
viktor_img = load_image("assets/viktor_a6.png", (VIKTOR_WIDTH, VIKTOR_HEIGHT))
dragon_img = load_image("assets/dragon.png", (DRAGON_WIDTH, DRAGON_HEIGHT))
coin_img = load_image("assets/coin.png", (COIN_WIDTH, COIN_HEIGHT))

bg_images = []
for bg_file in ["background1.png", "background2.png", "background3.png"]:
    try:
        img = pygame.image.load(bg_file).convert()
        bg_images.append(pygame.transform.scale(img, (BACKGROUND_WIDTH, BACKGROUND_HEIGHT)))
    except:
        surf = pygame.Surface((BACKGROUND_WIDTH, BACKGROUND_HEIGHT))
        surf.fill((135, 206, 235))
        bg_images.append(surf)

bg_x = [0, BACKGROUND_WIDTH, BACKGROUND_WIDTH * 2]

# Hangok
try:
    pygame.mixer.music.load("background_music.mp3")
except:
    pass

jump_sound = load_sound("jump.wav")
coin_sound = load_sound("coin.wav")
game_over_sound = load_sound("game_over.wav")
viktor_jump_sound = load_sound("viktor_jump.wav")
viktor_coin_sound = load_sound("viktor_coin.wav")
dragon_sound = load_sound("dragon_roar.wav")

def play_sfx(sound_obj):
    if sound_obj:
        pygame.mixer.Sound.play(sound_obj)

# --- OSZTÁLYOK ---
class Viktor(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.image = viktor_img
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self.gravity = 0.8
        self.is_jumping = False
        self.y_velocity = 0
        self.can_jump = True

    def jump(self):
        if self.can_jump:
            play_sfx(viktor_jump_sound)
            self.is_jumping = True
            self.y_velocity = -10
            self.can_jump = False

    def update(self):
        if self.is_jumping:
            self.y_velocity += self.gravity
            self.rect.y += self.y_velocity
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT
                self.is_jumping = False
                self.y_velocity = 0
                self.can_jump = True

class Dragon(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = dragon_img
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - DRAGON_HEIGHT - 50)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = coin_img
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = random.randint(50, SCREEN_HEIGHT - COIN_HEIGHT - 50)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


# --- ASZINKRON FŐCIKLUS (Böngészőhöz) ---
async def main():
    clock = pygame.time.Clock()
    viktor = Viktor(50, 360)
    
    dragons = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    
    score = 0
    coin_count = 0
    lives = 5
    difficulty_level = 1
    game_speed = 2
    dragon_speed = 2
    game_mode = "normal"
    
    dragon_timer = 0
    coin_timer = 0
    DRAGON_SPAWN_INTERVAL = 2000
    COIN_SPAWN_INTERVAL = 1000
    last_speed_increase_time = pygame.time.get_ticks()
    
    running = True
    game_start = False
    game_over = False
    new_high_score = False
    high_score = 0

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_start:
                        try:
                            pygame.mixer.music.play(-1)
                        except:
                            pass
                        game_start = True
                        score = 0
                        coin_count = 0
                        lives = 5
                        dragons.empty()
                        coins.empty()
                        game_over = False
                        new_high_score = False
                        game_speed = 2
                        dragon_speed = 2
                        difficulty_level = 1
                        last_speed_increase_time = pygame.time.get_ticks()
                    elif not viktor.is_jumping:
                        viktor.jump()
                
                if event.key == pygame.K_m:
                    if game_mode == "normal":
                        game_mode = "easy"
                        dragon_speed = max(1, dragon_speed - 1)
                        game_speed = max(1, game_speed - 1)
                    else:
                        game_mode = "normal"
                        dragon_speed += 1
                        game_speed += 1

        if not game_start:
            for i, img in enumerate(bg_images):
                screen.blit(img, (bg_x[i], 0))
                bg_x[i] -= 1
                if bg_x[i] <= -img.get_width():
                    bg_x[i] = img.get_width() * 2
            
            start_text = font.render("Nyomd meg a SPACE-t a jatekhoz!", True, BLACK)
            screen.blit(start_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            await asyncio.sleep(0) # --- WEBASSEMBLY BÖNGÉSZŐ CIKLUS LÉLEGZET ---
            continue

        if game_over:
            for i, img in enumerate(bg_images):
                screen.blit(img, (bg_x[i], 0))
            
            over_text = pixel_font.render("Vege van!", True, BLACK)
            screen.blit(over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 30))
            score_text = font.render("Pontszam: " + str(score), True, BLACK)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2))
            
            restart_text = font.render("SPACE = Uj jatek", True, BLACK)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60))
            
            pygame.display.flip()
            await asyncio.sleep(0)
            continue

        # --- JÁTÉK MOZGATÁSOK ---
        for i, img in enumerate(bg_images):
            screen.blit(img, (bg_x[i], 0))
            bg_x[i] -= game_speed
            if bg_x[i] <= -img.get_width():
                bg_x[i] = img.get_width() * 2

        if score >= difficulty_level * 100:
            if current_time - last_speed_increase_time >= 2000:
                difficulty_level += 1
                game_speed = min(game_speed + 1, 15)
                dragon_speed = min(dragon_speed + 1, 15)
                last_speed_increase_time = current_time

        viktor.update()
        screen.blit(viktor.image, viktor.rect)

        if current_time - dragon_timer >= DRAGON_SPAWN_INTERVAL:
            dragons.add(Dragon(dragon_speed))
            dragon_timer = current_time

        for dragon in dragons:
            dragon.update()
            screen.blit(dragon.image, dragon.rect)
            if pygame.sprite.collide_rect(viktor, dragon):
                play_sfx(dragon_sound)
                lives -= 1
                dragon.kill()
                if lives <= 0:
                    try:
                        pygame.mixer.music.stop()
                    except:
                        pass
                    play_sfx(game_over_sound)
                    game_over = True
                    if score > high_score:
                        high_score = score
                        new_high_score = True

        if current_time - coin_timer >= COIN_SPAWN_INTERVAL:
            coins.add(Coin(game_speed))
            coin_timer = current_time

        for coin in coins:
            coin.update()
            screen.blit(coin.image, coin.rect)
            if pygame.sprite.collide_rect(viktor, coin):
                play_sfx(viktor_coin_sound)
                coin.kill()
                score += 10
                coin_count += 1

        score_text = font.render("Pont: " + str(score), True, BLACK)
        lives_text = font.render("Elet: " + str(lives), True, BLACK)
        screen.blit(score_text, (SCREEN_WIDTH - 150, 10))
        screen.blit(lives_text, (SCREEN_WIDTH - 150, 40))

        pygame.display.flip()
        clock.tick(60)
        
        # --- A LEGFONTOSABB SOR: Átadja a vezérlést a böngészőnek ---
        await asyncio.sleep(0) 

# Indítás Wasm kompatibilis módon
asyncio.run(main())