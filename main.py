import pygame
import random
import asyncio
import os

# --- INICIALIZÁLÁS (Tisztább hang beállításokkal) ---
pygame.mixer.pre_init(44100, -16, 2, 4096)
pygame.init()
pygame.mixer.init()

# Ablak méretei
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Viktor Kalandjai")

# --- ASSET BETÖLTÉS ---
def load_img(name, scale=None):
    try:
        img = pygame.image.load(name).convert_alpha()
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    except:
        surf = pygame.Surface(scale if scale else (50, 50))
        surf.fill((255, 0, 0)) 
        return surf

def load_sd(name):
    try:
        return pygame.mixer.Sound(name)
    except:
        return None

# --- ASSETS ---
RUNNING = [load_img("ViktorRun1.png"), load_img("ViktorRun2.png")]
JUMPING = load_img("ViktorJump.png")
DUCKING = [load_img("ViktorDuck1.png"), load_img("ViktorDuck2.png")]
SMALL_AVOCADO = [load_img("SmallAvocado1.png"), load_img("SmallAvocado2.png"), load_img("SmallAvocado3.png")]
LARGE_AVOCADO = [load_img("LargeAvocado1.png"), load_img("LargeAvocado2.png")]
HELI = [load_img("heli1.png"), load_img("heli2.png")]
CLOUD_IMG = load_img("Cloud.png") 
LANDING_PAGE = load_img("landingpage.png", (SCREEN_WIDTH, SCREEN_HEIGHT))

# Háttér panoráma
try:
    orig_bg = pygame.image.load("background.png").convert()
    bg_ratio = orig_bg.get_width() / orig_bg.get_height()
    BACKGROUND = pygame.transform.scale(orig_bg, (int(600 * bg_ratio), 600))
except:
    BACKGROUND = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    BACKGROUND.fill((200, 200, 200))

# Hangok
jump_sound = load_sd("jump.ogg")
duck_sound = load_sd("duck.ogg")
collision_sound = load_sd("collision.ogg")
game_over_sound = load_sd("game_over.ogg")

# --- OSZTÁLYOK ---
class Viktosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.image = RUNNING[0]
        self.rect = self.image.get_rect(topleft=(self.X_POS, self.Y_POS))
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.is_run, self.is_jump, self.is_duck = True, False, False
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, userInput, jump_input, duck_input):
        if self.is_run: self.run()
        if self.is_jump: self.jump()
        if self.is_duck: self.duck()

        if self.step_index >= 10: self.step_index = 0

        # Irányítás kombinálása (Billentyűzet + Egér/Érintés)
        if (userInput[pygame.K_UP] or jump_input) and not self.is_jump:
            self.is_run, self.is_jump, self.is_duck = False, True, False
            if jump_sound: jump_sound.play()
        elif (userInput[pygame.K_DOWN] or duck_input) and not self.is_jump:
            if not self.is_duck and duck_sound: 
                duck_sound.play()
