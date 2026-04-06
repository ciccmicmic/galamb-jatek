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

# Hangok (MINDEN ÁTÍRVA OGG-RA)
try:
    pygame.mixer.music.load("background_music.ogg")
except:
    pass

jump_sound = load_sound("jump.ogg")
coin_sound = load_sound("coin.ogg")
game_over_sound = load_sound("game_over.ogg")
viktor_jump_sound = load_sound("viktor_jump.ogg")
viktor_coin_sound = load_sound("viktor_coin.ogg")
dragon_sound = load_sound("dragon_roar.ogg")

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

    def update(
