import pygame
import random
import asyncio
import os

# Inicializálás
pygame.init()
pygame.mixer.init()

# Ablak méretei
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vége van kicsi")

# --- SEGÉDFÜGGVÉNYEK A BIZTONSÁGOS BETÖLTÉSHEZ ---
def get_path(filename):
    paths = [
        filename,
        os.path.join("Assets/Viktor", filename),
        os.path.join("Assets/Sounds", filename),
        os.path.join("Assets/Avocado", filename),
        os.path.join("Assets/Heli", filename),
        os.path.join("Assets/Other", filename),
        os.path.join("assets", filename)
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return filename

def load_img(name, scale=None):
    try:
        img = pygame.image.load(get_path(name)).convert_alpha()
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    except:
        surf = pygame.Surface(scale if scale else (50, 50))
        surf.fill((255, 0, 0))
        return surf

def load_sd(name):
    try:
        return pygame.mixer.Sound(get_path(name))
    except:
        return None

# --- ASSETS BETÖLTÉSE ---
RUNNING = [load_img("ViktorRun1.png"), load_img("ViktorRun2.png")]
JUMPING = load_img("ViktorJump.png")
DUCKING = [load_img("ViktorDuck1.png"), load_img("ViktorDuck2.png")]
SMALL_AVOCADO = [load_img("SmallAvocado1.png"), load_img("SmallAvocado2.png"), load_img("SmallAvocado3.png")]
LARGE_AVOCADO = [load_img("LargeAvocado1.png"), load_img("LargeAvocado2.png")]
HELI = [load_img("Heli1.png"), load_img("Heli2.png")]
CLOUD = load_img("Cloud.png")
LANDING_PAGE = load_img("landingpage.png", (SCREEN_WIDTH, SCREEN_HEIGHT))

# Speciális Háttérkezelés (Panoráma mód)
try:
    orig_bg = pygame.image.load(get_path("background.png")).convert()
    bg_ratio = orig_bg.get_width() / orig_bg.get_height()
    BACKGROUND = pygame.transform.scale(orig_bg, (int(600 * bg_ratio), 600))
except:
    BACKGROUND = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    BACKGROUND.fill((200, 200, 200))

# Hangok
jump_sound = load_sd("jump.ogg")
duck_sound = load_sd("duck.ogg")
collision_sound = load_sd("collision.ogg")
coin_sound = load_sd("coin.ogg")
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

    def update(self, userInput):
        if self.is_run: self.run()
        if self.is_jump: self.jump()
        if self.is_duck: self.duck()

        if self.step_index >= 10: self.step_index = 0

        if userInput[pygame.K_UP] and not self.is_jump:
            self.is_run, self.is_jump, self.is_duck = False, True, False
            if jump_sound: jump_sound.play()
        elif userInput[pygame.K_DOWN] and not self.is_jump:
            self.is_run, self.is_jump, self.is_duck = False, False, True
            if duck_sound: duck_sound.play()
        elif not (self.is_jump or userInput[pygame.K_DOWN]):
            self.is_run, self.is_jump, self.is_duck = True, False, False

    def run(self):
        self.image = RUNNING[self.step_index // 5]
        self.rect = self.image.get_rect(topleft=(self.X_POS, self.Y_POS))
        self.step_index += 1
        self.mask = pygame.mask.from_surface(self.image)

    def duck(self):
        self.image = DUCKING[self.step_index // 5]
        self.rect = self.image.get_rect(topleft=(self.X_POS, self.Y_POS_DUCK))
        self.step_index += 1
        self.mask = pygame.mask.from_surface(self.image)

    def jump(self):
        self.image = JUMPING
        if self.is_jump:
            self.rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.rect.y >= self.Y_POS:
            self.rect.y = self.Y_POS
            self.is_jump = False
            self.jump_vel = self.JUMP_VEL
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Obstacle:
    def __init__(self, images):
        self.images = images
        self.type = random.randint(0, len(images) - 1)
        self.image = self.images[self.type]
        self.rect = self.image.get_rect(topleft=(SCREEN_WIDTH, 370))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, speed, obstacles):
        self.rect.x -= speed
        if self.rect.x < -self.rect.width:
            obstacles.pop(0)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# --- FŐ JÁTÉK CIKLUS ---
async def main_game(name):
    global game_speed, x_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Viktosaur()
    game_speed = 15
    x_pos_bg = 0
    points = 0
    obstacles = []
    font = pygame.font.Font(None, 30)

    try:
        pygame.mixer.music.load(get_path("background_music.ogg"))
        pygame.mixer.music.play(-1)
    except:
        pass

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return

        SCREEN.fill((255, 255, 255))
        
        # Panoráma háttér rajzolása
        SCREEN.blit(BACKGROUND, (x_pos_bg, 0))
        if x_pos_bg + BACKGROUND.get_width() < SCREEN_WIDTH:
            SCREEN.blit(BACKGROUND, (x_pos_bg + BACKGROUND.get_width(), 0))
        
        x_pos_bg -= game_speed * 0.5
        if x_pos_bg <= -BACKGROUND.get_width(): x_pos_bg = 0

        userInput = pygame.key.get_pressed()
        player.draw(SCREEN)
        player.update(userInput)

        if len(obstacles) == 0:
            choice = random.randint(0, 2)
            if choice == 0: obstacles.append(Obstacle(SMALL_AVOCADO))
            elif choice == 1: obstacles.append(Obstacle(LARGE_AVOCADO))
            elif choice == 2:
                h = Obstacle(HELI)
                h.rect.y = 280
                obstacles.append(h)

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update(game_speed, obstacles)
            if player.mask.overlap(obstacle.mask, (obstacle.rect.x - player.rect.x, obstacle.rect.y - player.rect.y)):
                if collision_sound: collision_sound.play()
                pygame.mixer.music.stop()
                if game_over_sound: game_over_sound.play()
                await asyncio.sleep(2)
                return

        points += 1
        if points % 100 == 0: game_speed += 1
        txt = font.render(f"Pilóta: {name} | Pont: {points}", True, (0, 0, 0))
        SCREEN.blit(txt, (40, 40))

        pygame.display.update()
        clock.tick(30)
        await asyncio.sleep(0)

# --- MENÜ ---
async def menu():
    player_name = ""
    font = pygame.font.Font(None, 50)
    
    while True:
        SCREEN.blit(LANDING_PAGE, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name:
                    await main_game(player_name)
                    player_name = ""
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 12:
                        player_name += event.unicode

        msg = font.render("Írd be a neved és nyomj ENTER-t!", True, (0, 0, 0))
        SCREEN.blit(msg, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 50))
        name_surf = font.render(player_name + "_", True, (255, 0, 0))
        SCREEN.blit(name_surf, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2 + 20))

        pygame.display.update()
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(menu())
